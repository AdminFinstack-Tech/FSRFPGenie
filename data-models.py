# data_models.py - Pydantic models for RFP RAG System

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, validator


# Enums
class DocumentType(str, Enum):
    RFP = "RFP"
    DOCUMENTATION = "Documentation"


class RequirementCategory(str, Enum):
    MUST_HAVE = "Must Have"
    CRITICAL = "Critical"
    GOOD_TO_HAVE = "Good to Have"


class ResponseCategory(str, Enum):
    READILY_AVAILABLE = "Readily Available"
    CONFIGURATION = "Configuration"
    CUSTOMIZATION = "Customization"
    NOT_AVAILABLE = "Not Available"


class EffortRequired(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CONSIDERABLE = "Considerable"


class DocumentCategory(str, Enum):
    GUIDANCE = "Guidance"
    WHITE_PAPER = "White Paper"
    USER_MANUAL = "User Manual"
    GAP_DOCUMENT = "Gap Document"


class ProcessingStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# Request Models
class UploadMetadata(BaseModel):
    # RFP specific fields
    rfp_name: Optional[str] = None
    bank_name: Optional[str] = None
    product: Optional[str] = None
    
    # Documentation specific fields
    document_name: Optional[str] = None
    related_product: Optional[str] = None
    submodule: Optional[str] = None
    document_category: Optional[DocumentCategory] = None
    tags: Optional[List[str]] = []

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            return [tag.strip().lower() for tag in v if tag.strip()]
        return []


class ColumnMapping(BaseModel):
    product: str = Field(..., description="Source column for product")
    requirement: str = Field(..., description="Source column for requirement")
    requirement_category: str = Field(..., description="Source column for requirement category")
    response_category: str = Field(..., description="Source column for response category")
    effort_required: Optional[str] = Field(None, description="Source column for effort required")
    comments: Optional[str] = Field(None, description="Source column for comments")


class ColumnMappingRequest(BaseModel):
    mappings: ColumnMapping
    save_template: bool = False
    template_name: Optional[str] = None

    @validator('template_name')
    def validate_template_name(cls, v, values):
        if values.get('save_template') and not v:
            raise ValueError('template_name is required when save_template is True')
        return v


class QueryFilters(BaseModel):
    products: Optional[List[str]] = []
    response_categories: Optional[List[ResponseCategory]] = []
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    document_types: Optional[List[DocumentType]] = []


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_n: int = Field(10, ge=1, le=100)
    filters: Optional[QueryFilters] = None


# Response Models
class UploadResponse(BaseModel):
    document_id: UUID
    status: ProcessingStatus
    message: str


class ProcessingError(BaseModel):
    row: int
    error: str


class DocumentStatus(BaseModel):
    document_id: UUID
    status: ProcessingStatus
    records_processed: Optional[int] = None
    total_records: Optional[int] = None
    errors: List[ProcessingError] = []
    completed_at: Optional[datetime] = None


class RFPRecord(BaseModel):
    record_id: UUID
    product: str
    requirement: str
    requirement_category: RequirementCategory
    response_category: ResponseCategory
    effort_required: Optional[EffortRequired] = None
    comments: Optional[str] = None
    rfp_name: str
    bank_name: str
    date: date
    created_by: str
    last_modified: datetime


class QueryResult(RFPRecord):
    relevance_score: float = Field(..., ge=0, le=1)
    highlight: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    total_results: int
    returned_results: int
    results: List[QueryResult]


class MappingTemplate(BaseModel):
    template_id: UUID
    template_name: str
    created_at: datetime
    mappings: Dict[str, str]


class HealthStatus(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str
    services: Dict[str, str] = {}


# Database Models
class DocumentRecord(BaseModel):
    id: UUID
    document_type: DocumentType
    file_name: str
    file_path: str
    file_size: int
    upload_date: datetime
    uploaded_by: str
    processing_status: ProcessingStatus
    metadata: Dict[str, Any]
    error_details: Optional[List[ProcessingError]] = None
    
    class Config:
        orm_mode = True


class RFPEntry(BaseModel):
    id: UUID
    document_id: UUID
    product: str = "General"
    requirement: str
    requirement_category: RequirementCategory
    response_category: ResponseCategory
    effort_required: Optional[EffortRequired] = None
    comments: Optional[str] = None
    rfp_name: str
    bank_name: str
    date: date
    created_by: str
    created_at: datetime
    last_modified: datetime
    vector_id: Optional[str] = None  # ID in vector database
    
    class Config:
        orm_mode = True


# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(ErrorResponse):
    error: str = "ValidationError"
    
    
class AuthenticationErrorResponse(ErrorResponse):
    error: str = "AuthenticationError"


class NotFoundErrorResponse(ErrorResponse):
    error: str = "NotFoundError"


class PayloadTooLargeResponse(BaseModel):
    error: str = "PayloadTooLarge"
    message: str
    max_size_mb: int


# Utility Models
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=200)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[Any]  # Override in subclasses


class BulkOperationResult(BaseModel):
    total: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = []


# Vector Database Models
class VectorDocument(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class VectorSearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]


# Configuration Models
class SystemConfig(BaseModel):
    max_file_size_mb: int = 50
    supported_file_types: List[str] = [".xlsx", ".xls", ".pdf", ".docx"]
    default_top_n: int = 10
    vector_dimension: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 200