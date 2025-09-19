"""
Quality validation module for test case completeness and accuracy.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from models import (
    Requirement, TestCase, ComplianceMapping, QualityMetrics, GraphState,
    ProcessingStatus, WorkflowStep, ValidationResult
)
from config import settings, HealthcareDomainConfig

logger = logging.getLogger(__name__)


class QualityValidator:
    """Validate quality of generated test cases and requirements."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            top_p=settings.gemini_top_p,
            top_k=settings.gemini_top_k,
            google_api_key=settings.google_api_key
        )
        
        # Initialize quality criteria
        self._setup_quality_criteria()
        self._setup_prompts()
    
    def _setup_quality_criteria(self):
        """Setup quality criteria for validation."""
        self.quality_criteria = {
            "completeness": {
                "requirements": {
                    "min_title_length": 10,
                    "min_description_length": 50,
                    "required_fields": ["title", "description", "type", "priority"],
                    "optional_fields": ["acceptance_criteria", "stakeholders", "dependencies"]
                },
                "test_cases": {
                    "min_title_length": 10,
                    "min_description_length": 30,
                    "min_test_steps": 3,
                    "min_expected_results": 2,
                    "required_fields": ["title", "description", "test_steps", "expected_results"],
                    "optional_fields": ["preconditions", "test_data", "automation_status"]
                }
            },
            "accuracy": {
                "requirements": {
                    "coherence_check": True,
                    "consistency_check": True,
                    "ambiguity_check": True,
                    "completeness_check": True
                },
                "test_cases": {
                    "traceability_check": True,
                    "coverage_check": True,
                    "clarity_check": True,
                    "feasibility_check": True
                }
            },
            "traceability": {
                "requirement_to_test_mapping": True,
                "test_to_requirement_mapping": True,
                "compliance_standard_mapping": True,
                "bidirectional_traceability": True
            },
            "compliance": {
                "regulatory_standards": True,
                "audit_trail_completeness": True,
                "documentation_standards": True,
                "risk_assessment_adequacy": True
            }
        }
    
    def _setup_prompts(self):
        """Setup prompt templates for quality validation."""
        
        # System prompt for quality validation
        self.system_prompt = SystemMessagePromptTemplate.from_template("""
You are an expert healthcare software quality assurance analyst with deep knowledge of:
- Healthcare software quality standards
- Test case quality assessment
- Requirement validation methodologies
- Compliance verification processes
- Risk-based quality assessment
- Traceability matrix validation

Your task is to validate the quality of generated test cases and requirements.

Key principles:
1. Assess completeness of requirements and test cases
2. Evaluate accuracy and clarity of content
3. Verify traceability between requirements and tests
4. Check compliance with healthcare standards
5. Identify gaps and improvement opportunities
6. Provide actionable recommendations
7. Calculate quality scores and metrics
8. Ensure patient safety considerations

Quality dimensions to evaluate:
- Completeness: Are all necessary elements present?
- Accuracy: Is the content correct and unambiguous?
- Traceability: Are requirements properly linked to tests?
- Compliance: Do they meet regulatory standards?
- Coverage: Do tests adequately cover requirements?
- Clarity: Are they clear and understandable?
- Feasibility: Can they be executed effectively?

Output format: JSON with structured quality assessment.
""")
        
        # Human prompt template
        self.human_prompt = HumanMessagePromptTemplate.from_template("""
Please validate the quality of the following healthcare software requirements and test cases:

Requirements:
{requirements_json}

Test Cases:
{test_cases_json}

Compliance Mappings:
{compliance_mappings_json}

Quality Criteria:
{quality_criteria_json}

Evaluate and return in the following JSON format:
{{
    "quality_metrics": {{
        "completeness_score": 0.85,
        "accuracy_score": 0.90,
        "traceability_score": 0.95,
        "compliance_score": 0.88,
        "coverage_percentage": 85.0,
        "total_issues": 12,
        "critical_issues": 2,
        "recommendations": [
            "Add acceptance criteria to REQ-001",
            "Improve test case traceability for TC-005"
        ]
    }},
    "requirement_validation": [
        {{
            "requirement_id": "REQ-001",
            "completeness_score": 0.8,
            "accuracy_score": 0.9,
            "issues": ["Missing acceptance criteria"],
            "recommendations": ["Define clear acceptance criteria"]
        }}
    ],
    "test_case_validation": [
        {{
            "test_case_id": "TC-001",
            "completeness_score": 0.9,
            "accuracy_score": 0.85,
            "traceability_score": 1.0,
            "issues": ["Test steps could be more detailed"],
            "recommendations": ["Add more specific test steps"]
        }}
    ],
    "traceability_analysis": {{
        "requirement_coverage": 0.9,
        "test_coverage": 0.85,
        "missing_traceability": ["REQ-003"],
        "orphaned_tests": ["TC-010"]
    }},
    "compliance_analysis": {{
        "fda_compliance": 0.9,
        "iec_62304_compliance": 0.85,
        "iso_13485_compliance": 0.88,
        "compliance_gaps": ["Missing risk assessment for REQ-002"]
    }},
    "overall_assessment": {{
        "quality_grade": "B+",
        "ready_for_review": true,
        "critical_actions_required": ["Fix traceability gaps"],
        "improvement_priorities": ["Enhance test coverage", "Improve documentation"]
    }}
}}

Focus on:
1. Patient safety implications
2. Regulatory compliance requirements
3. Test case completeness and clarity
4. Requirement traceability
5. Coverage gaps and overlaps
6. Actionable improvement recommendations
""")
        
        # Create the chat prompt template
        self.chat_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def validate_quality(self, state: GraphState) -> GraphState:
        """
        Validate quality of requirements and test cases.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with quality metrics
        """
        logger.info("Starting quality validation")
        
        # Create workflow step
        step = WorkflowStep(
            step_name="quality_validator",
            status=ProcessingStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        state.workflow_steps.append(step)
        state.current_step = "quality_validator"
        
        try:
            if not state.extracted_requirements and not state.generated_test_cases:
                logger.warning("No requirements or test cases found for quality validation")
                state.overall_status = ProcessingStatus.FAILED
                step.status = ProcessingStatus.FAILED
                step.error_message = "No requirements or test cases available for quality validation"
                return state
            
            # Perform quality validation
            quality_metrics = self._validate_requirements_and_tests(
                state.extracted_requirements,
                state.generated_test_cases,
                state.compliance_mappings
            )
            
            # Update state
            state.quality_metrics = quality_metrics
            state.overall_status = ProcessingStatus.COMPLETED if quality_metrics else ProcessingStatus.FAILED
            
            # Update workflow step
            step.status = ProcessingStatus.COMPLETED
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            step.output_data = {
                "completeness_score": quality_metrics.completeness_score if quality_metrics else 0.0,
                "accuracy_score": quality_metrics.accuracy_score if quality_metrics else 0.0,
                "traceability_score": quality_metrics.traceability_score if quality_metrics else 0.0,
                "compliance_score": quality_metrics.compliance_score if quality_metrics else 0.0,
                "total_issues": quality_metrics.total_issues if quality_metrics else 0
            }
            
            logger.info(f"Quality validation completed with overall score: {quality_metrics.completeness_score if quality_metrics else 0.0}")
            
        except Exception as e:
            error_msg = f"Quality validation failed: {str(e)}"
            logger.error(error_msg)
            state.error_log.append(error_msg)
            state.overall_status = ProcessingStatus.FAILED
            
            step.status = ProcessingStatus.FAILED
            step.end_time = datetime.now()
            step.error_message = error_msg
        
        return state
    
    def _validate_requirements_and_tests(self, requirements: List[Requirement], 
                                       test_cases: List[TestCase],
                                       compliance_mappings: List[ComplianceMapping]) -> Optional[QualityMetrics]:
        """Validate quality using Gemini AI."""
        try:
            # Prepare data for validation
            requirements_data = [self._serialize_requirement(req) for req in requirements]
            test_cases_data = [self._serialize_test_case(tc) for tc in test_cases]
            compliance_data = [self._serialize_compliance_mapping(cm) for cm in compliance_mappings]
            
            # Prepare the prompt
            messages = self.chat_prompt.format_messages(
                requirements_json=json.dumps(requirements_data, indent=2),
                test_cases_json=json.dumps(test_cases_data, indent=2),
                compliance_mappings_json=json.dumps(compliance_data, indent=2),
                quality_criteria_json=json.dumps(self.quality_criteria, indent=2)
            )
            
            # Get response from Gemini
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Parse the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in response, using fallback validation")
                return self._fallback_quality_validation(requirements, test_cases, compliance_mappings)
            
            json_str = json_match.group()
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {str(e)}, using fallback validation")
                return self._fallback_quality_validation(requirements, test_cases, compliance_mappings)
            
            # Extract quality metrics
            quality_data = parsed_data.get('quality_metrics', {})
            if not quality_data:
                return self._fallback_quality_validation(requirements, test_cases, compliance_mappings)
            
            # Create QualityMetrics object
            quality_metrics = QualityMetrics(
                completeness_score=quality_data.get('completeness_score', 0.0),
                accuracy_score=quality_data.get('accuracy_score', 0.0),
                traceability_score=quality_data.get('traceability_score', 0.0),
                compliance_score=quality_data.get('compliance_score', 0.0),
                coverage_percentage=quality_data.get('coverage_percentage', 0.0),
                total_issues=quality_data.get('total_issues', 0),
                critical_issues=quality_data.get('critical_issues', 0),
                recommendations=quality_data.get('recommendations', [])
            )
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Failed to validate quality: {str(e)}")
            return self._fallback_quality_validation(requirements, test_cases, compliance_mappings)
    
    def _fallback_quality_validation(self, requirements: List[Requirement], 
                                   test_cases: List[TestCase],
                                   compliance_mappings: List[ComplianceMapping]) -> QualityMetrics:
        """Fallback quality validation using rule-based approach."""
        logger.info("Using fallback quality validation method")
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(requirements, test_cases)
        
        # Calculate accuracy score
        accuracy_score = self._calculate_accuracy_score(requirements, test_cases)
        
        # Calculate traceability score
        traceability_score = self._calculate_traceability_score(requirements, test_cases)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(requirements, test_cases, compliance_mappings)
        
        # Calculate coverage percentage
        coverage_percentage = self._calculate_coverage_percentage(requirements, test_cases)
        
        # Count issues
        total_issues, critical_issues = self._count_issues(requirements, test_cases)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(requirements, test_cases, compliance_mappings)
        
        return QualityMetrics(
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            traceability_score=traceability_score,
            compliance_score=compliance_score,
            coverage_percentage=coverage_percentage,
            total_issues=total_issues,
            critical_issues=critical_issues,
            recommendations=recommendations
        )
    
    def _calculate_completeness_score(self, requirements: List[Requirement], 
                                    test_cases: List[TestCase]) -> float:
        """Calculate completeness score."""
        if not requirements and not test_cases:
            return 0.0
        
        req_scores = []
        for req in requirements:
            score = 0.0
            if req.title and len(req.title) >= 10:
                score += 0.2
            if req.description and len(req.description) >= 50:
                score += 0.3
            if req.type:
                score += 0.1
            if req.priority:
                score += 0.1
            if req.acceptance_criteria:
                score += 0.2
            if req.stakeholders:
                score += 0.1
            req_scores.append(score)
        
        tc_scores = []
        for tc in test_cases:
            score = 0.0
            if tc.title and len(tc.title) >= 10:
                score += 0.2
            if tc.description and len(tc.description) >= 30:
                score += 0.2
            if tc.test_steps and len(tc.test_steps) >= 3:
                score += 0.3
            if tc.expected_results and len(tc.expected_results) >= 2:
                score += 0.2
            if tc.preconditions:
                score += 0.1
            tc_scores.append(score)
        
        all_scores = req_scores + tc_scores
        return sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    def _calculate_accuracy_score(self, requirements: List[Requirement], 
                                test_cases: List[TestCase]) -> float:
        """Calculate accuracy score."""
        if not requirements and not test_cases:
            return 0.0
        
        # Simple heuristic-based accuracy assessment
        accuracy_factors = []
        
        # Check for common accuracy issues
        for req in requirements:
            score = 1.0
            # Check for ambiguous language
            if any(word in req.description.lower() for word in ['maybe', 'perhaps', 'might', 'could']):
                score -= 0.1
            # Check for incomplete sentences
            if req.description.endswith(('...', 'etc', 'etc.')):
                score -= 0.1
            # Check for proper formatting
            if not req.description[0].isupper():
                score -= 0.05
            accuracy_factors.append(max(0.0, score))
        
        for tc in test_cases:
            score = 1.0
            # Check for clear test steps
            if any(step.lower().startswith(('verify', 'check', 'validate', 'confirm')) for step in tc.test_steps):
                score += 0.1
            # Check for specific expected results
            if any(result.lower().startswith(('should', 'must', 'will')) for result in tc.expected_results):
                score += 0.1
            accuracy_factors.append(min(1.0, score))
        
        return sum(accuracy_factors) / len(accuracy_factors) if accuracy_factors else 0.0
    
    def _calculate_traceability_score(self, requirements: List[Requirement], 
                                    test_cases: List[TestCase]) -> float:
        """Calculate traceability score."""
        if not requirements or not test_cases:
            return 0.0
        
        # Count requirements with test coverage
        req_with_tests = set()
        for tc in test_cases:
            req_with_tests.update(tc.requirement_ids)
        
        # Count test cases with requirement links
        tc_with_reqs = sum(1 for tc in test_cases if tc.requirement_ids)
        
        # Calculate scores
        req_coverage = len(req_with_tests) / len(requirements) if requirements else 0.0
        tc_coverage = tc_with_reqs / len(test_cases) if test_cases else 0.0
        
        return (req_coverage + tc_coverage) / 2.0
    
    def _calculate_compliance_score(self, requirements: List[Requirement], 
                                  test_cases: List[TestCase],
                                  compliance_mappings: List[ComplianceMapping]) -> float:
        """Calculate compliance score."""
        if not requirements:
            return 0.0
        
        # Count requirements with compliance mappings
        req_with_compliance = set()
        for mapping in compliance_mappings:
            req_with_compliance.add(mapping.requirement_id)
        
        # Count test cases with compliance standards
        tc_with_compliance = sum(1 for tc in test_cases if tc.compliance_standards)
        
        # Calculate scores
        req_compliance = len(req_with_compliance) / len(requirements) if requirements else 0.0
        tc_compliance = tc_with_compliance / len(test_cases) if test_cases else 0.0
        
        return (req_compliance + tc_compliance) / 2.0
    
    def _calculate_coverage_percentage(self, requirements: List[Requirement], 
                                     test_cases: List[TestCase]) -> float:
        """Calculate test coverage percentage."""
        if not requirements:
            return 0.0
        
        # Count requirements covered by tests
        covered_requirements = set()
        for tc in test_cases:
            covered_requirements.update(tc.requirement_ids)
        
        return (len(covered_requirements) / len(requirements)) * 100.0
    
    def _count_issues(self, requirements: List[Requirement], 
                     test_cases: List[TestCase]) -> Tuple[int, int]:
        """Count total and critical issues."""
        total_issues = 0
        critical_issues = 0
        
        # Check requirements for issues
        for req in requirements:
            if not req.title or len(req.title) < 10:
                total_issues += 1
                if req.priority.value == 'critical':
                    critical_issues += 1
            
            if not req.description or len(req.description) < 50:
                total_issues += 1
                if req.priority.value == 'critical':
                    critical_issues += 1
            
            if not req.acceptance_criteria:
                total_issues += 1
                if req.risk_level == 'critical':
                    critical_issues += 1
        
        # Check test cases for issues
        for tc in test_cases:
            if not tc.test_steps or len(tc.test_steps) < 3:
                total_issues += 1
                if tc.priority.value == 'critical':
                    critical_issues += 1
            
            if not tc.expected_results or len(tc.expected_results) < 2:
                total_issues += 1
                if tc.priority.value == 'critical':
                    critical_issues += 1
            
            if not tc.requirement_ids:
                total_issues += 1
                if tc.risk_level == 'critical':
                    critical_issues += 1
        
        return total_issues, critical_issues
    
    def _generate_recommendations(self, requirements: List[Requirement], 
                                test_cases: List[TestCase],
                                compliance_mappings: List[ComplianceMapping]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Requirements recommendations
        for req in requirements:
            if not req.acceptance_criteria:
                recommendations.append(f"Add acceptance criteria to {req.id}")
            if not req.stakeholders:
                recommendations.append(f"Identify stakeholders for {req.id}")
            if req.risk_level == 'critical' and req.priority.value != 'critical':
                recommendations.append(f"Review priority for critical risk requirement {req.id}")
        
        # Test case recommendations
        for tc in test_cases:
            if not tc.requirement_ids:
                recommendations.append(f"Add requirement traceability to {tc.id}")
            if len(tc.test_steps) < 3:
                recommendations.append(f"Add more detailed test steps to {tc.id}")
            if tc.automation_status == 'manual' and tc.type.value in ['functional', 'performance']:
                recommendations.append(f"Consider automation for {tc.id}")
        
        # Coverage recommendations
        req_ids = {req.id for req in requirements}
        covered_reqs = set()
        for tc in test_cases:
            covered_reqs.update(tc.requirement_ids)
        
        uncovered_reqs = req_ids - covered_reqs
        if uncovered_reqs:
            recommendations.append(f"Add test cases for uncovered requirements: {', '.join(list(uncovered_reqs)[:3])}")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _serialize_requirement(self, req: Requirement) -> Dict[str, Any]:
        """Serialize requirement for validation."""
        return {
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "type": req.type.value,
            "priority": req.priority.value,
            "risk_level": req.risk_level,
            "acceptance_criteria": req.acceptance_criteria,
            "stakeholders": req.stakeholders,
            "dependencies": req.dependencies,
            "compliance_standards": [std.value for std in req.compliance_standards],
            "tags": req.tags
        }
    
    def _serialize_test_case(self, tc: TestCase) -> Dict[str, Any]:
        """Serialize test case for validation."""
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
            "risk_level": tc.risk_level,
            "compliance_standards": [std.value for std in tc.compliance_standards],
            "traceability_matrix": tc.traceability_matrix
        }
    
    def _serialize_compliance_mapping(self, cm: ComplianceMapping) -> Dict[str, Any]:
        """Serialize compliance mapping for validation."""
        return {
            "requirement_id": cm.requirement_id,
            "standard": cm.standard.value,
            "applicable_sections": cm.applicable_sections,
            "compliance_level": cm.compliance_level,
            "evidence": cm.evidence,
            "gaps": cm.gaps,
            "recommendations": cm.recommendations
        }


# Export the main validator class
__all__ = ["QualityValidator"]
