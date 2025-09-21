"""
Quality validation service for generated test cases.
"""

import logging
from typing import List, Dict, Any
from ..models import QualityMetrics, Requirement, TestCase

logger = logging.getLogger(__name__)


class QualityValidator:
    """Validates quality of generated test cases."""
    
    def __init__(self):
        """Initialize the quality validator."""
        pass
    
    def validate_quality(self, state) -> Any:
        """
        Validate quality of generated test cases.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with quality metrics
        """
        logger.info("Starting quality validation")
        
        try:
            # Calculate quality metrics
            metrics = self._calculate_quality_metrics(
                state.extracted_requirements,
                state.generated_test_cases,
                state.compliance_mappings
            )
            
            state.quality_metrics = metrics
            logger.info(f"Quality validation completed with overall score: {metrics.completeness_score}")
            return state
            
        except Exception as e:
            logger.error(f"Quality validation failed: {str(e)}")
            state.error_log.append(f"Quality validation failed: {str(e)}")
            return state
    
    def _calculate_quality_metrics(
        self, 
        requirements: List[Requirement], 
        test_cases: List[TestCase], 
        compliance_mappings: List[Dict[str, Any]]
    ) -> QualityMetrics:
        """Calculate quality metrics for the generated content."""
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(requirements, test_cases)
        
        # Calculate accuracy score
        accuracy_score = self._calculate_accuracy_score(test_cases)
        
        # Calculate traceability score
        traceability_score = self._calculate_traceability_score(requirements, test_cases)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(requirements, compliance_mappings)
        
        # Calculate coverage percentage
        coverage_percentage = self._calculate_coverage_percentage(requirements, test_cases)
        
        # Calculate averages
        total_requirements = len(requirements)
        total_test_cases = len(test_cases)
        avg_test_cases_per_requirement = (
            total_test_cases / total_requirements if total_requirements > 0 else 0.0
        )
        
        return QualityMetrics(
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            traceability_score=traceability_score,
            compliance_score=compliance_score,
            coverage_percentage=coverage_percentage,
            total_requirements=total_requirements,
            total_test_cases=total_test_cases,
            average_test_cases_per_requirement=avg_test_cases_per_requirement
        )
    
    def _calculate_completeness_score(self, requirements: List[Requirement], test_cases: List[TestCase]) -> float:
        """Calculate completeness score based on requirement coverage."""
        if not requirements:
            return 0.0
        
        # Check how many requirements have associated test cases
        requirements_with_tests = set(tc.requirement_id for tc in test_cases)
        covered_requirements = len(requirements_with_tests)
        
        return min(covered_requirements / len(requirements), 1.0)
    
    def _calculate_accuracy_score(self, test_cases: List[TestCase]) -> float:
        """Calculate accuracy score based on test case quality."""
        if not test_cases:
            return 0.0
        
        # Simple accuracy scoring based on test case completeness
        total_score = 0.0
        
        for test_case in test_cases:
            score = 0.0
            
            # Check if test case has required fields
            if test_case.title:
                score += 0.2
            if test_case.description:
                score += 0.2
            if test_case.test_steps:
                score += 0.3
            if test_case.expected_results:
                score += 0.3
            
            total_score += score
        
        return total_score / len(test_cases)
    
    def _calculate_traceability_score(self, requirements: List[Requirement], test_cases: List[TestCase]) -> float:
        """Calculate traceability score."""
        if not requirements or not test_cases:
            return 0.0
        
        # Check if all test cases have valid requirement IDs
        valid_requirement_ids = set(req.id for req in requirements)
        traced_test_cases = sum(
            1 for tc in test_cases if tc.requirement_id in valid_requirement_ids
        )
        
        return traced_test_cases / len(test_cases)
    
    def _calculate_compliance_score(self, requirements: List[Requirement], compliance_mappings: List[Dict[str, Any]]) -> float:
        """Calculate compliance coverage score."""
        if not requirements:
            return 0.0
        
        # Check how many requirements have compliance mappings
        mapped_requirements = set(mapping.get("requirement_id") for mapping in compliance_mappings)
        covered_requirements = len(mapped_requirements)
        
        return min(covered_requirements / len(requirements), 1.0)
    
    def _calculate_coverage_percentage(self, requirements: List[Requirement], test_cases: List[TestCase]) -> float:
        """Calculate overall coverage percentage."""
        if not requirements:
            return 0.0
        
        # Simple coverage calculation
        requirements_with_tests = set(tc.requirement_id for tc in test_cases)
        covered_count = len(requirements_with_tests)
        
        return (covered_count / len(requirements)) * 100.0
