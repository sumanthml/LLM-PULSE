from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.utils.logger import setup_custom_logger

logger = setup_custom_logger("DataContractGuard")

class TelemetryRecord(BaseModel):
    """
    Strict Pydantic data schema for enterprise validation.
    Enforces types and non-empty bounds on all streaming fields.
    """
    id: str = Field(..., min_length=2, description="Unique source identifier string")
    timestamp: datetime = Field(..., description="Timestamp of event creation")
    source: str = Field(..., min_length=2, description="Origin platform node")
    raw_text: str = Field(..., min_length=5, description="Cleaned text description body")
    target_entity: Optional[str] = Field(default=None, description="Classified AI ecosystem brand entity")
    sentiment_label: Optional[str] = Field(default=None, description="Computed inference classification token")
    sentiment_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Inference model certainty confidence metric")

    @field_validator('id', 'source', 'raw_text', mode='before')
    def strip_and_verify_strings(cls, value):
        """Ensures incoming payload values are trimmed and valid strings."""
        if value is None:
            raise ValueError("Field entry cannot resolve to a None value matrix type")
        if not isinstance(value, str):
            value = str(value)
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Target string cannot evaluate to an empty whitespace frame")
        return cleaned

def enforce_schema_quality(payload: dict) -> Optional[TelemetryRecord]:
    """
    Validates an incoming payload against our strict Pydantic model.
    Returns a TelemetryRecord object if valid, or None if validation fails.
    """
    try:
        # Pydantic validates schemas and converts timestamp strings to datetime objects automatically
        record = TelemetryRecord(**payload)
        return record
    except Exception as validation_error:
        logger.warning(f"Rejected Log Stream Row: Data failed contract specifications. Error: {validation_error}")
        return None