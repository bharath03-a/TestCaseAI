"""
Core data models and enums for the healthcare test case generation system.
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


class ProcessingStatus(str, Enum):
    """Processing status for workflow steps."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Requirement(BaseModel):
    """Healthcare software requirement."""
    id: str = Field(..., description="Unique requirement identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed requirement description")
    priority: TestCasePriority = Field(default=TestCasePriority.MEDIUM)
    source_document: str = Field(..., description="Source document filename")
    source_section: Optional[str] = Field(None, description="Source section or page")
    requirement_type: str = Field(default="functional", description="Type of requirement")
    compliance_standards: List[str] = Field(default_factory=list, description="Relevant compliance standards")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TestCase(BaseModel):
    """Generated test case."""
    id: str = Field(..., description="Unique test case identifier")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Test case description")
    test_type: TestCaseType = Field(default=TestCaseType.FUNCTIONAL)
    priority: TestCasePriority = Field(default=TestCasePriority.MEDIUM)
    requirement_id: str = Field(..., description="Linked requirement ID")
    test_steps: List[str] = Field(default_factory=list, description="Test execution steps")
    expected_results: List[str] = Field(default_factory=list, description="Expected test results")
    test_data: Optional[Dict[str, Any]] = Field(None, description="Required test data")
    preconditions: List[str] = Field(default_factory=list, description="Test preconditions")
    postconditions: List[str] = Field(default_factory=list, description="Test postconditions")
    compliance_standards: List[str] = Field(default_factory=list, description="Relevant compliance standards")
    created_at: datetime = Field(default_factory=datetime.now)


class QualityMetrics(BaseModel):
    """Quality assessment metrics."""
    completeness_score: float = Field(ge=0.0, le=1.0, description="Test case completeness score")
    accuracy_score: float = Field(ge=0.0, le=1.0, description="Test case accuracy score")
    traceability_score: float = Field(ge=0.0, le=1.0, description="Requirement traceability score")
    compliance_score: float = Field(ge=0.0, le=1.0, description="Compliance coverage score")
    coverage_percentage: float = Field(ge=0.0, le=100.0, description="Overall coverage percentage")
    total_requirements: int = Field(ge=0, description="Total requirements processed")
    total_test_cases: int = Field(ge=0, description="Total test cases generated")
    average_test_cases_per_requirement: float = Field(ge=0.0, description="Average test cases per requirement")


class DocumentMetadata(BaseModel):
    """Document metadata and parsing information."""
    filename: str = Field(..., description="Document filename")
    document_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(ge=0, description="File size in bytes")
    page_count: Optional[int] = Field(None, description="Number of pages")
    word_count: int = Field(ge=0, description="Word count")
    parsed_at: datetime = Field(default_factory=datetime.now)
    parsing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    error_message: Optional[str] = Field(None, description="Parsing error message if any")


class ComplianceMapping(BaseModel):
    """Mapping between requirements and compliance standards."""
    requirement_id: str = Field(..., description="Requirement identifier")
    compliance_standard: ComplianceStandard = Field(..., description="Compliance standard")
    mapping_confidence: float = Field(ge=0.0, le=1.0, description="Mapping confidence score")
    relevant_sections: List[str] = Field(default_factory=list, description="Relevant standard sections")
    compliance_notes: Optional[str] = Field(None, description="Additional compliance notes")
    created_at: datetime = Field(default_factory=datetime.now)


class ToolchainIntegration(BaseModel):
    """Toolchain integration configuration."""
    platform: str = Field(..., description="Integration platform (Jira, Polarion, etc.)")
    project_id: str = Field(..., description="Project identifier")
    export_format: str = Field(..., description="Export format")
    export_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    export_url: Optional[str] = Field(None, description="Export URL if available")
    exported_at: Optional[datetime] = Field(None, description="Export timestamp")
    error_message: Optional[str] = Field(None, description="Export error if any")


class WorkflowStep(BaseModel):
    """Individual workflow step information."""
    step_name: str = Field(..., description="Workflow step name")
    step_type: str = Field(..., description="Step type")
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    started_at: Optional[datetime] = Field(None, description="Step start time")
    completed_at: Optional[datetime] = Field(None, description="Step completion time")
    duration_seconds: Optional[float] = Field(None, description="Step duration")
    input_count: int = Field(default=0, description="Input items processed")
    output_count: int = Field(default=0, description="Output items generated")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class SessionMemory(BaseModel):
    """Session memory for workflow state management."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    workflow_state: Optional[Dict[str, Any]] = Field(None, description="Current workflow state")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Contextual data")
    is_active: bool = Field(default=True, description="Session active status")


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
