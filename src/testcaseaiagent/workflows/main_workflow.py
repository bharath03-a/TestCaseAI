"""
Main LangGraph workflow for healthcare test case generation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models import (
    GraphState, 
    ComplianceStandard, 
    ProcessingStatus, 
    WorkflowStep
)
from ..services import (
    DocumentParser,
    RequirementExtractor,
    ComplianceMapper,
    TestGenerator,
    QualityValidator,
    SessionMemoryManager
)
from ..core.config import settings

logger = logging.getLogger(__name__)


class HealthcareTestCaseGenerator:
    """Main healthcare test case generation system using LangGraph."""
    
    def __init__(self):
        """Initialize the healthcare test case generator."""
        self.document_parser = DocumentParser()
        self.requirement_extractor = RequirementExtractor()
        self.compliance_mapper = ComplianceMapper()
        self.test_generator = TestGenerator()
        self.quality_validator = QualityValidator()
        self.session_memory = SessionMemoryManager()
        
        # Build the workflow
        self.workflow = self._build_workflow()
        
        logger.info("Healthcare Test Case Generator initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Builds the LangGraph workflow."""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("document_parser", self._document_parser_node)
        workflow.add_node("requirement_extractor", self._requirement_extractor_node)
        workflow.add_node("compliance_mapper", self._compliance_mapper_node)
        workflow.add_node("test_generator", self._test_generator_node)
        workflow.add_node("quality_validator", self._quality_validator_node)
        workflow.add_node("error_handler", self._error_handler_node)
        workflow.add_node("finalizer", self._finalizer_node)
        
        # Set entry point
        workflow.set_entry_point("document_parser")
        
        # Add edges with conditional routing
        workflow.add_edge("document_parser", "requirement_extractor")
        workflow.add_conditional_edges(
            "requirement_extractor",
            self._should_continue_after_requirements,
            {
                "continue": "compliance_mapper",
                "error": "error_handler"
            }
        )
        workflow.add_conditional_edges(
            "compliance_mapper",
            self._should_continue_after_compliance,
            {
                "continue": "test_generator",
                "error": "error_handler"
            }
        )
        workflow.add_conditional_edges(
            "test_generator",
            self._should_continue_after_tests,
            {
                "continue": "quality_validator",
                "error": "error_handler"
            }
        )
        workflow.add_edge("quality_validator", "finalizer")
        workflow.add_edge("error_handler", END)
        workflow.add_edge("finalizer", END)
        
        # Compile the workflow
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory, interrupt_before=[], interrupt_after=[])
    
    def _document_parser_node(self, state: GraphState) -> GraphState:
        """Document parsing node."""
        logger.info("Executing document parser node")
        return self.document_parser.parse_documents(state)
    
    def _requirement_extractor_node(self, state: GraphState) -> GraphState:
        """Requirement extraction node."""
        logger.info("Executing requirement extractor node")
        return self.requirement_extractor.extract_requirements(state)
    
    def _compliance_mapper_node(self, state: GraphState) -> GraphState:
        """Compliance mapping node."""
        logger.info("Executing compliance mapper node")
        try:
            mappings = self.compliance_mapper.map_requirements_to_compliance(
                state.extracted_requirements,
                state.compliance_standards
            )
            state.compliance_mappings = mappings
            return state
        except Exception as e:
            logger.error(f"Compliance mapping failed: {str(e)}")
            state.error_log.append(f"Compliance mapping failed: {str(e)}")
            state.overall_status = ProcessingStatus.FAILED
            return state
    
    def _test_generator_node(self, state: GraphState) -> GraphState:
        """Test case generation node."""
        logger.info("Executing test generator node")
        try:
            test_cases = self.test_generator.generate_test_cases(
                state.extracted_requirements,
                state.compliance_mappings
            )
            state.generated_test_cases = test_cases
            return state
        except Exception as e:
            logger.error(f"Test generation failed: {str(e)}")
            state.error_log.append(f"Test generation failed: {str(e)}")
            state.overall_status = ProcessingStatus.FAILED
            return state
    
    def _quality_validator_node(self, state: GraphState) -> GraphState:
        """Quality validation node."""
        logger.info("Executing quality validator node")
        return self.quality_validator.validate_quality(state)
    
    def _error_handler_node(self, state: GraphState) -> GraphState:
        """Error handling node."""
        logger.error("Executing error handler node")
        state.overall_status = ProcessingStatus.FAILED
        state.final_report = {
            "status": "failed",
            "error_summary": state.error_log,
            "completed_steps": [step.step_name for step in state.workflow_steps if step.status == ProcessingStatus.COMPLETED]
        }
        return state
    
    def _finalizer_node(self, state: GraphState) -> GraphState:
        """Finalization node."""
        logger.info("Executing finalizer node")
        state.overall_status = ProcessingStatus.COMPLETED
        state.progress_percentage = 100.0
        state.estimated_completion = datetime.now()
        
        # Generate final report
        state.final_report = self._generate_final_report(state)
        
        return state
    
    def _should_continue_after_requirements(self, state: GraphState) -> str:
        """Determine if workflow should continue after requirement extraction."""
        if state.overall_status == ProcessingStatus.FAILED:
            return "error"
        if not state.extracted_requirements:
            state.error_log.append("No requirements extracted from documents")
            return "error"
        return "continue"
    
    def _should_continue_after_compliance(self, state: GraphState) -> str:
        """Determine if workflow should continue after compliance mapping."""
        if state.overall_status == ProcessingStatus.FAILED:
            return "error"
        if not state.compliance_mappings:
            logger.warning("No compliance mappings generated, continuing with test generation")
        return "continue"
    
    def _should_continue_after_tests(self, state: GraphState) -> str:
        """Determine if workflow should continue after test generation."""
        if state.overall_status == ProcessingStatus.FAILED:
            return "error"
        if not state.generated_test_cases:
            state.error_log.append("No test cases generated")
            return "error"
        return "continue"
    
    def _generate_final_report(self, state: GraphState) -> Dict[str, Any]:
        """Generate final processing report."""
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "processing_summary": {
                "documents_processed": len(state.document_metadata),
                "requirements_extracted": len(state.extracted_requirements),
                "compliance_mappings": len(state.compliance_mappings),
                "test_cases_generated": len(state.generated_test_cases),
                "quality_metrics": {
                    "completeness_score": state.quality_metrics.completeness_score if state.quality_metrics else 0.0,
                    "accuracy_score": state.quality_metrics.accuracy_score if state.quality_metrics else 0.0,
                    "traceability_score": state.quality_metrics.traceability_score if state.quality_metrics else 0.0,
                    "compliance_score": state.quality_metrics.compliance_score if state.quality_metrics else 0.0,
                    "coverage_percentage": state.quality_metrics.coverage_percentage if state.quality_metrics else 0.0
                } if state.quality_metrics else None
            },
            "workflow_steps": [
                {
                    "step_name": step.step_name,
                    "status": step.status.value,
                    "duration_seconds": step.duration_seconds,
                    "input_count": step.input_count,
                    "output_count": step.output_count
                }
                for step in state.workflow_steps
            ],
            "error_log": state.error_log,
            "improvement_suggestions": state.improvement_suggestions
        }
    
    def process_documents(
        self, 
        documents: List[Dict[str, Any]], 
        session_id: Optional[str] = None,
        compliance_standards: Optional[List[ComplianceStandard]] = None
    ) -> Dict[str, Any]:
        """
        Process documents and generate test cases.
        
        Args:
            documents: List of document data
            session_id: Optional session ID for memory management
            compliance_standards: Optional list of compliance standards to focus on
            
        Returns:
            Processing results
        """
        try:
            # Create or get session
            if not session_id:
                session_id = self.session_memory.create_session()
            
            # Initialize state
            initial_state = GraphState(
                input_documents=documents,
                compliance_standards=compliance_standards or settings.default_compliance_standards,
                processing_config={
                    "session_id": session_id,
                    "start_time": datetime.now().isoformat(),
                    "compliance_standards": [std.value for std in (compliance_standards or settings.default_compliance_standards)]
                }
            )
            
            # Store initial state in session memory
            self.session_memory.store_workflow_state(session_id, initial_state)
            
            # Execute workflow
            logger.info(f"Starting workflow execution for session {session_id}")
            config = {"configurable": {"thread_id": session_id}}
            final_state = self.workflow.invoke(initial_state, config=config)
            
            # Ensure final_state is a GraphState object
            if isinstance(final_state, dict):
                # Convert dict back to GraphState if needed
                final_state = GraphState(**final_state)
            
            # Store final state in session memory
            self.session_memory.store_workflow_state(session_id, final_state)
            
            # Return results
            return {
                "success": final_state.overall_status == ProcessingStatus.COMPLETED,
                "session_id": session_id,
                "requirements": [req.model_dump() for req in final_state.extracted_requirements],
                "test_cases": [tc.model_dump() for tc in final_state.generated_test_cases],
                "quality_metrics": final_state.quality_metrics.model_dump() if final_state.quality_metrics else None,
                "final_report": final_state.final_report,
                "error_log": final_state.error_log,
                "error": final_state.error_log[-1] if final_state.error_log else None
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "error_log": [str(e)]
            }
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a processing session."""
        return self.session_memory.get_session_summary(session_id)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        self.session_memory.cleanup_expired_sessions()
