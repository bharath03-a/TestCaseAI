"""
Configuration management for the healthcare test case generation system.
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from models import ComplianceStandard, TestCasePriority, DocumentType


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Keys
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")
    
    # Gemini Model Configuration
    gemini_model_name: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL_NAME")
    gemini_temperature: float = Field(default=0.1, env="GEMINI_TEMPERATURE")
    gemini_max_tokens: int = Field(default=8192, env="GEMINI_MAX_TOKENS")
    gemini_top_p: float = Field(default=0.8, env="GEMINI_TOP_P")
    gemini_top_k: int = Field(default=40, env="GEMINI_TOP_K")
    
    # Processing Configuration
    max_document_size_mb: int = Field(default=50, env="MAX_DOCUMENT_SIZE_MB")
    max_concurrent_documents: int = Field(default=5, env="MAX_CONCURRENT_DOCUMENTS")
    processing_timeout_seconds: int = Field(default=3600, env="PROCESSING_TIMEOUT_SECONDS")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")
    retry_delay_seconds: int = Field(default=5, env="RETRY_DELAY_SECONDS")
    
    # File Processing
    supported_document_types: List[DocumentType] = Field(
        default=[DocumentType.PDF, DocumentType.WORD, DocumentType.XML, DocumentType.MARKDOWN],
        env="SUPPORTED_DOCUMENT_TYPES"
    )
    temp_directory: str = Field(default="/tmp/testcase_ai", env="TEMP_DIRECTORY")
    output_directory: str = Field(default="./output", env="OUTPUT_DIRECTORY")
    
    # Compliance Standards
    default_compliance_standards: List[ComplianceStandard] = Field(
        default=[ComplianceStandard.FDA, ComplianceStandard.IEC_62304, ComplianceStandard.ISO_13485],
        env="DEFAULT_COMPLIANCE_STANDARDS"
    )
    
    # Quality Thresholds
    min_completeness_score: float = Field(default=0.8, env="MIN_COMPLETENESS_SCORE")
    min_accuracy_score: float = Field(default=0.85, env="MIN_ACCURACY_SCORE")
    min_traceability_score: float = Field(default=0.9, env="MIN_TRACEABILITY_SCORE")
    min_compliance_score: float = Field(default=0.95, env="MIN_COMPLIANCE_SCORE")
    
    # Test Case Generation
    default_test_case_priority: TestCasePriority = Field(
        default=TestCasePriority.MEDIUM, env="DEFAULT_TEST_CASE_PRIORITY"
    )
    max_test_cases_per_requirement: int = Field(default=10, env="MAX_TEST_CASES_PER_REQUIREMENT")
    include_negative_test_cases: bool = Field(default=True, env="INCLUDE_NEGATIVE_TEST_CASES")
    include_edge_cases: bool = Field(default=True, env="INCLUDE_EDGE_CASES")
    
    # Toolchain Integration
    jira_base_url: Optional[str] = Field(default=None, env="JIRA_BASE_URL")
    jira_username: Optional[str] = Field(default=None, env="JIRA_USERNAME")
    jira_api_token: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")
    
    azure_devops_org: Optional[str] = Field(default=None, env="AZURE_DEVOPS_ORG")
    azure_devops_project: Optional[str] = Field(default=None, env="AZURE_DEVOPS_PROJECT")
    azure_devops_token: Optional[str] = Field(default=None, env="AZURE_DEVOPS_TOKEN")
    
    polarion_url: Optional[str] = Field(default=None, env="POLARION_URL")
    polarion_username: Optional[str] = Field(default=None, env="POLARION_USERNAME")
    polarion_password: Optional[str] = Field(default=None, env="POLARION_PASSWORD")
    
    # Session Management
    session_timeout_minutes: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    max_session_memory_size: int = Field(default=100, env="MAX_SESSION_MEMORY_SIZE")
    enable_session_persistence: bool = Field(default=True, env="ENABLE_SESSION_PERSISTENCE")
    
    # Logging and Monitoring
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    enable_structured_logging: bool = Field(default=True, env="ENABLE_STRUCTURED_LOGGING")
    log_file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    
    # Performance and Scaling
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    enable_parallel_processing: bool = Field(default=True, env="ENABLE_PARALLEL_PROCESSING")
    max_worker_threads: int = Field(default=4, env="MAX_WORKER_THREADS")
    
    # Security
    enable_input_validation: bool = Field(default=True, env="ENABLE_INPUT_VALIDATION")
    enable_output_sanitization: bool = Field(default=True, env="ENABLE_OUTPUT_SANITIZATION")
    max_input_length: int = Field(default=1000000, env="MAX_INPUT_LENGTH")
    allowed_file_extensions: List[str] = Field(
        default=[".pdf", ".docx", ".xml", ".md", ".txt", ".xlsx"],
        env="ALLOWED_FILE_EXTENSIONS"
    )
    
    # Development and Debug
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    enable_detailed_logging: bool = Field(default=False, env="ENABLE_DETAILED_LOGGING")
    mock_external_apis: bool = Field(default=False, env="MOCK_EXTERNAL_APIS")
    
    @field_validator('gemini_temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperature must be between 0.0 and 1.0')
        return v
    
    @field_validator('gemini_max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if v <= 0:
            raise ValueError('Max tokens must be positive')
        return v
    
    @field_validator('min_completeness_score', 'min_accuracy_score', 'min_traceability_score', 'min_compliance_score')
    @classmethod
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Scores must be between 0.0 and 1.0')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


class HealthcareDomainConfig:
    """Healthcare-specific domain configuration."""
    
    # Medical terminology and concepts
    MEDICAL_TERMS = [
        "patient", "diagnosis", "treatment", "medication", "vital signs", "symptoms",
        "medical history", "allergies", "contraindications", "dosage", "administration",
        "side effects", "adverse events", "clinical trial", "protocol", "informed consent",
        "privacy", "confidentiality", "HIPAA", "PHI", "medical device", "software",
        "validation", "verification", "risk management", "quality assurance"
    ]
    
    # Healthcare compliance keywords
    COMPLIANCE_KEYWORDS = {
        ComplianceStandard.FDA: [
            "FDA", "21 CFR", "510(k)", "PMA", "IDE", "QSR", "design controls",
            "risk management", "clinical evaluation", "post-market surveillance"
        ],
        ComplianceStandard.IEC_62304: [
            "IEC 62304", "medical device software", "software lifecycle",
            "risk classification", "software safety classification", "verification",
            "validation", "configuration management", "problem resolution"
        ],
        ComplianceStandard.ISO_13485: [
            "ISO 13485", "quality management", "medical devices", "design and development",
            "risk management", "corrective action", "preventive action", "management review"
        ],
        ComplianceStandard.ISO_27001: [
            "ISO 27001", "information security", "risk assessment", "security controls",
            "data protection", "access control", "incident management", "business continuity"
        ],
        ComplianceStandard.HIPAA: [
            "HIPAA", "PHI", "protected health information", "privacy rule", "security rule",
            "breach notification", "administrative safeguards", "physical safeguards",
            "technical safeguards"
        ],
        ComplianceStandard.GDPR: [
            "GDPR", "personal data", "data subject", "data controller", "data processor",
            "consent", "right to be forgotten", "data portability", "privacy by design"
        ]
    }
    
    # Test case templates for healthcare
    HEALTHCARE_TEST_TEMPLATES = {
        "functional": {
            "positive": [
                "Verify that the system correctly {function} when {condition}",
                "Validate that {feature} operates as expected with {input}",
                "Confirm that {process} completes successfully under {scenario}"
            ],
            "negative": [
                "Verify that the system handles {error_condition} gracefully",
                "Validate that {feature} rejects {invalid_input} appropriately",
                "Confirm that {process} fails safely when {failure_condition}"
            ]
        },
        "security": [
            "Verify that {sensitive_data} is properly encrypted during {operation}",
            "Validate that access to {resource} is restricted to {authorized_users}",
            "Confirm that {audit_trail} is maintained for {security_event}"
        ],
        "compliance": [
            "Verify that {process} complies with {standard} requirements",
            "Validate that {data_handling} meets {regulation} standards",
            "Confirm that {documentation} is maintained per {compliance_requirement}"
        ]
    }
    
    # Risk levels for healthcare applications
    RISK_LEVELS = {
        "critical": [
            "patient safety", "life-threatening", "medical device failure",
            "data breach", "unauthorized access", "system downtime"
        ],
        "high": [
            "data integrity", "regulatory compliance", "audit trail",
            "user authentication", "data backup", "error handling"
        ],
        "medium": [
            "performance", "usability", "integration", "reporting",
            "configuration", "logging"
        ],
        "low": [
            "cosmetic", "minor features", "optional functionality",
            "documentation", "help text"
        ]
    }


class WorkflowConfig:
    """Configuration for LangGraph workflow steps."""
    
    # Step configurations
    STEP_CONFIGS = {
        "document_parser": {
            "timeout_seconds": 300,
            "retry_attempts": 3,
            "parallel_processing": True,
            "chunk_size": 1000
        },
        "requirement_extractor": {
            "timeout_seconds": 600,
            "retry_attempts": 2,
            "batch_size": 5,
            "confidence_threshold": 0.8
        },
        "compliance_mapper": {
            "timeout_seconds": 300,
            "retry_attempts": 2,
            "strict_mode": True,
            "include_recommendations": True
        },
        "test_generator": {
            "timeout_seconds": 900,
            "retry_attempts": 2,
            "max_test_cases": 10,
            "include_edge_cases": True
        },
        "quality_validator": {
            "timeout_seconds": 300,
            "retry_attempts": 2,
            "strict_validation": True,
            "generate_report": True
        },
        "toolchain_integrator": {
            "timeout_seconds": 600,
            "retry_attempts": 3,
            "async_processing": True,
            "batch_export": True
        }
    }
    
    # Conditional routing rules
    ROUTING_RULES = {
        "skip_compliance_mapping": {
            "condition": "len(extracted_requirements) == 0",
            "target_step": "error_handler"
        },
        "skip_test_generation": {
            "condition": "len(compliance_mappings) == 0",
            "target_step": "requirement_extractor"
        },
        "skip_toolchain_integration": {
            "condition": "len(generated_test_cases) == 0",
            "target_step": "quality_validator"
        }
    }


# Global settings instance
settings = Settings()

# Export commonly used configurations
__all__ = [
    "Settings",
    "HealthcareDomainConfig", 
    "WorkflowConfig",
    "settings"
]
