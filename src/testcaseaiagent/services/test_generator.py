"""
Test case generation service for healthcare requirements.
"""

import json
import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models import Requirement, TestCase, TestCaseType, TestCasePriority
from ..core.config import settings

logger = logging.getLogger(__name__)


class TestGenerator:
    """Generates test cases from healthcare requirements."""
    
    def __init__(self):
        """Initialize the test generator."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            google_api_key=settings.google_api_key
        )
    
    def generate_test_cases(
        self, 
        requirements: List[Requirement], 
        compliance_mappings: List[Dict[str, Any]]
    ) -> List[TestCase]:
        """
        Generate test cases from requirements.
        
        Args:
            requirements: List of requirements
            compliance_mappings: List of compliance mappings
            
        Returns:
            List of generated test cases
        """
        logger.info("Starting test case generation")
        test_cases = []
        
        try:
            for requirement in requirements:
                # Generate test cases for each requirement
                requirement_tests = self._generate_requirement_test_cases(requirement)
                test_cases.extend(requirement_tests)
            
            logger.info(f"Successfully generated {len(test_cases)} test cases")
            return test_cases
            
        except Exception as e:
            logger.error(f"Test generation failed: {str(e)}")
            # Return fallback test cases
            return self._create_fallback_test_cases(requirements)
    
    def _generate_requirement_test_cases(self, requirement: Requirement) -> List[TestCase]:
        """Generate test cases for a single requirement."""
        test_cases = []
        
        # Generate positive test case
        positive_test = self._create_positive_test_case(requirement)
        test_cases.append(positive_test)
        
        # Generate negative test case if enabled
        if settings.include_negative_test_cases:
            negative_test = self._create_negative_test_case(requirement)
            test_cases.append(negative_test)
        
        # Generate boundary test case if enabled
        if settings.include_boundary_test_cases:
            boundary_test = self._create_boundary_test_case(requirement)
            test_cases.append(boundary_test)
        
        # Generate security test case if enabled and applicable
        if settings.include_security_test_cases and self._is_security_related(requirement):
            security_test = self._create_security_test_case(requirement)
            test_cases.append(security_test)
        
        return test_cases
    
    def _create_positive_test_case(self, requirement: Requirement) -> TestCase:
        """Create a positive test case for a requirement."""
        test_id = f"TC_{requirement.id}_POS_001"
        
        return TestCase(
            id=test_id,
            title=f"Verify {requirement.title} - Positive Scenario",
            description=f"Test that {requirement.description} works correctly under normal conditions",
            test_type=TestCaseType.FUNCTIONAL,
            priority=self._determine_priority(requirement),
            requirement_id=requirement.id,
            test_steps=[
                f"1. Prepare test environment for {requirement.title}",
                f"2. Execute {requirement.description} with valid inputs",
                "3. Verify the system responds correctly",
                "4. Confirm all expected outputs are generated",
                "5. Validate system state after execution"
            ],
            expected_results=[
                f"System successfully implements {requirement.title}",
                "All expected outputs are generated",
                "No errors or exceptions occur",
                "System state is consistent and valid"
            ],
            preconditions=[
                "System is in a known good state",
                "All required data is available",
                "User has appropriate permissions"
            ],
            postconditions=[
                "System maintains data integrity",
                "All changes are properly logged",
                "System returns to stable state"
            ],
            compliance_standards=requirement.compliance_standards
        )
    
    def _create_negative_test_case(self, requirement: Requirement) -> TestCase:
        """Create a negative test case for a requirement."""
        test_id = f"TC_{requirement.id}_NEG_001"
        
        return TestCase(
            id=test_id,
            title=f"Verify {requirement.title} - Negative Scenario",
            description=f"Test that {requirement.description} handles invalid inputs gracefully",
            test_type=TestCaseType.FUNCTIONAL,
            priority=self._determine_priority(requirement),
            requirement_id=requirement.id,
            test_steps=[
                f"1. Prepare test environment for {requirement.title}",
                f"2. Execute {requirement.description} with invalid inputs",
                "3. Verify the system handles errors appropriately",
                "4. Confirm appropriate error messages are displayed",
                "5. Validate system remains stable"
            ],
            expected_results=[
                "System rejects invalid inputs",
                "Appropriate error messages are displayed",
                "System does not crash or become unstable",
                "Data integrity is maintained"
            ],
            preconditions=[
                "System is in a known good state",
                "Invalid test data is prepared"
            ],
            postconditions=[
                "System maintains data integrity",
                "Error conditions are properly logged",
                "System returns to stable state"
            ],
            compliance_standards=requirement.compliance_standards
        )
    
    def _create_boundary_test_case(self, requirement: Requirement) -> TestCase:
        """Create a boundary test case for a requirement."""
        test_id = f"TC_{requirement.id}_BND_001"
        
        return TestCase(
            id=test_id,
            title=f"Verify {requirement.title} - Boundary Conditions",
            description=f"Test {requirement.description} at boundary limits",
            test_type=TestCaseType.FUNCTIONAL,
            priority=self._determine_priority(requirement),
            requirement_id=requirement.id,
            test_steps=[
                f"1. Prepare test environment for {requirement.title}",
                f"2. Test {requirement.description} with minimum valid values",
                f"3. Test {requirement.description} with maximum valid values",
                "4. Verify system behavior at boundaries",
                "5. Test edge cases and limits"
            ],
            expected_results=[
                "System handles minimum values correctly",
                "System handles maximum values correctly",
                "Boundary conditions are properly validated",
                "System maintains performance at limits"
            ],
            preconditions=[
                "System is in a known good state",
                "Boundary test data is prepared"
            ],
            postconditions=[
                "System maintains data integrity",
                "Performance remains acceptable",
                "System returns to stable state"
            ],
            compliance_standards=requirement.compliance_standards
        )
    
    def _create_security_test_case(self, requirement: Requirement) -> TestCase:
        """Create a security test case for a requirement."""
        test_id = f"TC_{requirement.id}_SEC_001"
        
        return TestCase(
            id=test_id,
            title=f"Verify {requirement.title} - Security",
            description=f"Test security aspects of {requirement.description}",
            test_type=TestCaseType.SECURITY,
            priority=TestCasePriority.HIGH,
            requirement_id=requirement.id,
            test_steps=[
                f"1. Prepare test environment for {requirement.title}",
                f"2. Test {requirement.description} with unauthorized access attempts",
                "3. Verify authentication and authorization controls",
                "4. Test for common security vulnerabilities",
                "5. Validate security logging and monitoring"
            ],
            expected_results=[
                "Unauthorized access is properly denied",
                "Authentication controls work correctly",
                "Security vulnerabilities are not present",
                "Security events are properly logged"
            ],
            preconditions=[
                "System is in a known good state",
                "Security test scenarios are prepared"
            ],
            postconditions=[
                "System maintains security posture",
                "Security events are properly recorded",
                "System returns to secure state"
            ],
            compliance_standards=requirement.compliance_standards
        )
    
    def _determine_priority(self, requirement: Requirement) -> TestCasePriority:
        """Determine test case priority based on requirement priority."""
        priority_mapping = {
            TestCasePriority.CRITICAL: TestCasePriority.CRITICAL,
            TestCasePriority.HIGH: TestCasePriority.HIGH,
            TestCasePriority.MEDIUM: TestCasePriority.MEDIUM,
            TestCasePriority.LOW: TestCasePriority.LOW
        }
        
        return priority_mapping.get(requirement.priority, TestCasePriority.MEDIUM)
    
    def _is_security_related(self, requirement: Requirement) -> bool:
        """Check if a requirement is security-related."""
        security_keywords = [
            "security", "authentication", "authorization", "access", "login",
            "password", "encryption", "data protection", "privacy", "audit"
        ]
        
        requirement_text = f"{requirement.title} {requirement.description}".lower()
        return any(keyword in requirement_text for keyword in security_keywords)
    
    def _create_fallback_test_cases(self, requirements: List[Requirement]) -> List[TestCase]:
        """Create fallback test cases when AI generation fails."""
        logger.info("Using fallback test case generation method")
        test_cases = []
        
        for requirement in requirements:
            # Create basic positive test case
            test_case = TestCase(
                id=f"TC_{requirement.id}_001",
                title=f"Basic test for {requirement.title}",
                description=f"Basic test case for {requirement.description}",
                test_type=TestCaseType.FUNCTIONAL,
                priority=requirement.priority,
                requirement_id=requirement.id,
                test_steps=[
                    "1. Prepare test environment",
                    "2. Execute test scenario",
                    "3. Verify results"
                ],
                expected_results=[
                    "Test passes successfully"
                ],
                compliance_standards=requirement.compliance_standards
            )
            test_cases.append(test_case)
        
        return test_cases
