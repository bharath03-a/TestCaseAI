"""
Test case generation module using Gemini for healthcare requirements.
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
    Requirement, TestCase, TestCaseType, TestCasePriority, ComplianceStandard,
    GraphState, ProcessingStatus, WorkflowStep
)
from config import settings, HealthcareDomainConfig

logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """Generate test cases from healthcare requirements using Gemini AI."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            top_p=settings.gemini_top_p,
            top_k=settings.gemini_top_k,
            google_api_key=settings.google_api_key
        )
        
        # Initialize test case templates
        self._setup_test_templates()
        self._setup_prompts()
    
    def _setup_test_templates(self):
        """Setup test case templates for different types."""
        self.test_templates = {
            TestCaseType.FUNCTIONAL: {
                "positive": [
                    "Verify that the system correctly {function} when {condition}",
                    "Validate that {feature} operates as expected with {input}",
                    "Confirm that {process} completes successfully under {scenario}",
                    "Test that {component} responds appropriately to {stimulus}",
                    "Ensure that {operation} produces the expected {output}"
                ],
                "negative": [
                    "Verify that the system handles {error_condition} gracefully",
                    "Validate that {feature} rejects {invalid_input} appropriately",
                    "Confirm that {process} fails safely when {failure_condition}",
                    "Test that {component} prevents {unauthorized_action}",
                    "Ensure that {operation} maintains data integrity during {error_state}"
                ],
                "boundary": [
                    "Test {feature} behavior at the minimum {parameter} value",
                    "Test {feature} behavior at the maximum {parameter} value",
                    "Verify {operation} handles {boundary_condition} correctly",
                    "Validate {component} response at {edge_case} boundary"
                ]
            },
            TestCaseType.SECURITY: [
                "Verify that {sensitive_data} is properly encrypted during {operation}",
                "Validate that access to {resource} is restricted to {authorized_users}",
                "Confirm that {audit_trail} is maintained for {security_event}",
                "Test that {authentication} mechanism prevents {unauthorized_access}",
                "Ensure that {data_transmission} uses secure protocols"
            ],
            TestCaseType.COMPLIANCE: [
                "Verify that {process} complies with {standard} requirements",
                "Validate that {data_handling} meets {regulation} standards",
                "Confirm that {documentation} is maintained per {compliance_requirement}",
                "Test that {audit_log} captures all required {compliance_events}",
                "Ensure that {data_retention} follows {regulatory_guidelines}"
            ],
            TestCaseType.PERFORMANCE: [
                "Verify that {operation} completes within {time_limit} under {load_condition}",
                "Test {system} response time with {concurrent_users} users",
                "Validate {throughput} meets {performance_requirement}",
                "Confirm {resource_usage} stays within {acceptable_limits}",
                "Test {scalability} under {stress_condition}"
            ],
            TestCaseType.INTEGRATION: [
                "Verify that {component_a} integrates correctly with {component_b}",
                "Test {data_flow} between {system_a} and {system_b}",
                "Validate {api_interface} handles {integration_scenarios}",
                "Confirm {error_handling} works across {system_boundaries}",
                "Test {synchronization} between {distributed_components}"
            ],
            TestCaseType.USABILITY: [
                "Verify that {user_interface} is intuitive for {user_type}",
                "Test {workflow} efficiency for {typical_user_tasks}",
                "Validate {accessibility} features for {user_with_disabilities}",
                "Confirm {error_messages} are clear and actionable",
                "Test {navigation} supports {user_goals} effectively"
            ]
        }
    
    def _setup_prompts(self):
        """Setup prompt templates for test case generation."""
        
        # System prompt for test case generation
        self.system_prompt = SystemMessagePromptTemplate.from_template("""
You are an expert healthcare software test engineer with deep knowledge of:
- Healthcare software testing methodologies
- Medical device software validation (IEC 62304)
- FDA software validation guidelines
- Healthcare data privacy and security testing
- Clinical workflow testing
- Risk-based testing approaches

Your task is to generate comprehensive test cases from healthcare software requirements.

Key principles:
1. Generate both positive and negative test scenarios
2. Include boundary value testing
3. Consider patient safety implications
4. Address data privacy and security
5. Ensure regulatory compliance
6. Include edge cases and error conditions
7. Provide clear test steps and expected results
8. Consider different user roles and permissions
9. Include performance and scalability testing
10. Address integration points

Test case types to generate:
- Functional tests (positive, negative, boundary)
- Security tests (authentication, authorization, data protection)
- Compliance tests (regulatory standards, audit trails)
- Performance tests (response time, throughput, scalability)
- Integration tests (system interfaces, data flow)
- Usability tests (user experience, accessibility)

Output format: JSON with structured test case objects.
""")
        
        # Human prompt template
        self.human_prompt = HumanMessagePromptTemplate.from_template("""
Please generate comprehensive test cases for the following healthcare software requirements:

Requirements:
{requirements_json}

Compliance Mappings:
{compliance_mappings_json}

Generate test cases and return them in the following JSON format:
{{
    "test_cases": [
        {{
            "id": "TC-001",
            "title": "Test Case Title",
            "description": "Test case description",
            "type": "functional|integration|system|acceptance|performance|security|usability|compliance",
            "priority": "critical|high|medium|low",
            "requirement_ids": ["REQ-001", "REQ-002"],
            "preconditions": ["precondition1", "precondition2"],
            "test_steps": ["step1", "step2", "step3"],
            "expected_results": ["result1", "result2"],
            "test_data": {{
                "input_data": "sample input",
                "expected_output": "expected output",
                "test_environment": "test environment details"
            }},
            "automation_status": "manual|automated|semi_automated",
            "estimated_duration": 30,
            "risk_level": "low|medium|high|critical",
            "compliance_standards": ["fda", "iec_62304"],
            "traceability_matrix": {{
                "requirement_id": "REQ-001",
                "test_coverage": "100%"
            }}
        }}
    ],
    "test_generation_summary": {{
        "total_test_cases": 25,
        "functional_tests": 15,
        "security_tests": 5,
        "compliance_tests": 3,
        "performance_tests": 2,
        "estimated_total_duration": 1200,
        "automation_coverage": "60%"
    }}
}}

Focus on:
1. Patient safety test scenarios
2. Data privacy and security testing
3. Regulatory compliance validation
4. System reliability and performance
5. User interface and usability
6. Integration and interoperability
7. Error handling and recovery
8. Audit trail and traceability
9. Scalability and load testing
10. Edge cases and boundary conditions
""")
        
        # Create the chat prompt template
        self.chat_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])
    
    def generate_test_cases(self, state: GraphState) -> GraphState:
        """
        Generate test cases from requirements and compliance mappings.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with generated test cases
        """
        logger.info("Starting test case generation")
        
        # Create workflow step
        step = WorkflowStep(
            step_name="test_generator",
            status=ProcessingStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        state.workflow_steps.append(step)
        state.current_step = "test_generator"
        
        try:
            if not state.extracted_requirements:
                logger.warning("No requirements found for test case generation")
                state.overall_status = ProcessingStatus.FAILED
                step.status = ProcessingStatus.FAILED
                step.error_message = "No requirements available for test case generation"
                return state
            
            # Generate test cases
            test_cases = self._generate_from_requirements(
                state.extracted_requirements, 
                state.compliance_mappings
            )
            
            # Post-process and validate test cases
            validated_test_cases = self._validate_and_enhance_test_cases(test_cases)
            
            # Update state
            state.generated_test_cases = validated_test_cases
            state.overall_status = ProcessingStatus.COMPLETED if validated_test_cases else ProcessingStatus.FAILED
            
            # Update workflow step
            step.status = ProcessingStatus.COMPLETED
            step.end_time = datetime.now()
            step.duration_seconds = (step.end_time - step.start_time).total_seconds()
            step.output_data = {
                "generated_test_cases_count": len(validated_test_cases),
                "test_types": self._calculate_test_types(validated_test_cases),
                "automation_coverage": self._calculate_automation_coverage(validated_test_cases)
            }
            
            logger.info(f"Successfully generated {len(validated_test_cases)} test cases")
            
        except Exception as e:
            error_msg = f"Test case generation failed: {str(e)}"
            logger.error(error_msg)
            state.error_log.append(error_msg)
            state.overall_status = ProcessingStatus.FAILED
            
            step.status = ProcessingStatus.FAILED
            step.end_time = datetime.now()
            step.error_message = error_msg
        
        return state
    
    def _generate_from_requirements(self, requirements: List[Requirement], 
                                  compliance_mappings: List[Any]) -> List[TestCase]:
        """Generate test cases from requirements using Gemini."""
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
                    "acceptance_criteria": req.acceptance_criteria,
                    "compliance_standards": [std.value for std in req.compliance_standards],
                    "tags": req.tags
                }
                requirements_data.append(req_data)
            
            # Prepare compliance mappings data
            compliance_data = []
            for mapping in compliance_mappings:
                comp_data = {
                    "requirement_id": mapping.requirement_id,
                    "standard": mapping.standard.value,
                    "compliance_level": mapping.compliance_level,
                    "applicable_sections": mapping.applicable_sections
                }
                compliance_data.append(comp_data)
            
            # Prepare the prompt
            messages = self.chat_prompt.format_messages(
                requirements_json=json.dumps(requirements_data, indent=2),
                compliance_mappings_json=json.dumps(compliance_data, indent=2)
            )
            
            # Get response from Gemini
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Parse the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in response, using fallback generation")
                return self._fallback_test_generation(requirements, compliance_mappings)
            
            json_str = json_match.group()
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {str(e)}, using fallback generation")
                return self._fallback_test_generation(requirements, compliance_mappings)
            
            # Convert to TestCase objects
            test_cases = []
            for tc_data in parsed_data.get('test_cases', []):
                try:
                    test_case = self._create_test_case_object(tc_data)
                    if test_case:
                        test_cases.append(test_case)
                except Exception as e:
                    logger.warning(f"Failed to create test case object: {str(e)}")
                    continue
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Failed to generate test cases: {str(e)}")
            return self._fallback_test_generation(requirements, compliance_mappings)
    
    def _create_test_case_object(self, tc_data: Dict[str, Any]) -> Optional[TestCase]:
        """Create a TestCase object from extracted data."""
        try:
            # Generate unique ID if not provided
            tc_id = tc_data.get('id', f"TC-{uuid.uuid4().hex[:8].upper()}")
            
            # Map string values to enums
            tc_type = self._map_test_case_type(tc_data.get('type', 'functional'))
            priority = self._map_priority(tc_data.get('priority', 'medium'))
            risk_level = tc_data.get('risk_level', 'medium')
            
            # Map compliance standards
            compliance_standards = []
            for std in tc_data.get('compliance_standards', []):
                try:
                    compliance_standards.append(ComplianceStandard(std.lower()))
                except ValueError:
                    logger.warning(f"Unknown compliance standard: {std}")
            
            # Create test case object
            test_case = TestCase(
                id=tc_id,
                title=tc_data.get('title', 'Untitled Test Case'),
                description=tc_data.get('description', ''),
                type=tc_type,
                priority=priority,
                requirement_ids=tc_data.get('requirement_ids', []),
                preconditions=tc_data.get('preconditions', []),
                test_steps=tc_data.get('test_steps', []),
                expected_results=tc_data.get('expected_results', []),
                test_data=tc_data.get('test_data', {}),
                automation_status=tc_data.get('automation_status', 'manual'),
                estimated_duration=tc_data.get('estimated_duration'),
                risk_level=risk_level,
                compliance_standards=compliance_standards,
                traceability_matrix=tc_data.get('traceability_matrix', {})
            )
            
            return test_case
            
        except Exception as e:
            logger.error(f"Failed to create test case object: {str(e)}")
            return None
    
    def _map_test_case_type(self, type_str: str) -> TestCaseType:
        """Map string to TestCaseType enum."""
        type_mapping = {
            'functional': TestCaseType.FUNCTIONAL,
            'integration': TestCaseType.INTEGRATION,
            'system': TestCaseType.SYSTEM,
            'acceptance': TestCaseType.ACCEPTANCE,
            'performance': TestCaseType.PERFORMANCE,
            'security': TestCaseType.SECURITY,
            'usability': TestCaseType.USABILITY,
            'compliance': TestCaseType.COMPLIANCE
        }
        return type_mapping.get(type_str.lower(), TestCaseType.FUNCTIONAL)
    
    def _map_priority(self, priority_str: str) -> TestCasePriority:
        """Map string to TestCasePriority enum."""
        priority_mapping = {
            'critical': TestCasePriority.CRITICAL,
            'high': TestCasePriority.HIGH,
            'medium': TestCasePriority.MEDIUM,
            'low': TestCasePriority.LOW
        }
        return priority_mapping.get(priority_str.lower(), TestCasePriority.MEDIUM)
    
    def _fallback_test_generation(self, requirements: List[Requirement], 
                                compliance_mappings: List[Any]) -> List[TestCase]:
        """Fallback test case generation using templates and rules."""
        logger.info("Using fallback test case generation method")
        
        test_cases = []
        
        for req in requirements:
            # Generate different types of test cases for each requirement
            req_test_cases = self._generate_requirement_test_cases(req, compliance_mappings)
            test_cases.extend(req_test_cases)
        
        return test_cases
    
    def _generate_requirement_test_cases(self, requirement: Requirement, 
                                       compliance_mappings: List[Any]) -> List[TestCase]:
        """Generate test cases for a specific requirement."""
        test_cases = []
        
        # Get compliance mappings for this requirement
        req_mappings = [m for m in compliance_mappings if m.requirement_id == requirement.id]
        
        # Generate functional test cases
        functional_tests = self._generate_functional_tests(requirement)
        test_cases.extend(functional_tests)
        
        # Generate security test cases if applicable
        if requirement.type.value == 'security' or any('security' in tag.lower() for tag in requirement.tags):
            security_tests = self._generate_security_tests(requirement)
            test_cases.extend(security_tests)
        
        # Generate compliance test cases
        if req_mappings:
            compliance_tests = self._generate_compliance_tests(requirement, req_mappings)
            test_cases.extend(compliance_tests)
        
        # Generate performance test cases if applicable
        if requirement.type.value == 'performance' or any('performance' in tag.lower() for tag in requirement.tags):
            performance_tests = self._generate_performance_tests(requirement)
            test_cases.extend(performance_tests)
        
        return test_cases
    
    def _generate_functional_tests(self, requirement: Requirement) -> List[TestCase]:
        """Generate functional test cases."""
        test_cases = []
        
        # Positive test case
        positive_tc = TestCase(
            id=f"TC-{uuid.uuid4().hex[:8].upper()}",
            title=f"Positive Test: {requirement.title}",
            description=f"Verify that {requirement.description} works correctly under normal conditions",
            type=TestCaseType.FUNCTIONAL,
            priority=requirement.priority,
            requirement_ids=[requirement.id],
            preconditions=["System is in normal operating state", "Required data is available"],
            test_steps=[
                f"Navigate to the {requirement.title} functionality",
                f"Execute the {requirement.title} operation",
                "Verify the operation completes successfully",
                "Validate the results meet acceptance criteria"
            ],
            expected_results=[
                "Operation completes without errors",
                "Results match expected output",
                "System remains stable",
                "All acceptance criteria are met"
            ],
            test_data={"input_data": "Valid test data", "expected_output": "Expected results"},
            automation_status="manual",
            estimated_duration=30,
            risk_level=requirement.risk_level,
            compliance_standards=requirement.compliance_standards
        )
        test_cases.append(positive_tc)
        
        # Negative test case
        negative_tc = TestCase(
            id=f"TC-{uuid.uuid4().hex[:8].upper()}",
            title=f"Negative Test: {requirement.title}",
            description=f"Verify that {requirement.description} handles error conditions gracefully",
            type=TestCaseType.FUNCTIONAL,
            priority=requirement.priority,
            requirement_ids=[requirement.id],
            preconditions=["System is in normal operating state"],
            test_steps=[
                f"Navigate to the {requirement.title} functionality",
                "Provide invalid or incomplete input data",
                f"Execute the {requirement.title} operation",
                "Verify error handling behavior"
            ],
            expected_results=[
                "System displays appropriate error message",
                "No data corruption occurs",
                "System remains stable",
                "User can recover from error state"
            ],
            test_data={"input_data": "Invalid test data", "expected_output": "Error message"},
            automation_status="manual",
            estimated_duration=20,
            risk_level=requirement.risk_level,
            compliance_standards=requirement.compliance_standards
        )
        test_cases.append(negative_tc)
        
        return test_cases
    
    def _generate_security_tests(self, requirement: Requirement) -> List[TestCase]:
        """Generate security test cases."""
        test_cases = []
        
        # Authentication test
        auth_tc = TestCase(
            id=f"TC-{uuid.uuid4().hex[:8].upper()}",
            title=f"Security Test: Authentication for {requirement.title}",
            description=f"Verify that {requirement.title} requires proper authentication",
            type=TestCaseType.SECURITY,
            priority=TestCasePriority.HIGH,
            requirement_ids=[requirement.id],
            preconditions=["User is not authenticated"],
            test_steps=[
                f"Attempt to access {requirement.title} without authentication",
                "Verify authentication is required",
                "Provide valid credentials",
                "Verify access is granted"
            ],
            expected_results=[
                "Access is denied without authentication",
                "Authentication prompt is displayed",
                "Access is granted with valid credentials",
                "Session is properly established"
            ],
            test_data={"credentials": "Valid user credentials"},
            automation_status="semi_automated",
            estimated_duration=15,
            risk_level="high",
            compliance_standards=[ComplianceStandard.ISO_27001, ComplianceStandard.HIPAA]
        )
        test_cases.append(auth_tc)
        
        return test_cases
    
    def _generate_compliance_tests(self, requirement: Requirement, 
                                 compliance_mappings: List[Any]) -> List[TestCase]:
        """Generate compliance test cases."""
        test_cases = []
        
        for mapping in compliance_mappings:
            compliance_tc = TestCase(
                id=f"TC-{uuid.uuid4().hex[:8].upper()}",
                title=f"Compliance Test: {mapping.standard.value} for {requirement.title}",
                description=f"Verify that {requirement.title} complies with {mapping.standard.value} requirements",
                type=TestCaseType.COMPLIANCE,
                priority=TestCasePriority.HIGH,
                requirement_ids=[requirement.id],
                preconditions=["System is configured for compliance testing"],
                test_steps=[
                    f"Execute {requirement.title} functionality",
                    f"Verify compliance with {mapping.standard.value} sections: {', '.join(mapping.applicable_sections[:3])}",
                    "Check audit trail generation",
                    "Validate documentation requirements"
                ],
                expected_results=[
                    f"Functionality complies with {mapping.standard.value}",
                    "Audit trail is properly generated",
                    "Documentation requirements are met",
                    "No compliance violations detected"
                ],
                test_data={"compliance_standard": mapping.standard.value},
                automation_status="manual",
                estimated_duration=45,
                risk_level="high",
                compliance_standards=[mapping.standard]
            )
            test_cases.append(compliance_tc)
        
        return test_cases
    
    def _generate_performance_tests(self, requirement: Requirement) -> List[TestCase]:
        """Generate performance test cases."""
        test_cases = []
        
        performance_tc = TestCase(
            id=f"TC-{uuid.uuid4().hex[:8].upper()}",
            title=f"Performance Test: {requirement.title}",
            description=f"Verify that {requirement.title} meets performance requirements",
            type=TestCaseType.PERFORMANCE,
            priority=requirement.priority,
            requirement_ids=[requirement.id],
            preconditions=["Performance testing environment is set up"],
            test_steps=[
                f"Execute {requirement.title} under normal load",
                "Measure response time and throughput",
                "Execute under increased load",
                "Verify performance degradation is acceptable"
            ],
            expected_results=[
                "Response time meets requirements",
                "Throughput meets specifications",
                "System remains stable under load",
                "Performance degradation is within acceptable limits"
            ],
            test_data={"load_levels": "Normal, 2x, 5x normal load"},
            automation_status="automated",
            estimated_duration=60,
            risk_level=requirement.risk_level,
            compliance_standards=requirement.compliance_standards
        )
        test_cases.append(performance_tc)
        
        return test_cases
    
    def _validate_and_enhance_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Validate and enhance generated test cases."""
        validated_test_cases = []
        
        for tc in test_cases:
            # Basic validation
            if not tc.title or not tc.test_steps or not tc.expected_results:
                continue
            
            # Enhance with additional information
            tc = self._enhance_test_case(tc)
            
            # Add to validated list
            validated_test_cases.append(tc)
        
        # Remove duplicates based on title similarity
        validated_test_cases = self._remove_duplicate_test_cases(validated_test_cases)
        
        return validated_test_cases
    
    def _enhance_test_case(self, test_case: TestCase) -> TestCase:
        """Enhance test case with additional information."""
        # Add healthcare-specific test data if not present
        if not test_case.test_data:
            test_case.test_data = {
                "patient_data": "Sample patient information",
                "medical_records": "Sample medical records",
                "test_environment": "Healthcare test environment"
            }
        
        # Estimate duration if not provided
        if not test_case.estimated_duration:
            test_case.estimated_duration = self._estimate_test_duration(test_case)
        
        # Add traceability information
        if not test_case.traceability_matrix:
            test_case.traceability_matrix = {
                "requirement_id": test_case.requirement_ids[0] if test_case.requirement_ids else "",
                "test_coverage": "100%",
                "compliance_standards": [std.value for std in test_case.compliance_standards]
            }
        
        return test_case
    
    def _estimate_test_duration(self, test_case: TestCase) -> int:
        """Estimate test case duration in minutes."""
        base_duration = 15  # Base minutes
        
        # Adjust based on test type
        type_multiplier = {
            TestCaseType.FUNCTIONAL: 1.0,
            TestCaseType.INTEGRATION: 1.5,
            TestCaseType.SYSTEM: 2.0,
            TestCaseType.ACCEPTANCE: 1.2,
            TestCaseType.PERFORMANCE: 3.0,
            TestCaseType.SECURITY: 2.5,
            TestCaseType.USABILITY: 1.8,
            TestCaseType.COMPLIANCE: 2.0
        }
        
        # Adjust based on automation status
        automation_multiplier = {
            "manual": 1.0,
            "semi_automated": 0.7,
            "automated": 0.3
        }
        
        # Adjust based on risk level
        risk_multiplier = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.5,
            "critical": 2.0
        }
        
        duration = base_duration
        duration *= type_multiplier.get(test_case.type, 1.0)
        duration *= automation_multiplier.get(test_case.automation_status, 1.0)
        duration *= risk_multiplier.get(test_case.risk_level, 1.0)
        
        return max(5, int(duration))
    
    def _remove_duplicate_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Remove duplicate test cases based on title similarity."""
        unique_test_cases = []
        
        for tc in test_cases:
            is_duplicate = False
            for existing_tc in unique_test_cases:
                # Simple similarity check based on title
                similarity = self._calculate_similarity(tc.title, existing_tc.title)
                if similarity > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_test_cases.append(tc)
        
        return unique_test_cases
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _calculate_test_types(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """Calculate distribution of test case types."""
        types = {}
        for tc in test_cases:
            tc_type = tc.type.value
            types[tc_type] = types.get(tc_type, 0) + 1
        return types
    
    def _calculate_automation_coverage(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """Calculate automation coverage statistics."""
        coverage = {"manual": 0, "semi_automated": 0, "automated": 0}
        for tc in test_cases:
            status = tc.automation_status
            coverage[status] = coverage.get(status, 0) + 1
        return coverage


# Export the main generator class
__all__ = ["TestCaseGenerator"]
