"""
State models and data structures for the healthcare test case generation system.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types for requirement ingestion."""
    PDF = "pdf"
    WORD = "docx"
    XML = "xml"
    MARKDOWN = "md"
    TEXT = "txt"
    EXCEL = "xlsx"


class ComplianceStandard(str, Enum):
    """Healthcare compliance standards."""
    FDA = "fda"
    IEC_62304 = "iec_62304"
    ISO_9001 = "iso_9001"
    ISO_13485 = "iso_13485"
    ISO_27001 = "iso_27001"
    HIPAA = "hipaa"
    GDPR = "gdpr"


class TestCaseType(str, Enum):
    """Types of test cases."""
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    SYSTEM = "system"
    ACCEPTANCE = "acceptance"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    COMPLIANCE = "compliance"


class TestCasePriority(str, Enum):
    """Test case priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementType(str, Enum):
    """Types of requirements."""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    USABILITY = "usability"


class DocumentMetadata(BaseModel):
    """Metadata for processed documents."""
    filename: str
    document_type: DocumentType
    file_size: int
    upload_timestamp: datetime
    checksum: str
    language: str = "en"
    encoding: str = "utf-8"


class Requirement(BaseModel):
    """Individual requirement extracted from documents."""
    id: str = Field(..., description="Unique requirement identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed requirement description")
    type: RequirementType
    priority: TestCasePriority
    source_document: str
    source_section: Optional[str] = None
    source_line_number: Optional[int] = None
    stakeholders: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    compliance_standards: List[ComplianceStandard] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    complexity: Literal["simple", "moderate", "complex"] = "moderate"
    estimated_effort: Optional[int] = None  # in hours
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TestCase(BaseModel):
    """Generated test case."""
    id: str = Field(..., description="Unique test case identifier")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Test case description")
    type: TestCaseType
    priority: TestCasePriority
    requirement_ids: List[str] = Field(..., description="Linked requirement IDs")
    preconditions: List[str] = Field(default_factory=list)
    test_steps: List[str] = Field(..., description="Step-by-step test instructions")
    expected_results: List[str] = Field(..., description="Expected outcomes")
    test_data: Dict[str, Any] = Field(default_factory=dict)
    automation_status: Literal["manual", "automated", "semi_automated"] = "manual"
    estimated_duration: Optional[int] = None  # in minutes
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    compliance_standards: List[ComplianceStandard] = Field(default_factory=list)
    traceability_matrix: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ComplianceMapping(BaseModel):
    """Mapping between requirements and compliance standards."""
    requirement_id: str
    standard: ComplianceStandard
    applicable_sections: List[str]
    compliance_level: Literal["fully_compliant", "partially_compliant", "non_compliant"]
    evidence: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class QualityMetrics(BaseModel):
    """Quality metrics for generated test cases."""
    completeness_score: float = Field(ge=0, le=1)
    accuracy_score: float = Field(ge=0, le=1)
    traceability_score: float = Field(ge=0, le=1)
    compliance_score: float = Field(ge=0, le=1)
    coverage_percentage: float = Field(ge=0, le=100)
    total_issues: int = 0
    critical_issues: int = 0
    recommendations: List[str] = Field(default_factory=list)


class ToolchainIntegration(BaseModel):
    """Integration configuration for enterprise toolchains."""
    platform: Literal["jira", "polarion", "azure_devops", "testrail", "qtest"]
    project_id: str
    api_endpoint: str
    authentication: Dict[str, str]
    mapping_config: Dict[str, Any]
    sync_status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    last_sync: Optional[datetime] = None
    sync_errors: List[str] = Field(default_factory=list)


class SessionMemory(BaseModel):
    """Session memory for maintaining context across interactions."""
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_context: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)


class ProcessingStatus(str, Enum):
    """Processing status for workflow steps."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    """Individual workflow step tracking."""
    step_name: str
    status: ProcessingStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphState(BaseModel):
    """Main state for the LangGraph workflow."""
    # Input data
    input_documents: List[Dict[str, Any]] = Field(default_factory=list)
    document_metadata: List[DocumentMetadata] = Field(default_factory=list)
    raw_text_content: List[str] = Field(default_factory=list)
    
    # Processing results
    extracted_requirements: List[Requirement] = Field(default_factory=list)
    compliance_mappings: List[ComplianceMapping] = Field(default_factory=list)
    generated_test_cases: List[TestCase] = Field(default_factory=list)
    quality_metrics: Optional[QualityMetrics] = None
    
    # Integration and export
    toolchain_integrations: List[ToolchainIntegration] = Field(default_factory=list)
    export_formats: List[str] = Field(default_factory=list)
    export_files: List[str] = Field(default_factory=list)
    
    # Session and workflow management
    session_memory: Optional[SessionMemory] = None
    workflow_steps: List[WorkflowStep] = Field(default_factory=list)
    current_step: Optional[str] = None
    error_log: List[str] = Field(default_factory=list)
    
    # Configuration and settings
    processing_config: Dict[str, Any] = Field(default_factory=dict)
    compliance_standards: List[ComplianceStandard] = Field(default_factory=list)
    output_preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # Status tracking
    overall_status: ProcessingStatus = ProcessingStatus.PENDING
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None
    
    # Results and feedback
    final_report: Optional[Dict[str, Any]] = None
    user_feedback: Optional[Dict[str, Any]] = None
    improvement_suggestions: List[str] = Field(default_factory=list)


class APIResponse(BaseModel):
    """Standard API response format."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str


class BatchProcessingRequest(BaseModel):
    """Request for batch processing multiple documents."""
    documents: List[Dict[str, Any]]
    processing_options: Dict[str, Any] = Field(default_factory=dict)
    compliance_standards: List[ComplianceStandard] = Field(default_factory=list)
    output_formats: List[str] = Field(default_factory=list)
    priority: TestCasePriority = TestCasePriority.MEDIUM
    callback_url: Optional[str] = None


class ValidationResult(BaseModel):
    """Result of validation operations."""
    is_valid: bool
    validation_type: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)
    validated_at: datetime = Field(default_factory=datetime.now)
