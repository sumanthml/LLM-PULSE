from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator
from src.utils.logger import setup_custom_logger

logger = setup_custom_logger("DataContractGuard")

class TelemetryRecord(BaseModel):
    id: str = Field(..., min_length=2)
    timestamp: str = Field(..., description="Stored as standard ISO string format")
    source: str = Field(..., min_length=2)
    raw_text: str = Field(..., min_length=5)
    target_entity: Optional[str] = Field(default="Generic Tech")
    sentiment_label: Optional[str] = Field(default="Neutral")
    sentiment_score: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator('timestamp', mode='before')
    def clean_and_coerce_timestamp(cls, value):
        """
        Advanced Datetime Parsing Gate:
        Cleans and normalizes irregular time strings from RSS and Reddit feeds
        into a consistent format.
        """
        if not value:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        
        value_str = str(value).strip()
        
        # Strip trailing text or time zone info (e.g., 'GMT', 'UTC', '+0000')
        value_str = re.sub(r'\s+[A-Z]{3,4}$', '', value_str)
        value_str = re.sub(r'\s+[\+\-]\d{4}$', '', value_str)
        
        # Clean common enterprise syndication formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%a, %d %b %Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
        # Safe fallback to current time if parsing fails
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @field_validator('id', 'source', 'raw_text', mode='before')
    def verify_strings(cls, value):
        if value is None:
            raise ValueError("Field cannot resolve to None matrix type")
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Target string cannot evaluate to empty spaces")
        return cleaned

def enforce_schema_quality(payload: dict) -> Optional[TelemetryRecord]:
    try:
        record = TelemetryRecord(**payload)
        return record
    except Exception as validation_error:
        logger.warning(f"Contract Gate Rejected Row from source {payload.get('source')}: {validation_error}")
        return None