"""
Session memory management for multi-step conversations and context persistence.
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import logging
import pickle
import os
from pathlib import Path

from models import (
    SessionMemory, GraphState, ProcessingStatus, WorkflowStep,
    Requirement, TestCase, ComplianceMapping
)
from config import settings

logger = logging.getLogger(__name__)


class SessionMemoryManager:
    """Manages session memory for multi-step conversations and context persistence."""
    
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}
        self.memory_file_path = Path(settings.temp_directory) / "session_memory.pkl"
        self._ensure_memory_directory()
        self._load_sessions_from_disk()
    
    def _ensure_memory_directory(self):
        """Ensure the memory directory exists."""
        self.memory_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_sessions_from_disk(self):
        """Load sessions from disk if persistence is enabled."""
        if not settings.enable_session_persistence:
            return
        
        try:
            if self.memory_file_path.exists():
                with open(self.memory_file_path, 'rb') as f:
                    self.sessions = pickle.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from disk")
        except Exception as e:
            logger.warning(f"Failed to load sessions from disk: {str(e)}")
            self.sessions = {}
    
    def _save_sessions_to_disk(self):
        """Save sessions to disk if persistence is enabled."""
        if not settings.enable_session_persistence:
            return
        
        try:
            with open(self.memory_file_path, 'wb') as f:
                pickle.dump(self.sessions, f)
        except Exception as e:
            logger.warning(f"Failed to save sessions to disk: {str(e)}")
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        
        session = SessionMemory(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        self.sessions[session_id] = session
        self._save_sessions_to_disk()
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if session:
            session.last_accessed = datetime.now()
            self._save_sessions_to_disk()
        return session
    
    def update_session_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Update session context."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.current_context.update(context)
        session.last_accessed = datetime.now()
        self._save_sessions_to_disk()
        return True
    
    def add_conversation_entry(self, session_id: str, entry: Dict[str, Any]) -> bool:
        """Add entry to conversation history."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        entry["timestamp"] = datetime.now().isoformat()
        session.conversation_history.append(entry)
        
        # Limit conversation history size
        if len(session.conversation_history) > settings.max_session_memory_size:
            session.conversation_history = session.conversation_history[-settings.max_session_memory_size:]
        
        session.last_accessed = datetime.now()
        self._save_sessions_to_disk()
        return True
    
    def update_session_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """Update session preferences."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.preferences.update(preferences)
        session.last_accessed = datetime.now()
        self._save_sessions_to_disk()
        return True
    
    def store_workflow_state(self, session_id: str, state: GraphState) -> bool:
        """Store workflow state in session memory."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Convert state to serializable format
        state_data = self._serialize_state(state)
        
        # Store in current context
        session.current_context["workflow_state"] = state_data
        session.current_context["last_workflow_update"] = datetime.now().isoformat()
        
        # Add to conversation history
        self.add_conversation_entry(session_id, {
            "type": "workflow_state_update",
            "status": state.overall_status.value,
            "step": state.current_step,
            "progress": state.progress_percentage,
            "requirements_count": len(state.extracted_requirements),
            "test_cases_count": len(state.generated_test_cases)
        })
        
        session.last_accessed = datetime.now()
        self._save_sessions_to_disk()
        return True
    
    def get_workflow_state(self, session_id: str) -> Optional[GraphState]:
        """Retrieve workflow state from session memory."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        state_data = session.current_context.get("workflow_state")
        if not state_data:
            return None
        
        try:
            return self._deserialize_state(state_data)
        except Exception as e:
            logger.error(f"Failed to deserialize workflow state: {str(e)}")
            return None
    
    def _serialize_state(self, state: GraphState) -> Dict[str, Any]:
        """Serialize GraphState to dictionary."""
        return {
            "input_documents": state.input_documents,
            "document_metadata": [self._serialize_metadata(md) for md in state.document_metadata],
            "raw_text_content": state.raw_text_content,
            "extracted_requirements": [self._serialize_requirement(req) for req in state.extracted_requirements],
            "compliance_mappings": [self._serialize_compliance_mapping(cm) for cm in state.compliance_mappings],
            "generated_test_cases": [self._serialize_test_case(tc) for tc in state.generated_test_cases],
            "quality_metrics": self._serialize_quality_metrics(state.quality_metrics) if state.quality_metrics else None,
            "workflow_steps": [self._serialize_workflow_step(ws) for ws in state.workflow_steps],
            "current_step": state.current_step,
            "error_log": state.error_log,
            "processing_config": state.processing_config,
            "compliance_standards": [std.value for std in state.compliance_standards],
            "output_preferences": state.output_preferences,
            "overall_status": state.overall_status.value,
            "progress_percentage": state.progress_percentage,
            "estimated_completion": state.estimated_completion.isoformat() if state.estimated_completion else None,
            "final_report": state.final_report,
            "user_feedback": state.user_feedback,
            "improvement_suggestions": state.improvement_suggestions
        }
    
    def _deserialize_state(self, state_data: Dict[str, Any]) -> GraphState:
        """Deserialize dictionary to GraphState."""
        from models import DocumentMetadata, Requirement, ComplianceMapping, TestCase, QualityMetrics, WorkflowStep, ComplianceStandard, ProcessingStatus
        
        # Deserialize document metadata
        document_metadata = []
        for md_data in state_data.get("document_metadata", []):
            document_metadata.append(self._deserialize_metadata(md_data))
        
        # Deserialize requirements
        extracted_requirements = []
        for req_data in state_data.get("extracted_requirements", []):
            extracted_requirements.append(self._deserialize_requirement(req_data))
        
        # Deserialize compliance mappings
        compliance_mappings = []
        for cm_data in state_data.get("compliance_mappings", []):
            compliance_mappings.append(self._deserialize_compliance_mapping(cm_data))
        
        # Deserialize test cases
        generated_test_cases = []
        for tc_data in state_data.get("generated_test_cases", []):
            generated_test_cases.append(self._deserialize_test_case(tc_data))
        
        # Deserialize quality metrics
        quality_metrics = None
        if state_data.get("quality_metrics"):
            quality_metrics = self._deserialize_quality_metrics(state_data["quality_metrics"])
        
        # Deserialize workflow steps
        workflow_steps = []
        for ws_data in state_data.get("workflow_steps", []):
            workflow_steps.append(self._deserialize_workflow_step(ws_data))
        
        # Deserialize compliance standards
        compliance_standards = []
        for std_str in state_data.get("compliance_standards", []):
            try:
                compliance_standards.append(ComplianceStandard(std_str))
            except ValueError:
                logger.warning(f"Unknown compliance standard: {std_str}")
        
        # Deserialize estimated completion
        estimated_completion = None
        if state_data.get("estimated_completion"):
            estimated_completion = datetime.fromisoformat(state_data["estimated_completion"])
        
        return GraphState(
            input_documents=state_data.get("input_documents", []),
            document_metadata=document_metadata,
            raw_text_content=state_data.get("raw_text_content", []),
            extracted_requirements=extracted_requirements,
            compliance_mappings=compliance_mappings,
            generated_test_cases=generated_test_cases,
            quality_metrics=quality_metrics,
            workflow_steps=workflow_steps,
            current_step=state_data.get("current_step"),
            error_log=state_data.get("error_log", []),
            processing_config=state_data.get("processing_config", {}),
            compliance_standards=compliance_standards,
            output_preferences=state_data.get("output_preferences", {}),
            overall_status=ProcessingStatus(state_data.get("overall_status", "pending")),
            progress_percentage=state_data.get("progress_percentage", 0.0),
            estimated_completion=estimated_completion,
            final_report=state_data.get("final_report"),
            user_feedback=state_data.get("user_feedback"),
            improvement_suggestions=state_data.get("improvement_suggestions", [])
        )
    
    def _serialize_metadata(self, metadata) -> Dict[str, Any]:
        """Serialize DocumentMetadata."""
        return {
            "filename": metadata.filename,
            "document_type": metadata.document_type.value,
            "file_size": metadata.file_size,
            "upload_timestamp": metadata.upload_timestamp.isoformat(),
            "checksum": metadata.checksum,
            "language": metadata.language,
            "encoding": metadata.encoding
        }
    
    def _deserialize_metadata(self, data: Dict[str, Any]):
        """Deserialize DocumentMetadata."""
        from models import DocumentMetadata, DocumentType
        return DocumentMetadata(
            filename=data["filename"],
            document_type=DocumentType(data["document_type"]),
            file_size=data["file_size"],
            upload_timestamp=datetime.fromisoformat(data["upload_timestamp"]),
            checksum=data["checksum"],
            language=data.get("language", "en"),
            encoding=data.get("encoding", "utf-8")
        )
    
    def _serialize_requirement(self, req: Requirement) -> Dict[str, Any]:
        """Serialize Requirement."""
        return {
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "type": req.type.value,
            "priority": req.priority.value,
            "source_document": req.source_document,
            "source_section": req.source_section,
            "source_line_number": req.source_line_number,
            "stakeholders": req.stakeholders,
            "acceptance_criteria": req.acceptance_criteria,
            "dependencies": req.dependencies,
            "compliance_standards": [std.value for std in req.compliance_standards],
            "risk_level": req.risk_level,
            "complexity": req.complexity,
            "estimated_effort": req.estimated_effort,
            "tags": req.tags,
            "created_at": req.created_at.isoformat(),
            "updated_at": req.updated_at.isoformat()
        }
    
    def _deserialize_requirement(self, data: Dict[str, Any]) -> Requirement:
        """Deserialize Requirement."""
        from models import Requirement, RequirementType, TestCasePriority, ComplianceStandard
        return Requirement(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=RequirementType(data["type"]),
            priority=TestCasePriority(data["priority"]),
            source_document=data["source_document"],
            source_section=data.get("source_section"),
            source_line_number=data.get("source_line_number"),
            stakeholders=data.get("stakeholders", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            dependencies=data.get("dependencies", []),
            compliance_standards=[ComplianceStandard(std) for std in data.get("compliance_standards", [])],
            risk_level=data.get("risk_level", "medium"),
            complexity=data.get("complexity", "moderate"),
            estimated_effort=data.get("estimated_effort"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def _serialize_compliance_mapping(self, cm: ComplianceMapping) -> Dict[str, Any]:
        """Serialize ComplianceMapping."""
        return {
            "requirement_id": cm.requirement_id,
            "standard": cm.standard.value,
            "applicable_sections": cm.applicable_sections,
            "compliance_level": cm.compliance_level,
            "evidence": cm.evidence,
            "gaps": cm.gaps,
            "recommendations": cm.recommendations
        }
    
    def _deserialize_compliance_mapping(self, data: Dict[str, Any]) -> ComplianceMapping:
        """Deserialize ComplianceMapping."""
        from models import ComplianceMapping, ComplianceStandard
        return ComplianceMapping(
            requirement_id=data["requirement_id"],
            standard=ComplianceStandard(data["standard"]),
            applicable_sections=data.get("applicable_sections", []),
            compliance_level=data.get("compliance_level", "non_compliant"),
            evidence=data.get("evidence", []),
            gaps=data.get("gaps", []),
            recommendations=data.get("recommendations", [])
        )
    
    def _serialize_test_case(self, tc: TestCase) -> Dict[str, Any]:
        """Serialize TestCase."""
        return {
            "id": tc.id,
            "title": tc.title,
            "description": tc.description,
            "type": tc.type.value,
            "priority": tc.priority.value,
            "requirement_ids": tc.requirement_ids,
            "preconditions": tc.preconditions,
            "test_steps": tc.test_steps,
            "expected_results": tc.expected_results,
            "test_data": tc.test_data,
            "automation_status": tc.automation_status,
            "estimated_duration": tc.estimated_duration,
            "risk_level": tc.risk_level,
            "compliance_standards": [std.value for std in tc.compliance_standards],
            "traceability_matrix": tc.traceability_matrix,
            "created_at": tc.created_at.isoformat(),
            "updated_at": tc.updated_at.isoformat()
        }
    
    def _deserialize_test_case(self, data: Dict[str, Any]) -> TestCase:
        """Deserialize TestCase."""
        from models import TestCase, TestCaseType, TestCasePriority, ComplianceStandard
        return TestCase(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=TestCaseType(data["type"]),
            priority=TestCasePriority(data["priority"]),
            requirement_ids=data.get("requirement_ids", []),
            preconditions=data.get("preconditions", []),
            test_steps=data.get("test_steps", []),
            expected_results=data.get("expected_results", []),
            test_data=data.get("test_data", {}),
            automation_status=data.get("automation_status", "manual"),
            estimated_duration=data.get("estimated_duration"),
            risk_level=data.get("risk_level", "medium"),
            compliance_standards=[ComplianceStandard(std) for std in data.get("compliance_standards", [])],
            traceability_matrix=data.get("traceability_matrix", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def _serialize_quality_metrics(self, qm) -> Dict[str, Any]:
        """Serialize QualityMetrics."""
        return {
            "completeness_score": qm.completeness_score,
            "accuracy_score": qm.accuracy_score,
            "traceability_score": qm.traceability_score,
            "compliance_score": qm.compliance_score,
            "coverage_percentage": qm.coverage_percentage,
            "total_issues": qm.total_issues,
            "critical_issues": qm.critical_issues,
            "recommendations": qm.recommendations
        }
    
    def _deserialize_quality_metrics(self, data: Dict[str, Any]):
        """Deserialize QualityMetrics."""
        from models import QualityMetrics
        return QualityMetrics(
            completeness_score=data.get("completeness_score", 0.0),
            accuracy_score=data.get("accuracy_score", 0.0),
            traceability_score=data.get("traceability_score", 0.0),
            compliance_score=data.get("compliance_score", 0.0),
            coverage_percentage=data.get("coverage_percentage", 0.0),
            total_issues=data.get("total_issues", 0),
            critical_issues=data.get("critical_issues", 0),
            recommendations=data.get("recommendations", [])
        )
    
    def _serialize_workflow_step(self, ws: WorkflowStep) -> Dict[str, Any]:
        """Serialize WorkflowStep."""
        return {
            "step_name": ws.step_name,
            "status": ws.status.value,
            "start_time": ws.start_time.isoformat() if ws.start_time else None,
            "end_time": ws.end_time.isoformat() if ws.end_time else None,
            "duration_seconds": ws.duration_seconds,
            "input_data": ws.input_data,
            "output_data": ws.output_data,
            "error_message": ws.error_message,
            "retry_count": ws.retry_count,
            "metadata": ws.metadata
        }
    
    def _deserialize_workflow_step(self, data: Dict[str, Any]) -> WorkflowStep:
        """Deserialize WorkflowStep."""
        from models import WorkflowStep, ProcessingStatus
        return WorkflowStep(
            step_name=data["step_name"],
            status=ProcessingStatus(data["status"]),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            duration_seconds=data.get("duration_seconds"),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            metadata=data.get("metadata", {})
        )
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_accessed > timedelta(minutes=settings.session_timeout_minutes):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        if expired_sessions:
            self._save_sessions_to_disk()
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary information."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "conversation_entries": len(session.conversation_history),
            "has_workflow_state": "workflow_state" in session.current_context,
            "preferences": session.preferences
        }
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions_to_disk()
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get summary of all sessions."""
        return [self.get_session_summary(session_id) for session_id in self.sessions.keys()]


# Export the main memory manager class
__all__ = ["SessionMemoryManager"]
