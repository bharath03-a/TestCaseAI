"""
Compliance mapping module for healthcare standards (FDA, IEC 62304, ISO, etc.).
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from models import (
    Requirement, ComplianceMapping, ComplianceStandard, GraphState, 
    ProcessingStatus, WorkflowStep
)
from config import settings, HealthcareDomainConfig

logger = logging.getLogger(__name__)


class ComplianceMapper:
    """Map requirements to healthcare compliance standards."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            top_p=settings.gemini_top_p,
            top_k=settings.gemini_top_k,
            google_api_key=settings.google_api_key
        )
        
        # Initialize compliance knowledge base
        self._setup_compliance_knowledge()
        self._setup_prompts()
    
    def _setup_compliance_knowledge(self):
        """Setup compliance standards knowledge base."""
        self.compliance_standards = {
            ComplianceStandard.FDA: {
                "name": "FDA 21 CFR Part 820",
                "description": "Quality System Regulation for Medical Devices",
                "key_sections": [
                    "820.30 - Design Controls",
                    "820.50 - Purchasing Controls", 
                    "820.70 - Production and Process Controls",
                    "820.80 - Acceptance Activities",
                    "820.90 - Nonconforming Product",
                    "820.100 - Corrective and Preventive Action",
                    "820.120 - Device Labeling",
                    "820.130 - Device Packaging",
                    "820.140 - Handling, Storage, Distribution, and Installation",
                    "820.150 - Servicing",
                    "820.160 - Installation",
                    "820.170 - Servicing",
                    "820.180 - General Requirements",
                    "820.184 - Device History Record",
                    "820.186 - Quality System Record",
                    "820.198 - Complaint Files"
                ],
                "requirements": [
                    "Design validation must ensure devices conform to defined user needs",
                    "Risk management must be implemented throughout device lifecycle",
                    "Software must be validated for its intended use",
                    "Change control procedures must be established",
                    "Documentation must be maintained and controlled"
                ]
            },
            ComplianceStandard.IEC_62304: {
                "name": "IEC 62304 - Medical Device Software Lifecycle",
                "description": "International standard for medical device software lifecycle processes",
                "key_sections": [
                    "5.1 - Software Development Process",
                    "5.2 - Software Maintenance Process",
                    "5.3 - Software Risk Management Process",
                    "5.4 - Software Configuration Management Process",
                    "5.5 - Software Problem Resolution Process",
                    "5.6 - Software Safety Classification",
                    "5.7 - Software Development Planning",
                    "5.8 - Software Requirements Analysis",
                    "5.9 - Software Architectural Design",
                    "5.10 - Software Detailed Design",
                    "5.11 - Software Implementation",
                    "5.12 - Software Integration",
                    "5.13 - Software System Testing",
                    "5.14 - Software Release"
                ],
                "requirements": [
                    "Software must be classified according to risk (Class A, B, or C)",
                    "Software development lifecycle must be established",
                    "Risk management must be integrated with software development",
                    "Software must be validated and verified",
                    "Configuration management must be implemented"
                ]
            },
            ComplianceStandard.ISO_13485: {
                "name": "ISO 13485 - Medical Device Quality Management",
                "description": "Quality management system requirements for medical devices",
                "key_sections": [
                    "4.1 - General Requirements",
                    "4.2 - Documentation Requirements",
                    "5.1 - Management Responsibility",
                    "6.1 - Resource Management",
                    "7.1 - Product Realization",
                    "7.2 - Customer-Related Processes",
                    "7.3 - Design and Development",
                    "7.4 - Purchasing",
                    "7.5 - Production and Service Provision",
                    "7.6 - Control of Monitoring and Measuring Equipment",
                    "8.1 - Measurement, Analysis and Improvement",
                    "8.2 - Monitoring and Measurement",
                    "8.3 - Control of Nonconforming Product",
                    "8.4 - Analysis of Data",
                    "8.5 - Improvement"
                ],
                "requirements": [
                    "Quality management system must be established and maintained",
                    "Management responsibility must be defined",
                    "Resource management must be implemented",
                    "Product realization processes must be controlled",
                    "Measurement and monitoring must be performed"
                ]
            },
            ComplianceStandard.ISO_27001: {
                "name": "ISO 27001 - Information Security Management",
                "description": "Information security management system requirements",
                "key_sections": [
                    "4.1 - Understanding the Organization",
                    "4.2 - Understanding Stakeholder Needs",
                    "4.3 - Determining ISMS Scope",
                    "4.4 - Information Security Management System",
                    "5.1 - Leadership and Commitment",
                    "5.2 - Policy",
                    "5.3 - Organizational Roles and Responsibilities",
                    "6.1 - Actions to Address Risks and Opportunities",
                    "6.2 - Information Security Objectives",
                    "7.1 - Resources",
                    "7.2 - Competence",
                    "7.3 - Awareness",
                    "7.4 - Communication",
                    "7.5 - Documented Information",
                    "8.1 - Operational Planning and Control",
                    "8.2 - Information Security Risk Assessment",
                    "8.3 - Information Security Risk Treatment",
                    "9.1 - Monitoring, Measurement, Analysis and Evaluation",
                    "9.2 - Internal Audit",
                    "9.3 - Management Review",
                    "10.1 - Nonconformity and Corrective Action",
                    "10.2 - Continual Improvement"
                ],
                "requirements": [
                    "Information security management system must be established",
                    "Risk assessment and treatment must be performed",
                    "Security controls must be implemented",
                    "Monitoring and measurement must be performed",
                    "Continual improvement must be ensured"
                ]
            },
            ComplianceStandard.HIPAA: {
                "name": "HIPAA - Health Insurance Portability and Accountability Act",
                "description": "US federal law for protecting health information",
                "key_sections": [
                    "Administrative Safeguards",
                    "Physical Safeguards", 
                    "Technical Safeguards",
                    "Organizational Requirements",
                    "Policies and Procedures",
                    "Workforce Training",
                    "Access Management",
                    "Audit Controls",
                    "Integrity",
                    "Transmission Security"
                ],
                "requirements": [
                    "Protected Health Information (PHI) must be safeguarded",
                    "Access controls must be implemented",
                    "Audit trails must be maintained",
                    "Data integrity must be ensured",
                    "Transmission security must be implemented"
                ]
            },
            ComplianceStandard.GDPR: {
                "name": "GDPR - General Data Protection Regulation",
                "description": "EU regulation for data protection and privacy",
                "key_sections": [
                    "Article 5 - Principles of Processing",
                    "Article 6 - Lawfulness of Processing",
                    "Article 7 - Conditions for Consent",
                    "Article 8 - Child's Consent",
                    "Article 9 - Processing of Special Categories",
                    "Article 12 - Transparent Information",
                    "Article 13 - Information to be Provided",
                    "Article 14 - Information to be Provided",
                    "Article 15 - Right of Access",
                    "Article 16 - Right to Rectification",
                    "Article 17 - Right to Erasure",
                    "Article 18 - Right to Restriction",
                    "Article 20 - Right to Data Portability",
                    "Article 25 - Data Protection by Design",
                    "Article 32 - Security of Processing",
                    "Article 33 - Breach Notification",
                    "Article 35 - Data Protection Impact Assessment"
                ],
                "requirements": [
                    "Personal data must be processed lawfully and transparently",
                    "Data minimization principle must be applied",
                    "Data subject rights must be respected",
                    "Data protection by design must be implemented",
                    "Security measures must be appropriate"
                ]
            }
        }
    
    def _setup_prompts(self):
        """Setup prompt templates for compliance mapping."""
        
        # System prompt for compliance mapping
        self.system_prompt = SystemMessagePromptTemplate.from_template("""
You are an expert healthcare compliance analyst with deep knowledge of:
- FDA 21 CFR Part 820 (Quality System Regulation)
- IEC 62304 (Medical Device Software Lifecycle)
- ISO 13485 (Medical Device Quality Management)
- ISO 27001 (Information Security Management)
- HIPAA (Health Insurance Portability and Accountability Act)
- GDPR (General Data Protection Regulation)

Your task is to map software requirements to relevant compliance standards and assess compliance levels.

Key principles:
1. Identify which compliance standards apply to each requirement
2. Map requirements to specific sections of applicable standards
3. Assess compliance level (fully compliant, partially compliant, non-compliant)
4. Identify gaps and provide recommendations
5. Consider risk implications for non-compliance
6. Ensure traceability between requirements and standards

Output format: JSON with structured compliance mapping objects.
""")
        
        # Human prompt template
        self.human_prompt = HumanMessagePromptTemplate.from_template("""
Please analyze the following requirements and map them to relevant healthcare compliance standards:

Requirements:
{requirements_json}

Compliance Standards Knowledge:
{compliance_knowledge}

Map each requirement to applicable compliance standards and return in the following JSON format:
{{
    "compliance_mappings": [
        {{
            "requirement_id": "REQ-001",
            "standard": "fda|iec_62304|iso_13485|iso_27001|hipaa|gdpr",
            "applicable_sections": ["section1", "section2"],
            "compliance_level": "fully_compliant|partially_compliant|non_compliant",
            "evidence": ["evidence1", "evidence2"],
            "gaps": ["gap1", "gap2"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}
    ],
    "compliance_summary": {{
        "total_requirements": 10,
        "fully_compliant": 6,
        "partially_compliant": 3,
        "non_compliant": 1,
        "standards_coverage": {{
            "fda": 8,
            "iec_62304": 5,
            "iso_13485": 7,
            "iso_27001": 4,
            "hipaa": 3,
            "gdpr": 2
        }}
    }}
}}

Focus on:
1. Patient safety implications
2. Data privacy and security requirements
3. Software lifecycle processes
4. Quality management requirements
5. Risk management obligations
6. Documentation and traceability needs
""")
        
        # Create the chat prompt template
        self.chat_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def map_compliance(self, state: GraphState) -> GraphState:
        """
        Map requirements to compliance standards.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with compliance mappings
        """
        logger.info("Starting compliance mapping")
        
        # Create workflow step
        step = WorkflowStep(
            step_name="compliance_mapper",
            status=ProcessingStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        state.workflow_steps.append(step)
        state.current_step = "compliance_mapper"
        
        try:
            if not state.extracted_requirements:
                logger.warning("No requirements found for compliance mapping")
                state.overall_status = ProcessingStatus.FAILED
                step.status = ProcessingStatus.FAILED
                step.error_message = "No requirements available for compliance mapping"
                return state
            
            # Map requirements to compliance standards
            compliance_mappings = self._map_requirements_to_standards(state.extracted_requirements)
            
            # Validate and enhance mappings
            validated_mappings = self._validate_and_enhance_mappings(compliance_mappings)
            
            # Update state
            state.compliance_mappings = validated_mappings
            state.overall_status = ProcessingStatus.COMPLETED if validated_mappings else ProcessingStatus.FAILED
            
            # Update workflow step
            step.status = ProcessingStatus.COMPLETED
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            step.output_data = {
                "mapped_requirements_count": len(validated_mappings),
                "standards_coverage": self._calculate_standards_coverage(validated_mappings),
                "compliance_levels": self._calculate_compliance_levels(validated_mappings)
            }
            
            logger.info(f"Successfully mapped {len(validated_mappings)} requirements to compliance standards")
            
        except Exception as e:
            error_msg = f"Compliance mapping failed: {str(e)}"
            logger.error(error_msg)
            state.error_log.append(error_msg)
            state.overall_status = ProcessingStatus.FAILED
            
            step.status = ProcessingStatus.FAILED
            step.end_time = datetime.now()
            step.error_message = error_msg
        
        return state
    
    def _map_requirements_to_standards(self, requirements: List[Requirement]) -> List[ComplianceMapping]:
        """Map requirements to compliance standards using Gemini."""
        try:
            # Prepare requirements data
            requirements_data = []
            for req in requirements:
                req_data = {
                    "id": req.id,
                    "title": req.title,
                    "description": req.description,
                    "type": req.type.value,
                    "priority": req.priority.value,
                    "risk_level": req.risk_level,
                    "compliance_standards": [std.value for std in req.compliance_standards],
                    "tags": req.tags
                }
                requirements_data.append(req_data)
            
            # Prepare compliance knowledge
            compliance_knowledge = json.dumps(self.compliance_standards, indent=2, default=str)
            
            # Prepare the prompt
            messages = self.chat_prompt.format_messages(
                requirements_json=json.dumps(requirements_data, indent=2),
                compliance_knowledge=compliance_knowledge
            )
            
            # Get response from Gemini
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Parse the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in response, using fallback mapping")
                return self._fallback_compliance_mapping(requirements)
            
            json_str = json_match.group()
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {str(e)}, using fallback mapping")
                return self._fallback_compliance_mapping(requirements)
            
            # Convert to ComplianceMapping objects
            mappings = []
            for mapping_data in parsed_data.get('compliance_mappings', []):
                try:
                    mapping = self._create_compliance_mapping_object(mapping_data)
                    if mapping:
                        mappings.append(mapping)
                except Exception as e:
                    logger.warning(f"Failed to create compliance mapping object: {str(e)}")
                    continue
            
            return mappings
            
        except Exception as e:
            logger.error(f"Failed to map requirements to standards: {str(e)}")
            return self._fallback_compliance_mapping(requirements)
    
    def _create_compliance_mapping_object(self, mapping_data: Dict[str, Any]) -> Optional[ComplianceMapping]:
        """Create a ComplianceMapping object from extracted data."""
        try:
            # Map string to ComplianceStandard enum
            standard_str = mapping_data.get('standard', '').lower()
            try:
                standard = ComplianceStandard(standard_str)
            except ValueError:
                logger.warning(f"Unknown compliance standard: {standard_str}")
                return None
            
            # Create compliance mapping object
            mapping = ComplianceMapping(
                requirement_id=mapping_data.get('requirement_id', ''),
                standard=standard,
                applicable_sections=mapping_data.get('applicable_sections', []),
                compliance_level=mapping_data.get('compliance_level', 'non_compliant'),
                evidence=mapping_data.get('evidence', []),
                gaps=mapping_data.get('gaps', []),
                recommendations=mapping_data.get('recommendations', [])
            )
            
            return mapping
            
        except Exception as e:
            logger.error(f"Failed to create compliance mapping object: {str(e)}")
            return None
    
    def _fallback_compliance_mapping(self, requirements: List[Requirement]) -> List[ComplianceMapping]:
        """Fallback compliance mapping using rule-based approach."""
        logger.info("Using fallback compliance mapping method")
        
        mappings = []
        
        for req in requirements:
            # Determine applicable standards based on requirement content
            applicable_standards = self._determine_applicable_standards(req)
            
            for standard in applicable_standards:
                # Create basic mapping
                mapping = ComplianceMapping(
                    requirement_id=req.id,
                    standard=standard,
                    applicable_sections=self._get_standard_sections(standard, req),
                    compliance_level=self._assess_compliance_level(req, standard),
                    evidence=self._generate_evidence(req, standard),
                    gaps=self._identify_gaps(req, standard),
                    recommendations=self._generate_recommendations(req, standard)
                )
                mappings.append(mapping)
        
        return mappings
    
    def _determine_applicable_standards(self, requirement: Requirement) -> List[ComplianceStandard]:
        """Determine which standards apply to a requirement."""
        applicable_standards = []
        description_lower = requirement.description.lower()
        
        # Check for explicit compliance standards in requirement
        for standard in requirement.compliance_standards:
            applicable_standards.append(standard)
        
        # Check for keywords in description
        for standard, keywords in HealthcareDomainConfig.COMPLIANCE_KEYWORDS.items():
            if any(keyword.lower() in description_lower for keyword in keywords):
                if standard not in applicable_standards:
                    applicable_standards.append(standard)
        
        # Default standards based on requirement type
        if not applicable_standards:
            if requirement.type.value in ['functional', 'non_functional']:
                applicable_standards.extend([ComplianceStandard.FDA, ComplianceStandard.IEC_62304])
            if requirement.type.value == 'security':
                applicable_standards.extend([ComplianceStandard.ISO_27001, ComplianceStandard.HIPAA])
            if requirement.type.value == 'compliance':
                applicable_standards.extend([ComplianceStandard.ISO_13485, ComplianceStandard.FDA])
        
        return list(set(applicable_standards))  # Remove duplicates
    
    def _get_standard_sections(self, standard: ComplianceStandard, requirement: Requirement) -> List[str]:
        """Get applicable sections of a standard for a requirement."""
        standard_info = self.compliance_standards.get(standard, {})
        sections = standard_info.get('key_sections', [])
        
        # Filter sections based on requirement content
        applicable_sections = []
        description_lower = requirement.description.lower()
        
        for section in sections:
            section_lower = section.lower()
            # Simple keyword matching
            if any(keyword in section_lower for keyword in description_lower.split()):
                applicable_sections.append(section)
        
        # If no specific sections found, return general sections
        if not applicable_sections:
            applicable_sections = sections[:3]  # Return first 3 sections
        
        return applicable_sections
    
    def _assess_compliance_level(self, requirement: Requirement, standard: ComplianceStandard) -> str:
        """Assess compliance level for a requirement against a standard."""
        # Simple heuristic based on requirement characteristics
        if requirement.priority.value == 'critical':
            return 'fully_compliant' if requirement.risk_level == 'low' else 'partially_compliant'
        elif requirement.priority.value == 'high':
            return 'partially_compliant'
        else:
            return 'non_compliant'
    
    def _generate_evidence(self, requirement: Requirement, standard: ComplianceStandard) -> List[str]:
        """Generate evidence for compliance assessment."""
        evidence = [
            f"Requirement {requirement.id} addresses {standard.value} compliance",
            f"Risk level: {requirement.risk_level}",
            f"Priority: {requirement.priority.value}"
        ]
        
        if requirement.acceptance_criteria:
            evidence.append(f"Acceptance criteria defined: {len(requirement.acceptance_criteria)} items")
        
        return evidence
    
    def _identify_gaps(self, requirement: Requirement, standard: ComplianceStandard) -> List[str]:
        """Identify compliance gaps."""
        gaps = []
        
        if not requirement.acceptance_criteria:
            gaps.append("No acceptance criteria defined")
        
        if not requirement.stakeholders:
            gaps.append("No stakeholders identified")
        
        if requirement.risk_level == 'critical' and requirement.priority.value != 'critical':
            gaps.append("Critical risk level but non-critical priority")
        
        return gaps
    
    def _generate_recommendations(self, requirement: Requirement, standard: ComplianceStandard) -> List[str]:
        """Generate recommendations for compliance improvement."""
        recommendations = []
        
        if not requirement.acceptance_criteria:
            recommendations.append("Define clear acceptance criteria")
        
        if not requirement.stakeholders:
            recommendations.append("Identify relevant stakeholders")
        
        if requirement.risk_level == 'critical':
            recommendations.append("Implement additional risk mitigation measures")
        
        recommendations.append(f"Ensure documentation meets {standard.value} requirements")
        
        return recommendations
    
    def _validate_and_enhance_mappings(self, mappings: List[ComplianceMapping]) -> List[ComplianceMapping]:
        """Validate and enhance compliance mappings."""
        validated_mappings = []
        
        for mapping in mappings:
            # Basic validation
            if not mapping.requirement_id or not mapping.standard:
                continue
            
            # Enhance with additional information
            mapping = self._enhance_mapping(mapping)
            
            # Add to validated list
            validated_mappings.append(mapping)
        
        return validated_mappings
    
    def _enhance_mapping(self, mapping: ComplianceMapping) -> ComplianceMapping:
        """Enhance compliance mapping with additional information."""
        # Add standard-specific recommendations
        standard_recommendations = self._get_standard_recommendations(mapping.standard)
        mapping.recommendations.extend(standard_recommendations)
        mapping.recommendations = list(set(mapping.recommendations))  # Remove duplicates
        
        return mapping
    
    def _get_standard_recommendations(self, standard: ComplianceStandard) -> List[str]:
        """Get standard-specific recommendations."""
        standard_info = self.compliance_standards.get(standard, {})
        requirements = standard_info.get('requirements', [])
        
        recommendations = []
        for req in requirements:
            recommendations.append(f"Ensure compliance with: {req}")
        
        return recommendations
    
    def _calculate_standards_coverage(self, mappings: List[ComplianceMapping]) -> Dict[str, int]:
        """Calculate coverage by compliance standards."""
        coverage = {}
        for mapping in mappings:
            standard = mapping.standard.value
            coverage[standard] = coverage.get(standard, 0) + 1
        return coverage
    
    def _calculate_compliance_levels(self, mappings: List[ComplianceMapping]) -> Dict[str, int]:
        """Calculate distribution of compliance levels."""
        levels = {}
        for mapping in mappings:
            level = mapping.compliance_level
            levels[level] = levels.get(level, 0) + 1
        return levels


# Export the main mapper class
__all__ = ["ComplianceMapper"]
