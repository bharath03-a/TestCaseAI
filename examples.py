"""
Example usage and test scenarios for the healthcare test case generation system.
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime

from workflow import HealthcareTestCaseGenerator
from models import ComplianceStandard, DocumentType


class HealthcareTestCaseExamples:
    """Example usage scenarios for the healthcare test case generation system."""
    
    def __init__(self):
        self.generator = HealthcareTestCaseGenerator()
    
    def example_1_basic_healthcare_requirements(self):
        """Example 1: Basic healthcare software requirements."""
        print("=" * 60)
        print("EXAMPLE 1: Basic Healthcare Software Requirements")
        print("=" * 60)
        
        documents = [
            {
                "filename": "patient_management_requirements.pdf",
                "content": """
                PATIENT MANAGEMENT SYSTEM REQUIREMENTS
                
                Functional Requirements:
                1. The system shall allow healthcare providers to register new patients with complete demographic information.
                2. The system shall maintain patient medical history including allergies, medications, and previous treatments.
                3. The system shall support appointment scheduling with automatic reminders.
                4. The system shall provide secure access to patient records based on user roles and permissions.
                5. The system shall generate patient reports and summaries for healthcare providers.
                
                Non-Functional Requirements:
                1. The system shall process patient data within 2 seconds of user input.
                2. The system shall maintain 99.9% uptime during business hours.
                3. The system shall support up to 1000 concurrent users.
                4. The system shall encrypt all patient data in transit and at rest.
                5. The system shall maintain audit logs for all data access and modifications.
                
                Security Requirements:
                1. The system shall implement multi-factor authentication for all users.
                2. The system shall comply with HIPAA regulations for patient data protection.
                3. The system shall automatically log out inactive users after 15 minutes.
                4. The system shall encrypt all data transmissions using TLS 1.3.
                5. The system shall implement role-based access control for patient data.
                
                Compliance Requirements:
                1. The system shall comply with FDA 21 CFR Part 820 for medical device software.
                2. The system shall meet IEC 62304 requirements for medical device software lifecycle.
                3. The system shall maintain documentation per ISO 13485 quality management standards.
                4. The system shall implement data protection measures per GDPR requirements.
                """
            }
        ]
        
        result = self.generator.process_documents(
            documents=documents,
            compliance_standards=[
                ComplianceStandard.FDA,
                ComplianceStandard.HIPAA,
                ComplianceStandard.IEC_62304,
                ComplianceStandard.ISO_13485,
                ComplianceStandard.GDPR
            ]
        )
        
        self._print_results(result, "Basic Healthcare Requirements")
    
    def example_2_medical_device_software(self):
        """Example 2: Medical device software requirements."""
        print("=" * 60)
        print("EXAMPLE 2: Medical Device Software Requirements")
        print("=" * 60)
        
        documents = [
            {
                "filename": "medical_device_requirements.docx",
                "content": """
                MEDICAL DEVICE SOFTWARE REQUIREMENTS
                
                System Overview:
                The software controls a patient monitoring device that measures vital signs including heart rate, blood pressure, temperature, and oxygen saturation.
                
                Functional Requirements:
                1. The system shall continuously monitor patient vital signs and display real-time values.
                2. The system shall trigger alarms when vital signs exceed predefined thresholds.
                3. The system shall store patient data for historical analysis and reporting.
                4. The system shall support calibration procedures for all sensors.
                5. The system shall provide data export capabilities for electronic health records.
                
                Safety Requirements:
                1. The system shall implement fail-safe mechanisms to prevent patient harm.
                2. The system shall provide redundant monitoring for critical vital signs.
                3. The system shall maintain backup power supply for continuous operation.
                4. The system shall validate all sensor readings before processing.
                5. The system shall implement emergency shutdown procedures.
                
                Performance Requirements:
                1. The system shall update vital sign displays within 1 second of measurement.
                2. The system shall maintain accuracy within ±2% for all measurements.
                3. The system shall operate continuously for 24 hours without interruption.
                4. The system shall support data logging at 1-second intervals.
                5. The system shall provide real-time trend analysis capabilities.
                
                Regulatory Requirements:
                1. The system shall comply with FDA 510(k) requirements for medical devices.
                2. The system shall meet IEC 60601-1 safety standards for medical electrical equipment.
                3. The system shall implement IEC 62304 software lifecycle processes.
                4. The system shall maintain traceability from requirements to test cases.
                5. The system shall provide comprehensive documentation for regulatory review.
                """
            }
        ]
        
        result = self.generator.process_documents(
            documents=documents,
            compliance_standards=[
                ComplianceStandard.FDA,
                ComplianceStandard.IEC_62304,
                ComplianceStandard.ISO_13485
            ]
        )
        
        self._print_results(result, "Medical Device Software")
    
    def example_3_telemedicine_platform(self):
        """Example 3: Telemedicine platform requirements."""
        print("=" * 60)
        print("EXAMPLE 3: Telemedicine Platform Requirements")
        print("=" * 60)
        
        documents = [
            {
                "filename": "telemedicine_platform_requirements.md",
                "content": """
                # Telemedicine Platform Requirements
                
                ## System Overview
                A comprehensive telemedicine platform enabling remote patient consultations, prescription management, and health monitoring.
                
                ## Core Features
                
                ### Video Consultation
                - The system shall support HD video calls between patients and healthcare providers
                - The system shall provide screen sharing capabilities for medical image review
                - The system shall maintain call quality with minimum 720p resolution
                - The system shall support group consultations with multiple participants
                - The system shall provide call recording with patient consent
                
                ### Patient Portal
                - The system shall allow patients to schedule appointments online
                - The system shall provide access to medical records and test results
                - The system shall support secure messaging with healthcare providers
                - The system shall enable prescription refill requests
                - The system shall provide health education resources
                
                ### Provider Dashboard
                - The system shall display patient schedules and appointment reminders
                - The system shall provide access to patient medical history
                - The system shall support electronic prescription writing
                - The system shall enable documentation of consultation notes
                - The system shall provide billing and insurance integration
                
                ## Security and Privacy
                - The system shall encrypt all communications using end-to-end encryption
                - The system shall comply with HIPAA requirements for patient data protection
                - The system shall implement multi-factor authentication for all users
                - The system shall maintain audit trails for all system activities
                - The system shall support data backup and disaster recovery procedures
                
                ## Integration Requirements
                - The system shall integrate with existing EHR systems
                - The system shall support API connections to pharmacy systems
                - The system shall provide integration with insurance verification systems
                - The system shall support third-party medical device data import
                - The system shall enable integration with laboratory information systems
                """
            }
        ]
        
        result = self.generator.process_documents(
            documents=documents,
            compliance_standards=[
                ComplianceStandard.HIPAA,
                ComplianceStandard.ISO_27001,
                ComplianceStandard.GDPR
            ]
        )
        
        self._print_results(result, "Telemedicine Platform")
    
    def example_4_clinical_decision_support(self):
        """Example 4: Clinical decision support system."""
        print("=" * 60)
        print("EXAMPLE 4: Clinical Decision Support System")
        print("=" * 60)
        
        documents = [
            {
                "filename": "clinical_decision_support.xml",
                "content": """
                <?xml version="1.0" encoding="UTF-8"?>
                <requirements>
                    <system_name>Clinical Decision Support System</system_name>
                    <description>AI-powered system providing clinical recommendations and alerts</description>
                    
                    <functional_requirements>
                        <requirement id="CDS-001">
                            <title>Drug Interaction Checking</title>
                            <description>The system shall check for potential drug interactions when prescribing medications and alert healthcare providers of contraindications.</description>
                            <priority>critical</priority>
                            <acceptance_criteria>
                                <criterion>System identifies known drug interactions within 2 seconds</criterion>
                                <criterion>System provides severity level for each interaction</criterion>
                                <criterion>System suggests alternative medications when appropriate</criterion>
                            </acceptance_criteria>
                        </requirement>
                        
                        <requirement id="CDS-002">
                            <title>Clinical Guidelines Integration</title>
                            <description>The system shall integrate evidence-based clinical guidelines and provide recommendations based on patient conditions.</description>
                            <priority>high</priority>
                            <acceptance_criteria>
                                <criterion>System accesses up-to-date clinical guidelines</criterion>
                                <criterion>System provides personalized recommendations</criterion>
                                <criterion>System explains reasoning behind recommendations</criterion>
                            </acceptance_criteria>
                        </requirement>
                        
                        <requirement id="CDS-003">
                            <title>Risk Assessment</title>
                            <description>The system shall assess patient risk factors and provide early warning alerts for potential complications.</description>
                            <priority>high</priority>
                            <acceptance_criteria>
                                <criterion>System analyzes multiple risk factors simultaneously</criterion>
                                <criterion>System provides risk scores with confidence intervals</criterion>
                                <criterion>System triggers alerts for high-risk patients</criterion>
                            </acceptance_criteria>
                        </requirement>
                    </functional_requirements>
                    
                    <non_functional_requirements>
                        <requirement id="CDS-NF-001">
                            <title>Performance</title>
                            <description>The system shall provide recommendations within 5 seconds of data input.</description>
                        </requirement>
                        
                        <requirement id="CDS-NF-002">
                            <title>Accuracy</title>
                            <description>The system shall maintain recommendation accuracy of at least 95%.</description>
                        </requirement>
                        
                        <requirement id="CDS-NF-003">
                            <title>Availability</title>
                            <description>The system shall maintain 99.9% uptime during business hours.</description>
                        </requirement>
                    </non_functional_requirements>
                    
                    <compliance_requirements>
                        <requirement id="CDS-C-001">
                            <title>FDA Compliance</title>
                            <description>The system shall comply with FDA guidance on clinical decision support software.</description>
                        </requirement>
                        
                        <requirement id="CDS-C-002">
                            <title>Data Privacy</title>
                            <description>The system shall protect patient data according to HIPAA requirements.</description>
                        </requirement>
                    </compliance_requirements>
                </requirements>
                """
            }
        ]
        
        result = self.generator.process_documents(
            documents=documents,
            compliance_standards=[
                ComplianceStandard.FDA,
                ComplianceStandard.HIPAA,
                ComplianceStandard.IEC_62304
            ]
        )
        
        self._print_results(result, "Clinical Decision Support System")
    
    def example_5_multi_document_processing(self):
        """Example 5: Processing multiple documents simultaneously."""
        print("=" * 60)
        print("EXAMPLE 5: Multi-Document Processing")
        print("=" * 60)
        
        documents = [
            {
                "filename": "system_requirements.pdf",
                "content": "The system shall provide secure patient data management with HIPAA compliance."
            },
            {
                "filename": "user_interface_specs.docx",
                "content": "The user interface shall be intuitive and accessible to healthcare providers with varying technical expertise."
            },
            {
                "filename": "integration_requirements.txt",
                "content": "The system shall integrate with existing hospital information systems and electronic health records."
            },
            {
                "filename": "security_requirements.md",
                "content": """
                # Security Requirements
                - Multi-factor authentication required
                - Data encryption in transit and at rest
                - Role-based access control
                - Audit logging for all activities
                - Regular security assessments
                """
            }
        ]
        
        result = self.generator.process_documents(
            documents=documents,
            compliance_standards=[
                ComplianceStandard.HIPAA,
                ComplianceStandard.ISO_27001,
                ComplianceStandard.FDA
            ]
        )
        
        self._print_results(result, "Multi-Document Processing")
    
    def _print_results(self, result: Dict[str, Any], example_name: str):
        """Print formatted results for an example."""
        print(f"\n{example_name} Results:")
        print("-" * 40)
        print(f"Success: {result['success']}")
        print(f"Session ID: {result['session_id']}")
        
        if result['success']:
            print(f"Requirements Extracted: {len(result['requirements'])}")
            print(f"Test Cases Generated: {len(result['test_cases'])}")
            print(f"Compliance Mappings: {len(result['compliance_mappings'])}")
            
            if result['quality_metrics']:
                print(f"Quality Metrics:")
                print(f"  - Completeness Score: {result['quality_metrics']['completeness_score']:.2f}")
                print(f"  - Accuracy Score: {result['quality_metrics']['accuracy_score']:.2f}")
                print(f"  - Traceability Score: {result['quality_metrics']['traceability_score']:.2f}")
                print(f"  - Compliance Score: {result['quality_metrics']['compliance_score']:.2f}")
                print(f"  - Coverage Percentage: {result['quality_metrics']['coverage_percentage']:.1f}%")
            
            # Show sample requirements
            if result['requirements']:
                print(f"\nSample Requirements:")
                for i, req in enumerate(result['requirements'][:3]):
                    print(f"  {i+1}. {req['title']} ({req['type']})")
            
            # Show sample test cases
            if result['test_cases']:
                print(f"\nSample Test Cases:")
                for i, tc in enumerate(result['test_cases'][:3]):
                    print(f"  {i+1}. {tc['title']} ({tc['type']})")
        
        if result['error_log']:
            print(f"\nErrors:")
            for error in result['error_log']:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
    
    def run_all_examples(self):
        """Run all example scenarios."""
        print("Healthcare Test Case Generation System - Examples")
        print("=" * 60)
        
        examples = [
            self.example_1_basic_healthcare_requirements,
            self.example_2_medical_device_software,
            self.example_3_telemedicine_platform,
            self.example_4_clinical_decision_support,
            self.example_5_multi_document_processing
        ]
        
        for example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"Error running {example_func.__name__}: {str(e)}")
                print("=" * 60)
        
        print("All examples completed!")


def main():
    """Main function to run examples."""
    examples = HealthcareTestCaseExamples()
    examples.run_all_examples()


if __name__ == "__main__":
    main()
