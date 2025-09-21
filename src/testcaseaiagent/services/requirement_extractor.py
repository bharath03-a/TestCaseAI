"""
Requirement extraction service using AI for healthcare domain.
"""

import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models import Requirement, TestCasePriority, ProcessingStatus
from ..core.config import settings

logger = logging.getLogger(__name__)


class RequirementExtractor:
    """Extracts requirements from parsed documents using AI."""
    
    def __init__(self):
        """Initialize the requirement extractor."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            google_api_key=settings.google_api_key
        )
    
    def extract_requirements(self, state) -> Any:
        """
        Extract requirements from parsed documents.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with extracted requirements
        """
        logger.info("Starting requirement extraction")
        
        try:
            requirements = []
            
            for i, content in enumerate(state.raw_text_content):
                logger.info(f"Processing document {i+1}/{len(state.raw_text_content)}")
                
                # Extract requirements from content
                doc_requirements = self._extract_requirements_from_text(content, i)
                requirements.extend(doc_requirements)
            
            state.extracted_requirements = requirements
            logger.info(f"Successfully extracted {len(requirements)} requirements")
            return state
            
        except Exception as e:
            logger.error(f"Requirement extraction failed: {str(e)}")
            state.error_log.append(f"Requirement extraction failed: {str(e)}")
            state.overall_status = ProcessingStatus.FAILED
            return state
    
    def _extract_requirements_from_text(self, text: str, doc_index: int) -> List[Requirement]:
        """Extract requirements from text content."""
        requirements = []
        
        # Simple extraction based on common requirement patterns
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for requirement patterns
            if self._is_requirement_line(line):
                req_id = f"REQ_{doc_index+1}_{i+1:03d}"
                
                requirement = Requirement(
                    id=req_id,
                    title=self._extract_requirement_title(line),
                    description=line,
                    priority=self._determine_priority(line),
                    source_document=f"document_{doc_index+1}",
                    source_section=f"line_{i+1}",
                    requirement_type="functional",
                    compliance_standards=self._identify_compliance_standards(line)
                )
                requirements.append(requirement)
        
        return requirements
    
    def _is_requirement_line(self, line: str) -> bool:
        """Check if a line contains a requirement."""
        requirement_indicators = [
            "shall", "must", "should", "will", "the system", "the software",
            "the application", "the platform", "the service"
        ]
        
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in requirement_indicators)
    
    def _extract_requirement_title(self, line: str) -> str:
        """Extract a title from a requirement line."""
        # Simple title extraction - first 50 characters
        title = line[:50].strip()
        if len(line) > 50:
            title += "..."
        return title
    
    def _determine_priority(self, line: str) -> TestCasePriority:
        """Determine requirement priority."""
        line_lower = line.lower()
        
        if any(keyword in line_lower for keyword in ["critical", "essential", "mandatory"]):
            return TestCasePriority.CRITICAL
        elif any(keyword in line_lower for keyword in ["important", "high", "priority"]):
            return TestCasePriority.HIGH
        elif any(keyword in line_lower for keyword in ["low", "optional", "nice to have"]):
            return TestCasePriority.LOW
        else:
            return TestCasePriority.MEDIUM
    
    def _identify_compliance_standards(self, line: str) -> List[str]:
        """Identify relevant compliance standards from requirement text."""
        standards = []
        line_lower = line.lower()
        
        # Simple keyword-based identification
        if any(keyword in line_lower for keyword in ["hipaa", "privacy", "patient data"]):
            standards.append("hipaa")
        if any(keyword in line_lower for keyword in ["fda", "medical device", "regulation"]):
            standards.append("fda")
        if any(keyword in line_lower for keyword in ["security", "access control"]):
            standards.append("iso_27001")
        if any(keyword in line_lower for keyword in ["software", "development"]):
            standards.append("iec_62304")
        if any(keyword in line_lower for keyword in ["gdpr", "data protection"]):
            standards.append("gdpr")
        
        return standards
