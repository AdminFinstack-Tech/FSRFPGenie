from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId

# Enums
class DocumentType(str, Enum):
    RFP = "RFP"
    DOCUMENTATION = "Documentation"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    AWAITING_MAPPING = "awaiting_mapping"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

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

# MongoDB Models
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

# Document Models
class Document(MongoBaseModel):
    document_type: DocumentType
    file_name: str
    file_path: str
    file_size: int
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: Dict[str, Any] = {}
    records_processed: int = 0
    total_records: int = 0
    error_details: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    uploaded_by: str = "anonymous"

    @validator('metadata', pre=True)
    def validate_metadata(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

class RFPEntry(MongoBaseModel):
    document_id: PyObjectId
    product: str = "General"
    requirement: str
    requirement_category: RequirementCategory
    response_category: ResponseCategory
    effort_required: Optional[EffortRequired] = None
    comments: Optional[str] = None
    rfp_name: str
    bank_name: str
    date: datetime
    created_by: str = "anonymous"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    vector_id: Optional[str] = None

class Template(MongoBaseModel):
    name: str
    mappings: Dict[str, str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "anonymous"

class User(MongoBaseModel):
    email: str
    name: Optional[str] = None
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

# Index definitions for MongoDB
INDEXES = {
    "documents": [
        {"keys": [("created_at", -1)]},
        {"keys": [("status", 1)]},
        {"keys": [("document_type", 1)]}
    ],
    "rfp_entries": [
        {"keys": [("document_id", 1)]},
        {"keys": [("product", 1)]},
        {"keys": [("response_category", 1)]},
        {"keys": [("date", -1)]},
        {"keys": [("created_at", -1)]},
        {"keys": [("vector_id", 1)], "unique": True, "sparse": True}
    ],
    "templates": [
        {"keys": [("name", 1)]},
        {"keys": [("created_at", -1)]}
    ],
    "users": [
        {"keys": [("email", 1)], "unique": True}
    ]
}

# Helper functions for MongoDB operations
def create_indexes(db):
    """Create indexes for all collections"""
    for collection_name, indexes in INDEXES.items():
        collection = db[collection_name]
        for index in indexes:
            collection.create_index(**index)

def to_mongo_dict(model: BaseModel) -> dict:
    """Convert Pydantic model to MongoDB document"""
    data = model.dict(by_alias=True, exclude_unset=True)
    if "_id" in data and data["_id"] is None:
        data.pop("_id")
    return data

def from_mongo_dict(data: dict, model_class: type) -> BaseModel:
    """Convert MongoDB document to Pydantic model"""
    if data and "_id" in data:
        data["_id"] = str(data["_id"])
    return model_class(**data) if data else None