"""
WebSocket message models for the MentraOS Python SDK

These models define all possible messages that can be sent between apps,
MentraOS Cloud, and smart glasses, with automatic type discrimination.
"""

from typing import Union, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .base import BaseMessage
from .enums import (
    AppToCloudMessageType,
    CloudToAppMessageType,
    StreamType,
    DashboardMode
)
from .config import AppSettings, AppConfig, ToolSchema
from .layouts import Layout, DisplayRequest
from .events import (
    TranscriptionData,
    TranslationData,
    AudioChunk,
    PhotoResponse,
    RtmpStreamStatus,
    CustomMessage,
    ToolCall
)
from .capabilities import Capabilities


# ===== APP TO CLOUD MESSAGES =====

class AppConnectionInit(BaseMessage):
    """Initialize app connection to MentraOS Cloud"""
    type: AppToCloudMessageType = AppToCloudMessageType.CONNECTION_INIT
    package_name: str = Field(..., description="App package identifier")
    api_key: str = Field(..., description="Authentication API key")


class AppSubscriptionUpdate(BaseMessage):
    """Update stream subscriptions"""
    type: AppToCloudMessageType = AppToCloudMessageType.SUBSCRIPTION_UPDATE
    package_name: str = Field(..., description="App package identifier")
    subscriptions: List[str] = Field(..., description="List of stream types to subscribe to")


class PhotoRequest(BaseMessage):
    """Request to take a photo"""
    type: AppToCloudMessageType = AppToCloudMessageType.PHOTO_REQUEST
    package_name: str = Field(..., description="App package identifier")
    save_to_gallery: bool = Field(default=False, description="Save photo to device gallery")


class RtmpStreamRequest(BaseMessage):
    """Request to start RTMP streaming"""
    type: AppToCloudMessageType = AppToCloudMessageType.RTMP_STREAM_REQUEST
    package_name: str = Field(..., description="App package identifier")
    rtmp_url: str = Field(..., description="RTMP destination URL")
    video: Optional[Dict[str, Any]] = Field(None, description="Video configuration")
    audio: Optional[Dict[str, Any]] = Field(None, description="Audio configuration")
    stream: Optional[Dict[str, Any]] = Field(None, description="Stream configuration")


class RtmpStreamStopRequest(BaseMessage):
    """Request to stop RTMP streaming"""
    type: AppToCloudMessageType = AppToCloudMessageType.RTMP_STREAM_STOP
    package_name: str = Field(..., description="App package identifier")
    stream_id: Optional[str] = Field(None, description="Specific stream ID to stop")


class DashboardContentUpdate(BaseMessage):
    """Update dashboard content"""
    type: AppToCloudMessageType = AppToCloudMessageType.DASHBOARD_CONTENT_UPDATE
    package_name: str = Field(..., description="App package identifier")
    content: str = Field(..., description="Content to display")
    modes: List[DashboardMode] = Field(..., description="Target dashboard modes")


class DashboardModeChange(BaseMessage):
    """Change dashboard mode"""
    type: AppToCloudMessageType = AppToCloudMessageType.DASHBOARD_MODE_CHANGE
    package_name: str = Field(..., description="App package identifier")
    mode: DashboardMode = Field(..., description="New dashboard mode")


# App-to-App Communication
class AppBroadcastMessage(BaseMessage):
    """Broadcast message to all app users"""
    type: AppToCloudMessageType = AppToCloudMessageType.APP_BROADCAST_MESSAGE
    package_name: str = Field(..., description="App package identifier")
    payload: Any = Field(..., description="Message payload")
    message_id: str = Field(..., description="Unique message identifier")
    sender_user_id: str = Field(..., description="Sender user ID")


class AppDirectMessage(BaseMessage):
    """Direct message to specific user"""
    type: AppToCloudMessageType = AppToCloudMessageType.APP_DIRECT_MESSAGE
    package_name: str = Field(..., description="App package identifier")
    target_user_id: str = Field(..., description="Target user ID")
    payload: Any = Field(..., description="Message payload")
    message_id: str = Field(..., description="Unique message identifier")
    sender_user_id: str = Field(..., description="Sender user ID")


# Union type for all app-to-cloud messages
AppToCloudMessage = Union[
    AppConnectionInit,
    AppSubscriptionUpdate,
    DisplayRequest,
    PhotoRequest,
    RtmpStreamRequest,
    RtmpStreamStopRequest,
    DashboardContentUpdate,
    DashboardModeChange,
    AppBroadcastMessage,
    AppDirectMessage,
]


# ===== CLOUD TO APP MESSAGES =====

class AppConnectionAck(BaseMessage):
    """Acknowledge app connection"""
    type: CloudToAppMessageType = CloudToAppMessageType.CONNECTION_ACK
    settings: Optional[AppSettings] = Field(None, description="App settings")
    mentraos_settings: Optional[Dict[str, Any]] = Field(None, description="MentraOS system settings")
    config: Optional[AppConfig] = Field(None, description="App configuration")
    capabilities: Optional[Capabilities] = Field(None, description="Device capabilities")


class AppConnectionError(BaseMessage):
    """App connection error"""
    type: CloudToAppMessageType = CloudToAppMessageType.CONNECTION_ERROR
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class AppStopped(BaseMessage):
    """App stopped notification"""
    type: CloudToAppMessageType = CloudToAppMessageType.APP_STOPPED
    reason: str = Field(..., description="Reason for stopping")
    message: Optional[str] = Field(None, description="Additional details")


class SettingsUpdate(BaseMessage):
    """App settings update"""
    type: CloudToAppMessageType = CloudToAppMessageType.SETTINGS_UPDATE
    package_name: str = Field(..., description="App package identifier")
    settings: AppSettings = Field(..., description="Updated settings")


class DataStream(BaseMessage):
    """Generic data stream wrapper"""
    type: CloudToAppMessageType = CloudToAppMessageType.DATA_STREAM
    stream_type: StreamType = Field(..., description="Type of stream data")
    data: Any = Field(..., description="Stream data payload")


class DashboardModeChanged(BaseMessage):
    """Dashboard mode change notification"""
    type: CloudToAppMessageType = CloudToAppMessageType.DASHBOARD_MODE_CHANGED
    mode: DashboardMode = Field(..., description="New dashboard mode")


class PermissionErrorDetail(BaseModel):
    """Details about a permission error"""
    stream: str = Field(..., description="Stream that was rejected")
    required_permission: str = Field(..., description="Required permission")
    message: str = Field(..., description="Detailed error message")


class PermissionError(BaseMessage):
    """Permission denied error"""
    type: CloudToAppMessageType = CloudToAppMessageType.PERMISSION_ERROR
    message: str = Field(..., description="General error message")
    details: List[PermissionErrorDetail] = Field(..., description="Detailed permission errors")


# App-to-App Communication Responses
class AppMessageReceived(BaseMessage):
    """Notification of received app message"""
    type: CloudToAppMessageType = CloudToAppMessageType.APP_MESSAGE_RECEIVED
    payload: Any = Field(..., description="Message payload")
    message_id: str = Field(..., description="Message identifier")
    sender_user_id: str = Field(..., description="Sender user ID")
    sender_session_id: str = Field(..., description="Sender session ID")
    room_id: Optional[str] = Field(None, description="Room ID if applicable")


class AppUserJoined(BaseMessage):
    """User joined app notification"""
    type: CloudToAppMessageType = CloudToAppMessageType.APP_USER_JOINED
    user_id: str = Field(..., description="User ID")
    joined_at: datetime = Field(..., description="Join timestamp")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="User profile")
    room_id: Optional[str] = Field(None, description="Room ID if applicable")


class AppUserLeft(BaseMessage):
    """User left app notification"""
    type: CloudToAppMessageType = CloudToAppMessageType.APP_USER_LEFT
    user_id: str = Field(..., description="User ID")
    left_at: datetime = Field(..., description="Leave timestamp")
    room_id: Optional[str] = Field(None, description="Room ID if applicable")


# Union type for all cloud-to-app messages
CloudToAppMessage = Union[
    AppConnectionAck,
    AppConnectionError,
    AppStopped,
    SettingsUpdate,
    DataStream,
    DashboardModeChanged,
    PermissionError,
    TranscriptionData,
    TranslationData,
    AudioChunk,
    PhotoResponse,
    RtmpStreamStatus,
    CustomMessage,
    AppMessageReceived,
    AppUserJoined,
    AppUserLeft,
]


# ===== MESSAGE PARSING =====

class MessageEnvelope(BaseModel):
    """Wrapper for parsing any incoming message"""
    message: CloudToAppMessage = Field(..., discriminator='type')

    @classmethod
    def parse_message(cls, json_data: str) -> CloudToAppMessage:
        """Parse JSON into the appropriate message type"""
        envelope = cls.model_validate_json(json_data)
        return envelope.message


# ===== TYPE GUARDS =====

def is_transcription_data(msg: CloudToAppMessage) -> bool:
    """Check if message is transcription data"""
    return isinstance(msg, TranscriptionData)


def is_translation_data(msg: CloudToAppMessage) -> bool:
    """Check if message is translation data"""
    return isinstance(msg, TranslationData)


def is_data_stream(msg: CloudToAppMessage) -> bool:
    """Check if message is a data stream"""
    return isinstance(msg, DataStream)


def is_app_connection_ack(msg: CloudToAppMessage) -> bool:
    """Check if message is connection acknowledgment"""
    return isinstance(msg, AppConnectionAck)


def is_settings_update(msg: CloudToAppMessage) -> bool:
    """Check if message is settings update"""
    return isinstance(msg, SettingsUpdate)


def is_permission_error(msg: CloudToAppMessage) -> bool:
    """Check if message is permission error"""
    return isinstance(msg, PermissionError)