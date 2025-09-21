"""
Application configuration and settings management.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from ..models import ComplianceStandard, TestCasePriority, DocumentType


class Settings(BaseSettings):
    """Application settings and configuration."""

    # API Keys
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")

    # Gemini Configuration
    gemini_model: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")
    gemini_temperature: float = Field(default=0.3, env="GEMINI_TEMPERATURE")
    gemini_max_tokens: int = Field(default=8192, env="GEMINI_MAX_TOKENS")
    gemini_top_p: float = Field(default=0.95, env="GEMINI_TOP_P")
    gemini_top_k: int = Field(default=40, env="GEMINI_TOP_K")

    # Processing Configuration
    max_documents_per_batch: int = Field(default=10, env="MAX_DOCUMENTS_PER_BATCH")
    max_requirements_per_document: int = Field(default=100, env="MAX_REQUIREMENTS_PER_DOCUMENT")
    max_test_cases_per_requirement: int = Field(default=10, env="MAX_TEST_CASES_PER_REQUIREMENT")
    processing_timeout_seconds: int = Field(default=300, env="PROCESSING_TIMEOUT_SECONDS")

    # Quality Thresholds
    min_completeness_score: float = Field(default=0.8, env="MIN_COMPLETENESS_SCORE")
    min_accuracy_score: float = Field(default=0.85, env="MIN_ACCURACY_SCORE")
    min_traceability_score: float = Field(default=0.9, env="MIN_TRACEABILITY_SCORE")
    min_compliance_score: float = Field(default=0.8, env="MIN_COMPLIANCE_SCORE")

    # Default Compliance Standards
    default_compliance_standards: List[ComplianceStandard] = Field(
        default=[
            ComplianceStandard.FDA,
            ComplianceStandard.HIPAA,
            ComplianceStandard.IEC_62304,
            ComplianceStandard.ISO_27001
        ],
        env="DEFAULT_COMPLIANCE_STANDARDS"
    )

    # Document Processing
    supported_document_types: List[DocumentType] = Field(
        default=[
            DocumentType.PDF,
            DocumentType.WORD,
            DocumentType.XML,
            DocumentType.MARKDOWN,
            DocumentType.TEXT,
            DocumentType.EXCEL
        ],
        env="SUPPORTED_DOCUMENT_TYPES"
    )

    # Output Configuration
    default_output_formats: List[str] = Field(
        default=["json", "xlsx", "xml"],
        env="DEFAULT_OUTPUT_FORMATS"
    )
    output_directory: str = Field(default="./output", env="OUTPUT_DIRECTORY")

    # Session Management
    session_timeout_minutes: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    max_concurrent_sessions: int = Field(default=10, env="MAX_CONCURRENT_SESSIONS")
    session_cleanup_interval_minutes: int = Field(default=30, env="SESSION_CLEANUP_INTERVAL_MINUTES")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    # Healthcare Domain Configuration
    healthcare_domains: List[str] = Field(
        default=[
            "medical_devices",
            "electronic_health_records",
            "clinical_decision_support",
            "telemedicine",
            "medical_imaging",
            "laboratory_information_systems",
            "pharmacy_management",
            "patient_monitoring",
            "healthcare_analytics",
            "healthcare_security"
        ],
        env="HEALTHCARE_DOMAINS"
    )

    # Compliance Mapping Rules
    compliance_mapping_enabled: bool = Field(default=True, env="COMPLIANCE_MAPPING_ENABLED")
    compliance_mapping_confidence_threshold: float = Field(
        default=0.7, env="COMPLIANCE_MAPPING_CONFIDENCE_THRESHOLD"
    )

    # Test Generation Configuration
    test_generation_enabled: bool = Field(default=True, env="TEST_GENERATION_ENABLED")
    include_negative_test_cases: bool = Field(default=True, env="INCLUDE_NEGATIVE_TEST_CASES")
    include_boundary_test_cases: bool = Field(default=True, env="INCLUDE_BOUNDARY_TEST_CASES")
    include_security_test_cases: bool = Field(default=True, env="INCLUDE_SECURITY_TEST_CASES")

    # Integration Configuration
    jira_integration_enabled: bool = Field(default=False, env="JIRA_INTEGRATION_ENABLED")
    jira_url: Optional[str] = Field(default=None, env="JIRA_URL")
    jira_username: Optional[str] = Field(default=None, env="JIRA_USERNAME")
    jira_api_token: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")

    polarion_integration_enabled: bool = Field(default=False, env="POLARION_INTEGRATION_ENABLED")
    polarion_url: Optional[str] = Field(default=None, env="POLARION_URL")
    polarion_username: Optional[str] = Field(default=None, env="POLARION_USERNAME")
    polarion_password: Optional[str] = Field(default=None, env="POLARION_PASSWORD")

    azure_devops_integration_enabled: bool = Field(default=False, env="AZURE_DEVOPS_INTEGRATION_ENABLED")
    azure_devops_url: Optional[str] = Field(default=None, env="AZURE_DEVOPS_URL")
    azure_devops_token: Optional[str] = Field(default=None, env="AZURE_DEVOPS_TOKEN")

    # Performance Configuration
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    max_retry_attempts: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    retry_delay_seconds: int = Field(default=1, env="RETRY_DELAY_SECONDS")

    # Security Configuration
    enable_api_rate_limiting: bool = Field(default=True, env="ENABLE_API_RATE_LIMITING")
    max_requests_per_minute: int = Field(default=60, env="MAX_REQUESTS_PER_MINUTE")
    enable_input_validation: bool = Field(default=True, env="ENABLE_INPUT_VALIDATION")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")

    # Validation Methods
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

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
