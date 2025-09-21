#!/usr/bin/env python3
"""
Basic usage example for the Healthcare Test Case Generation System.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testcaseaiagent.workflows import HealthcareTestCaseGenerator
from testcaseaiagent.models import ComplianceStandard


def main():
    """Basic usage example."""
    print("Healthcare Test Case Generation - Basic Example")
    print("=" * 55)
    
    # Initialize the generator
    generator = HealthcareTestCaseGenerator()
    
    # Sample healthcare requirements
    sample_documents = [
        {
            "filename": "patient_management_requirements.txt",
            "content": """
            The healthcare software system shall provide secure patient data management.
            The system shall comply with HIPAA regulations for data protection.
            The system shall support user authentication and authorization.
            The system shall maintain audit trails for all data access.
            The system shall provide real-time patient monitoring capabilities.
            The system shall integrate with existing hospital information systems.
            The system shall support mobile access for healthcare providers.
            The system shall provide automated alerts for critical patient conditions.
            The system shall maintain data backup and recovery procedures.
            The system shall support multi-language interfaces for international use.
            """
        },
        {
            "filename": "medical_device_requirements.txt", 
            "content": """
            The medical device software shall provide accurate vital signs monitoring.
            The system shall meet FDA Class II medical device requirements.
            The software shall implement IEC 62304 safety lifecycle processes.
            The system shall provide data encryption for patient information.
            The device shall support wireless connectivity with hospital networks.
            The system shall maintain device calibration records.
            The software shall provide real-time alarm notifications.
            The system shall support remote software updates.
            """
        }
    ]
    
    print(f"Processing {len(sample_documents)} documents...")
    
    # Process documents with healthcare compliance standards
    result = generator.process_documents(
        documents=sample_documents,
        compliance_standards=[
            ComplianceStandard.FDA,
            ComplianceStandard.HIPAA,
            ComplianceStandard.IEC_62304,
            ComplianceStandard.ISO_27001
        ]
    )
    
    # Display results
    print("\nProcessing Results:")
    print(f"Success: {result['success']}")
    print(f"Session ID: {result['session_id']}")
    
    if result['success']:
        print(f"Requirements Extracted: {len(result['requirements'])}")
        print(f"Test Cases Generated: {len(result['test_cases'])}")
        
        if result.get('quality_metrics'):
            metrics = result['quality_metrics']
            print(f"Quality Metrics:")
            print(f"   - Completeness: {metrics['completeness_score']:.2f}")
            print(f"   - Accuracy: {metrics['accuracy_score']:.2f}")
            print(f"   - Traceability: {metrics['traceability_score']:.2f}")
            print(f"   - Compliance: {metrics['compliance_score']:.2f}")
            print(f"   - Coverage: {metrics['coverage_percentage']:.1f}%")
        
        # Show sample requirements
        print(f"\nSample Requirements:")
        for i, req in enumerate(result['requirements'][:3]):
            print(f"   {i+1}. {req['title']}")
            print(f"      Priority: {req['priority']}")
            print(f"      Standards: {', '.join(req['compliance_standards'])}")
        
        # Show sample test cases
        print(f"\nSample Test Cases:")
        for i, tc in enumerate(result['test_cases'][:3]):
            print(f"   {i+1}. {tc['title']}")
            print(f"      Type: {tc['test_type']}")
            print(f"      Priority: {tc['priority']}")
            print(f"      Steps: {len(tc['test_steps'])}")
    
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if result.get('error_log'):
            print("Error Details:")
            for error in result['error_log']:
                print(f"   - {error}")
    
    print(f"\nExample completed successfully!")


if __name__ == "__main__":
    main()
