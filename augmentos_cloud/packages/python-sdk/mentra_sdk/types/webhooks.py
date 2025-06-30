"""
Webhook models for the MentraOS Python SDK

These models define the structure of HTTP webhook requests sent from
MentraOS Cloud to app servers for session management.
"""

from typing import Union, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .enums import WebhookRequestType


class BaseWebhookRequest(BaseModel):
    """Base class for all webhook requests"""
    type: WebhookRequestType = Field(..., description="Type of webhook request")
    session_id: str = Field(..., description="Session ID for the request")
    user_id: str = Field(..., description="User ID associated with the session")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")


class SessionWebhookRequest(BaseWebhookRequest):
    """Request to start a new app session"""
    type: WebhookRequestType = WebhookRequestType.SESSION_REQUEST
    mentra_os_websocket_url: Optional[str] = Field(
        None,
        description="WebSocket URL for this specific MentraOS server"
    )
    # Legacy field name for backward compatibility
    augment_os_websocket_url: Optional[str] = Field(
        None,
        description="Legacy WebSocket URL field (deprecated)"
    )


class StopWebhookRequest(BaseWebhookRequest):
    """Request to stop an app session"""
    type: WebhookRequestType = WebhookRequestType.STOP_REQUEST
    reason: str = Field(..., description="Reason for stopping: 'user_disabled', 'system_stop', or 'error'")


class ServerRegistrationWebhookRequest(BaseWebhookRequest):
    """Server registration confirmation"""
    type: WebhookRequestType = WebhookRequestType.SERVER_REGISTRATION
    registration_id: str = Field(..., description="Unique registration identifier")
    package_name: str = Field(..., description="App package name")
    server_urls: list[str] = Field(..., description="List of server URLs")


class ServerHeartbeatWebhookRequest(BaseWebhookRequest):
    """Server heartbeat response"""
    type: WebhookRequestType = WebhookRequestType.SERVER_HEARTBEAT
    registration_id: str = Field(..., description="Registration identifier")


class SessionRecoveryWebhookRequest(BaseWebhookRequest):
    """Session recovery request after disconnect"""
    type: WebhookRequestType = WebhookRequestType.SESSION_RECOVERY
    mentra_os_websocket_url: str = Field(..., description="WebSocket URL for recovery")


# Union type for all webhook requests
WebhookRequest = Union[
    SessionWebhookRequest,
    StopWebhookRequest,
    ServerRegistrationWebhookRequest,
    ServerHeartbeatWebhookRequest,
    SessionRecoveryWebhookRequest,
]


class WebhookResponse(BaseModel):
    """Standard webhook response format"""
    status: str = Field(..., description="Response status: 'success' or 'error'")
    message: Optional[str] = Field(None, description="Optional response message")


# Type guards for webhook requests
def is_session_webhook_request(request: WebhookRequest) -> bool:
    """Check if request is a session request"""
    return isinstance(request, SessionWebhookRequest)


def is_stop_webhook_request(request: WebhookRequest) -> bool:
    """Check if request is a stop request"""
    return isinstance(request, StopWebhookRequest)


def is_server_registration_webhook_request(request: WebhookRequest) -> bool:
    """Check if request is a server registration"""
    return isinstance(request, ServerRegistrationWebhookRequest)


def is_server_heartbeat_webhook_request(request: WebhookRequest) -> bool:
    """Check if request is a server heartbeat"""
    return isinstance(request, ServerHeartbeatWebhookRequest)


def is_session_recovery_webhook_request(request: WebhookRequest) -> bool:
    """Check if request is a session recovery"""
    return isinstance(request, SessionRecoveryWebhookRequest)