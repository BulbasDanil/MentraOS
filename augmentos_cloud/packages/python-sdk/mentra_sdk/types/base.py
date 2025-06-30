"""
Base Pydantic models for the MentraOS Python SDK

These models provide the foundation for all message types and data structures
used throughout the SDK, ensuring type safety and automatic validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """
    Base class for all WebSocket messages

    All messages in the MentraOS protocol inherit from this base model,
    ensuring consistent structure and automatic timestamp generation.
    """
    type: str = Field(..., description="Type identifier for this message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was created"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for routing"
    )

    class Config:
        # Allow serialization of datetime objects
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Use enum values for serialization
        use_enum_values = True
        # Validate assignment after creation
        validate_assignment = True


class WebSocketError(BaseModel):
    """WebSocket error information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class AuthenticatedRequest(BaseModel):
    """Base model for authenticated HTTP requests"""
    auth_user_id: Optional[str] = Field(None, description="Authenticated user ID")