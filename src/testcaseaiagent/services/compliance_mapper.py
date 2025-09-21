"""
Compliance mapping service for healthcare requirements.
"""

import json
import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models import ComplianceStandard, Requirement, ComplianceMapping
from ..core.config import settings

logger = logging.getLogger(__name__)


class ComplianceMapper:
    """Maps healthcare requirements to compliance standards."""
    
    def __init__(self):
        """Initialize the compliance mapper."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            google_api_key=settings.google_api_key
        )
        
        # Simplified compliance standards mapping
        self.compliance_standards = {
            "fda": "FDA (Food and Drug Administration) - Medical Device Regulations",
            "iec_62304": "IEC 62304 - Medical device software lifecycle processes",
            "iso_9001": "ISO 9001 - Quality management systems",
            "iso_13485": "ISO 13485 - Medical devices quality management systems",
            "iso_27001": "ISO 27001 - Information security management",
            "hipaa": "HIPAA - Health Insurance Portability and Accountability Act",
            "gdpr": "GDPR - General Data Protection Regulation"
        }
    
    def map_requirements_to_compliance(
        self, 
        requirements: List[Requirement], 
        compliance_standards: List[ComplianceStandard]
    ) -> List[ComplianceMapping]:
        """
        Map requirements to relevant compliance standards.
        
        Args:
            requirements: List of requirements to map
            compliance_standards: List of compliance standards to consider
            
        Returns:
            List of compliance mappings
        """
        logger.info("Starting compliance mapping")
        mappings = []
        
        try:
            for requirement in requirements:
                # Use simplified mapping logic
                requirement_mappings = self._map_single_requirement(requirement, compliance_standards)
                mappings.extend(requirement_mappings)
            
            logger.info(f"Successfully mapped {len(mappings)} requirements to compliance standards")
            return mappings
            
        except Exception as e:
            logger.error(f"Compliance mapping failed: {str(e)}")
            # Return fallback mappings
            return self._create_fallback_mappings(requirements, compliance_standards)
    
    def _map_single_requirement(
        self, 
        requirement: Requirement, 
        compliance_standards: List[ComplianceStandard]
    ) -> List[ComplianceMapping]:
        """Map a single requirement to compliance standards."""
        mappings = []
        
        # Simple keyword-based mapping
        requirement_text = f"{requirement.title} {requirement.description}".lower()
        
        for standard in compliance_standards:
            confidence = self._calculate_mapping_confidence(requirement_text, standard)
            
            if confidence >= settings.compliance_mapping_confidence_threshold:
                mapping = ComplianceMapping(
                    requirement_id=requirement.id,
                    compliance_standard=standard,
                    mapping_confidence=confidence,
                    relevant_sections=self._get_relevant_sections(standard),
                    compliance_notes=f"Mapped based on keyword analysis with {confidence:.2f} confidence"
                )
                mappings.append(mapping)
        
        return mappings
    
    def _calculate_mapping_confidence(self, requirement_text: str, standard: ComplianceStandard) -> float:
        """Calculate confidence score for requirement-to-standard mapping."""
        # Define keywords for each standard
        keywords = {
            ComplianceStandard.FDA: ["medical device", "fda", "regulation", "safety", "effectiveness"],
            ComplianceStandard.HIPAA: ["patient", "health", "privacy", "security", "data", "phi"],
            ComplianceStandard.IEC_62304: ["software", "medical device", "lifecycle", "development"],
            ComplianceStandard.ISO_27001: ["security", "information", "risk", "management"],
            ComplianceStandard.ISO_13485: ["quality", "management", "medical device"],
            ComplianceStandard.ISO_9001: ["quality", "management", "process"],
            ComplianceStandard.GDPR: ["data", "privacy", "personal", "protection", "consent"]
        }
        
        standard_keywords = keywords.get(standard, [])
        matches = sum(1 for keyword in standard_keywords if keyword in requirement_text)
        
        if not standard_keywords:
            return 0.0
        
        confidence = matches / len(standard_keywords)
        return min(confidence, 1.0)
    
    def _get_relevant_sections(self, standard: ComplianceStandard) -> List[str]:
        """Get relevant sections for a compliance standard."""
        sections = {
            ComplianceStandard.FDA: ["21 CFR Part 820", "21 CFR Part 11"],
            ComplianceStandard.HIPAA: ["164.312 - Technical Safeguards", "164.314 - Organizational Requirements"],
            ComplianceStandard.IEC_62304: ["5.1 - Software Development Process", "5.2 - Software Maintenance Process"],
            ComplianceStandard.ISO_27001: ["A.9 - Access Control", "A.12 - Operations Security"],
            ComplianceStandard.ISO_13485: ["4.1 - Quality Management System", "7.3 - Design and Development"],
            ComplianceStandard.ISO_9001: ["4.4 - Process Management", "8.3 - Design and Development"],
            ComplianceStandard.GDPR: ["Article 32 - Security of Processing", "Article 25 - Data Protection by Design"]
        }
        
        return sections.get(standard, [])
    
    def _create_fallback_mappings(
        self, 
        requirements: List[Requirement], 
        compliance_standards: List[ComplianceStandard]
    ) -> List[ComplianceMapping]:
        """Create fallback mappings when AI mapping fails."""
        logger.info("Using fallback compliance mapping method")
        mappings = []
        
        for requirement in requirements:
            for standard in compliance_standards:
                mapping = ComplianceMapping(
                    requirement_id=requirement.id,
                    compliance_standard=standard,
                    mapping_confidence=0.5,  # Default confidence
                    relevant_sections=self._get_relevant_sections(standard),
                    compliance_notes="Fallback mapping - manual review recommended"
                )
                mappings.append(mapping)
        
        return mappings
