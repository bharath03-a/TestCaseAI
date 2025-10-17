"""
Main entry point for the healthcare test case generation system.
"""

import logging

import dotenv

from .models import ComplianceStandard
from .workflows import HealthcareTestCaseGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

# Global instance
test_case_generator = HealthcareTestCaseGenerator()


def main():
    """Main function for testing the system."""
    # Example usage
    sample_documents = [
        {
            "filename": "healthcare_requirements.pdf",
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
            """,
        }
    ]

    # Process documents
    result = test_case_generator.process_documents(
        documents=sample_documents,
        compliance_standards=[
            ComplianceStandard.FDA,
            ComplianceStandard.HIPAA,
            ComplianceStandard.IEC_62304,
        ],
    )

    # Print results
    print("Processing Results:")
    print(f"Success: {result['success']}")
    print(f"Session ID: {result['session_id']}")

    if result["success"]:
        print(f"Requirements Count: {len(result.get('requirements', []))}")
        print(f"Test Cases Count: {len(result.get('test_cases', []))}")
        quality_score = (
            result["quality_metrics"]["completeness_score"]
            if result.get("quality_metrics")
            else "N/A"
        )
        print(f"Quality Score: {quality_score}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    if result.get("error_log"):
        print("Errors:")
        for error in result["error_log"]:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
