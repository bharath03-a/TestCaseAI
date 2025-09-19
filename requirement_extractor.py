"""
Requirement extraction module using Gemini for healthcare domain understanding.
"""

import json
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from models import (
    Requirement, RequirementType, TestCasePriority, ComplianceStandard,
    GraphState, ProcessingStatus, WorkflowStep
)
from config import settings, HealthcareDomainConfig

logger = logging.getLogger(__name__)


class RequirementExtractor:
    """Extract requirements from healthcare documents using Gemini AI."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            top_p=settings.gemini_top_p,
            top_k=settings.gemini_top_k,
            google_api_key=settings.google_api_key
        )
        
        # Initialize prompts
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompt templates for requirement extraction."""
        
        # System prompt for requirement extraction
        self.system_prompt = SystemMessagePromptTemplate.from_template("""
You are an expert healthcare software requirements analyst with deep knowledge of:
- FDA regulations (21 CFR Part 820, 510(k), PMA)
- IEC 62304 (Medical Device Software Lifecycle)
- ISO 13485 (Medical Device Quality Management)
- ISO 27001 (Information Security Management)
- HIPAA (Health Insurance Portability and Accountability Act)
- GDPR (General Data Protection Regulation)

Your task is to extract, analyze, and structure requirements from healthcare software documents.

Key principles:
1. Identify both functional and non-functional requirements
2. Map requirements to relevant compliance standards
3. Assess risk levels based on patient safety impact
4. Extract acceptance criteria and dependencies
5. Identify stakeholders and their roles
6. Consider data privacy and security implications

Output format: JSON with structured requirement objects.
""")
        
        # Human prompt template
        self.human_prompt = HumanMessagePromptTemplate.from_template("""
Please analyze the following healthcare software document and extract all requirements:

Document Content:
{document_content}

Extract requirements and return them in the following JSON format:
{{
    "requirements": [
        {{
            "id": "REQ-001",
            "title": "Requirement Title",
            "description": "Detailed requirement description",
            "type": "functional|non_functional|performance|security|compliance|usability",
            "priority": "critical|high|medium|low",
            "source_section": "Section name or reference",
            "source_line_number": 123,
            "stakeholders": ["stakeholder1", "stakeholder2"],
            "acceptance_criteria": ["criteria1", "criteria2"],
            "dependencies": ["REQ-002", "REQ-003"],
            "compliance_standards": ["fda", "iec_62304", "iso_13485"],
            "risk_level": "low|medium|high|critical",
            "complexity": "simple|moderate|complex",
            "estimated_effort": 8,
            "tags": ["tag1", "tag2"]
        }}
    ],
    "analysis_summary": {{
        "total_requirements": 10,
        "functional_count": 6,
        "non_functional_count": 4,
        "compliance_requirements": 3,
        "high_risk_requirements": 2,
        "estimated_total_effort": 80
    }}
}}

Focus on:
1. Patient safety requirements
2. Data privacy and security
3. Regulatory compliance
4. System reliability and performance
5. User interface and usability
6. Integration requirements
7. Audit and traceability needs
""")
        
        # Create the chat prompt template
        self.chat_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def extract_requirements(self, state: GraphState) -> GraphState:
        """
        Extract requirements from parsed documents.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with extracted requirements
        """
        logger.info("Starting requirement extraction")
        
        # Create workflow step
        step = WorkflowStep(
            step_name="requirement_extractor",
            status=ProcessingStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        state.workflow_steps.append(step)
        state.current_step = "requirement_extractor"
        
        try:
            all_requirements = []
            
            # Process each document's content
            for i, content in enumerate(state.raw_text_content):
                if not content.strip():
                    continue
                
                logger.info(f"Processing document {i+1}/{len(state.raw_text_content)}")
                
                # Extract requirements from this document
                doc_requirements = self._extract_from_content(
                    content, 
                    state.document_metadata[i] if i < len(state.document_metadata) else None
                )
                
                all_requirements.extend(doc_requirements)
            
            # Post-process and validate requirements
            validated_requirements = self._validate_and_enhance_requirements(all_requirements)
            
            # Update state
            state.extracted_requirements = validated_requirements
            state.overall_status = ProcessingStatus.COMPLETED if validated_requirements else ProcessingStatus.FAILED
            
            # Update workflow step
            step.status = ProcessingStatus.COMPLETED
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            step.output_data = {
                "extracted_requirements_count": len(validated_requirements),
                "functional_requirements": len([r for r in validated_requirements if r.type == RequirementType.FUNCTIONAL]),
                "non_functional_requirements": len([r for r in validated_requirements if r.type == RequirementType.NON_FUNCTIONAL]),
                "compliance_requirements": len([r for r in validated_requirements if r.type == RequirementType.COMPLIANCE])
            }
            
            logger.info(f"Successfully extracted {len(validated_requirements)} requirements")
            
        except Exception as e:
            error_msg = f"Requirement extraction failed: {str(e)}"
            logger.error(error_msg)
            state.error_log.append(error_msg)
            state.overall_status = ProcessingStatus.FAILED
            
            step.status = ProcessingStatus.FAILED
            step.end_time = datetime.now()
            step.error_message = error_msg
        
        return state
    
    def _extract_from_content(self, content: str, metadata: Optional[Any] = None) -> List[Requirement]:
        """Extract requirements from document content using Gemini."""
        try:
            # Prepare the prompt
            messages = self.chat_prompt.format_messages(
                document_content=content[:settings.max_input_length]  # Truncate if too long
            )
            
            # Get response from Gemini
            response = self.llm.invoke(messages)
            
            # Parse the response
            response_text = response.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in response, attempting to parse as plain text")
                return self._fallback_extraction(content, metadata)
            
            json_str = json_match.group()
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {str(e)}, using fallback extraction")
                return self._fallback_extraction(content, metadata)
            
            # Convert to Requirement objects
            requirements = []
            for req_data in parsed_data.get('requirements', []):
                try:
                    requirement = self._create_requirement_object(req_data, metadata)
                    if requirement:
                        requirements.append(requirement)
                except Exception as e:
                    logger.warning(f"Failed to create requirement object: {str(e)}")
                    continue
            
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to extract requirements from content: {str(e)}")
            return self._fallback_extraction(content, metadata)
    
    def _create_requirement_object(self, req_data: Dict[str, Any], metadata: Optional[Any] = None) -> Optional[Requirement]:
        """Create a Requirement object from extracted data."""
        try:
            # Generate unique ID if not provided
            req_id = req_data.get('id', f"REQ-{uuid.uuid4().hex[:8].upper()}")
            
            # Map string values to enums
            req_type = self._map_requirement_type(req_data.get('type', 'functional'))
            priority = self._map_priority(req_data.get('priority', 'medium'))
            risk_level = req_data.get('risk_level', 'medium')
            complexity = req_data.get('complexity', 'moderate')
            
            # Map compliance standards
            compliance_standards = []
            for std in req_data.get('compliance_standards', []):
                try:
                    compliance_standards.append(ComplianceStandard(std.lower()))
                except ValueError:
                    logger.warning(f"Unknown compliance standard: {std}")
            
            # Create requirement object
            requirement = Requirement(
                id=req_id,
                title=req_data.get('title', 'Untitled Requirement'),
                description=req_data.get('description', ''),
                type=req_type,
                priority=priority,
                source_document=metadata.filename if metadata else 'unknown',
                source_section=req_data.get('source_section'),
                source_line_number=req_data.get('source_line_number'),
                stakeholders=req_data.get('stakeholders', []),
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                dependencies=req_data.get('dependencies', []),
                compliance_standards=compliance_standards,
                risk_level=risk_level,
                complexity=complexity,
                estimated_effort=req_data.get('estimated_effort'),
                tags=req_data.get('tags', [])
            )
            
            return requirement
            
        except Exception as e:
            logger.error(f"Failed to create requirement object: {str(e)}")
            return None
    
    def _map_requirement_type(self, type_str: str) -> RequirementType:
        """Map string to RequirementType enum."""
        type_mapping = {
            'functional': RequirementType.FUNCTIONAL,
            'non_functional': RequirementType.NON_FUNCTIONAL,
            'performance': RequirementType.PERFORMANCE,
            'security': RequirementType.SECURITY,
            'compliance': RequirementType.COMPLIANCE,
            'usability': RequirementType.USABILITY
        }
        return type_mapping.get(type_str.lower(), RequirementType.FUNCTIONAL)
    
    def _map_priority(self, priority_str: str) -> TestCasePriority:
        """Map string to TestCasePriority enum."""
        priority_mapping = {
            'critical': TestCasePriority.CRITICAL,
            'high': TestCasePriority.HIGH,
            'medium': TestCasePriority.MEDIUM,
            'low': TestCasePriority.LOW
        }
        return priority_mapping.get(priority_str.lower(), TestCasePriority.MEDIUM)
    
    def _fallback_extraction(self, content: str, metadata: Optional[Any] = None) -> List[Requirement]:
        """Fallback extraction method using pattern matching."""
        logger.info("Using fallback extraction method")
        
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'(?:The\s+)?system\s+shall\s+(.+?)(?:\.|$)',  # "The system shall..."
            r'(?:The\s+)?software\s+shall\s+(.+?)(?:\.|$)',  # "The software shall..."
            r'(?:The\s+)?application\s+shall\s+(.+?)(?:\.|$)',  # "The application shall..."
            r'(?:The\s+)?system\s+must\s+(.+?)(?:\.|$)',  # "The system must..."
            r'(?:The\s+)?system\s+should\s+(.+?)(?:\.|$)',  # "The system should..."
            r'REQ-\d+[:\s]+(.+?)(?:\.|$)',  # "REQ-001: ..."
            r'Requirement\s+\d+[:\s]+(.+?)(?:\.|$)',  # "Requirement 1: ..."
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                description = match.group(1).strip()
                if len(description) > 10:  # Filter out very short matches
                    req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
                    
                    # Determine type based on content
                    req_type = self._classify_requirement_type(description)
                    priority = self._classify_priority(description)
                    compliance_standards = self._identify_compliance_standards(description)
                    
                    requirement = Requirement(
                        id=req_id,
                        title=f"Extracted Requirement {len(requirements) + 1}",
                        description=description,
                        type=req_type,
                        priority=priority,
                        source_document=metadata.filename if metadata else 'unknown',
                        source_section=f"Pattern {i+1}",
                        compliance_standards=compliance_standards,
                        risk_level=self._assess_risk_level(description),
                        complexity=self._assess_complexity(description)
                    )
                    
                    requirements.append(requirement)
        
        return requirements
    
    def _classify_requirement_type(self, description: str) -> RequirementType:
        """Classify requirement type based on description content."""
        description_lower = description.lower()
        
        # Security keywords
        security_keywords = ['security', 'encrypt', 'authenticate', 'authorize', 'access control', 'privacy', 'hipaa', 'gdpr']
        if any(keyword in description_lower for keyword in security_keywords):
            return RequirementType.SECURITY
        
        # Performance keywords
        performance_keywords = ['performance', 'speed', 'response time', 'throughput', 'scalability', 'load']
        if any(keyword in description_lower for keyword in performance_keywords):
            return RequirementType.PERFORMANCE
        
        # Compliance keywords
        compliance_keywords = ['compliance', 'fda', 'iec', 'iso', 'standard', 'regulation', 'audit']
        if any(keyword in description_lower for keyword in compliance_keywords):
            return RequirementType.COMPLIANCE
        
        # Usability keywords
        usability_keywords = ['user interface', 'ui', 'ux', 'usability', 'user experience', 'ergonomic']
        if any(keyword in description_lower for keyword in usability_keywords):
            return RequirementType.USABILITY
        
        # Default to functional
        return RequirementType.FUNCTIONAL
    
    def _classify_priority(self, description: str) -> TestCasePriority:
        """Classify priority based on description content."""
        description_lower = description.lower()
        
        # Critical keywords
        critical_keywords = ['critical', 'safety', 'life-threatening', 'emergency', 'patient safety']
        if any(keyword in description_lower for keyword in critical_keywords):
            return TestCasePriority.CRITICAL
        
        # High keywords
        high_keywords = ['important', 'essential', 'mandatory', 'required', 'must']
        if any(keyword in description_lower for keyword in high_keywords):
            return TestCasePriority.HIGH
        
        # Low keywords
        low_keywords = ['optional', 'nice to have', 'enhancement', 'improvement']
        if any(keyword in description_lower for keyword in low_keywords):
            return TestCasePriority.LOW
        
        # Default to medium
        return TestCasePriority.MEDIUM
    
    def _identify_compliance_standards(self, description: str) -> List[ComplianceStandard]:
        """Identify compliance standards mentioned in description."""
        description_lower = description.lower()
        standards = []
        
        for standard, keywords in HealthcareDomainConfig.COMPLIANCE_KEYWORDS.items():
            if any(keyword.lower() in description_lower for keyword in keywords):
                standards.append(standard)
        
        return standards
    
    def _assess_risk_level(self, description: str) -> str:
        """Assess risk level based on description content."""
        description_lower = description.lower()
        
        for risk_level, keywords in HealthcareDomainConfig.RISK_LEVELS.items():
            if any(keyword in description_lower for keyword in keywords):
                return risk_level
        
        return "medium"
    
    def _assess_complexity(self, description: str) -> str:
        """Assess complexity based on description length and content."""
        if len(description) < 50:
            return "simple"
        elif len(description) < 200:
            return "moderate"
        else:
            return "complex"
    
    def _validate_and_enhance_requirements(self, requirements: List[Requirement]) -> List[Requirement]:
        """Validate and enhance extracted requirements."""
        validated_requirements = []
        
        for req in requirements:
            # Basic validation
            if not req.title or not req.description:
                continue
            
            # Enhance with additional information
            req = self._enhance_requirement(req)
            
            # Add to validated list
            validated_requirements.append(req)
        
        # Remove duplicates based on description similarity
        validated_requirements = self._remove_duplicates(validated_requirements)
        
        return validated_requirements
    
    def _enhance_requirement(self, requirement: Requirement) -> Requirement:
        """Enhance requirement with additional information."""
        # Add healthcare-specific tags
        healthcare_tags = []
        description_lower = requirement.description.lower()
        
        for term in HealthcareDomainConfig.MEDICAL_TERMS:
            if term in description_lower:
                healthcare_tags.append(term)
        
        # Add compliance tags
        for standard in requirement.compliance_standards:
            healthcare_tags.append(standard.value)
        
        # Update tags
        requirement.tags.extend(healthcare_tags)
        requirement.tags = list(set(requirement.tags))  # Remove duplicates
        
        # Estimate effort if not provided
        if not requirement.estimated_effort:
            requirement.estimated_effort = self._estimate_effort(requirement)
        
        return requirement
    
    def _estimate_effort(self, requirement: Requirement) -> int:
        """Estimate effort in hours based on requirement characteristics."""
        base_effort = 4  # Base hours
        
        # Adjust based on complexity
        complexity_multiplier = {
            "simple": 0.5,
            "moderate": 1.0,
            "complex": 2.0
        }
        
        # Adjust based on type
        type_multiplier = {
            RequirementType.FUNCTIONAL: 1.0,
            RequirementType.NON_FUNCTIONAL: 1.2,
            RequirementType.PERFORMANCE: 1.5,
            RequirementType.SECURITY: 2.0,
            RequirementType.COMPLIANCE: 1.8,
            RequirementType.USABILITY: 1.3
        }
        
        # Adjust based on risk level
        risk_multiplier = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.5,
            "critical": 2.0
        }
        
        effort = base_effort
        effort *= complexity_multiplier.get(requirement.complexity, 1.0)
        effort *= type_multiplier.get(requirement.type, 1.0)
        effort *= risk_multiplier.get(requirement.risk_level, 1.0)
        
        return max(1, int(effort))
    
    def _remove_duplicates(self, requirements: List[Requirement]) -> List[Requirement]:
        """Remove duplicate requirements based on description similarity."""
        unique_requirements = []
        
        for req in requirements:
            is_duplicate = False
            for existing_req in unique_requirements:
                # Simple similarity check based on description
                similarity = self._calculate_similarity(req.description, existing_req.description)
                if similarity > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_requirements.append(req)
        
        return unique_requirements
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)


# Export the main extractor class
__all__ = ["RequirementExtractor"]
