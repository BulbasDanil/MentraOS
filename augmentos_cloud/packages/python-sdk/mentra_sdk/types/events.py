"""
Event data models for the MentraOS Python SDK

These models define the structure of real-time data streams from MentraOS,
including transcription, translations, sensor data, and user interactions.
"""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from .base import BaseMessage
from .enums import StreamType


class TranscriptionData(BaseMessage):
    """Real-time speech transcription data"""
    type: StreamType = StreamType.TRANSCRIPTION
    text: str = Field(..., description="The transcribed text")
    is_final: bool = Field(..., description="Whether this is a final transcription")
    transcribe_language: Optional[str] = Field(None, description="Detected language code")
    start_time: int = Field(..., description="Start time in milliseconds")
    end_time: int = Field(..., description="End time in milliseconds")
    speaker_id: Optional[str] = Field(None, description="ID of the speaker if available")
    duration: Optional[int] = Field(None, description="Audio duration in milliseconds")


class TranslationData(BaseMessage):
    """Real-time translation data"""
    type: StreamType = StreamType.TRANSLATION
    text: str = Field(..., description="The translated text")
    original_text: Optional[str] = Field(None, description="Original text before translation")
    is_final: bool = Field(..., description="Whether this is a final translation")
    start_time: int = Field(..., description="Start time in milliseconds")
    end_time: int = Field(..., description="End time in milliseconds")
    speaker_id: Optional[str] = Field(None, description="ID of the speaker if available")
    duration: Optional[int] = Field(None, description="Audio duration in milliseconds")
    transcribe_language: Optional[str] = Field(None, description="Source language code")
    translate_language: Optional[str] = Field(None, description="Target language code")
    did_translate: bool = Field(default=False, description="Whether text was actually translated")


class AudioChunk(BaseMessage):
    """Raw audio data chunk"""
    type: StreamType = StreamType.AUDIO_CHUNK
    array_buffer: bytes = Field(..., description="The audio data as bytes")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate (e.g., 16000 Hz)")


class ButtonPress(BaseMessage):
    """Physical button press on smart glasses"""
    type: StreamType = StreamType.BUTTON_PRESS
    button_id: str = Field(..., description="Identifier of the pressed button")
    press_type: str = Field(..., description="Type of press: 'short' or 'long'")


class HeadPosition(BaseMessage):
    """Head position/orientation data"""
    type: StreamType = StreamType.HEAD_POSITION
    position: str = Field(..., description="Head position: 'up' or 'down'")


class PhoneNotification(BaseMessage):
    """Phone notification data"""
    type: StreamType = StreamType.PHONE_NOTIFICATION
    notification_id: str = Field(..., description="Unique notification identifier")
    app: str = Field(..., description="Source app name")
    title: str = Field(..., description="Notification title")
    content: str = Field(..., description="Notification content")
    priority: str = Field(..., description="Priority level: 'low', 'normal', or 'high'")


class NotificationDismissed(BaseMessage):
    """Notification dismissal event"""
    type: StreamType = StreamType.NOTIFICATION_DISMISSED
    notification_id: str = Field(..., description="ID of dismissed notification")


class GlassesBatteryUpdate(BaseMessage):
    """Smart glasses battery status"""
    type: StreamType = StreamType.GLASSES_BATTERY_UPDATE
    level: int = Field(..., description="Battery level (0-100)")
    charging: bool = Field(..., description="Whether glasses are charging")
    time_remaining: Optional[int] = Field(None, description="Estimated time remaining in minutes")


class PhoneBatteryUpdate(BaseMessage):
    """Phone battery status"""
    type: StreamType = StreamType.PHONE_BATTERY_UPDATE
    level: int = Field(..., description="Battery level (0-100)")
    charging: bool = Field(..., description="Whether phone is charging")
    time_remaining: Optional[int] = Field(None, description="Estimated time remaining in minutes")


class GlassesConnectionState(BaseMessage):
    """Smart glasses connection status"""
    type: StreamType = StreamType.GLASSES_CONNECTION_STATE
    model_name: str = Field(..., description="Model name of the glasses")
    status: str = Field(..., description="Connection status")


class LocationUpdate(BaseMessage):
    """GPS location data"""
    type: StreamType = StreamType.LOCATION_UPDATE
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")


class VpsCoordinates(BaseMessage):
    """Visual Positioning System coordinates"""
    type: StreamType = StreamType.VPS_COORDINATES
    device_model: str = Field(..., description="Device model identifier")
    request_id: str = Field(..., description="VPS request identifier")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    qx: float = Field(..., description="Quaternion X component")
    qy: float = Field(..., description="Quaternion Y component")
    qz: float = Field(..., description="Quaternion Z component")
    qw: float = Field(..., description="Quaternion W component")
    confidence: float = Field(..., description="Confidence level (0.0-1.0)")


class CalendarEvent(BaseMessage):
    """Calendar event data"""
    type: StreamType = StreamType.CALENDAR_EVENT
    event_id: str = Field(..., description="Unique event identifier")
    title: str = Field(..., description="Event title")
    dt_start: str = Field(..., description="Event start datetime (ISO format)")
    dt_end: str = Field(..., description="Event end datetime (ISO format)")
    timezone: str = Field(..., description="Event timezone")
    time_stamp: str = Field(..., description="Event timestamp")


class Vad(BaseMessage):
    """Voice Activity Detection data"""
    type: StreamType = StreamType.VAD
    status: bool = Field(..., description="Whether voice activity is detected")


class PhotoTaken(BaseMessage):
    """Photo capture event"""
    type: StreamType = StreamType.PHOTO_TAKEN
    photo_data: bytes = Field(..., description="Raw photo data")
    mime_type: str = Field(..., description="MIME type of the photo")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When photo was taken")


class PhotoResponse(BaseMessage):
    """Response to photo request"""
    type: str = "photo_response"
    request_id: str = Field(..., description="Original photo request ID")
    photo_url: str = Field(..., description="URL of the uploaded photo")
    saved_to_gallery: bool = Field(..., description="Whether photo was saved to gallery")


class RtmpStreamStatus(BaseMessage):
    """RTMP streaming status update"""
    type: StreamType = StreamType.RTMP_STREAM_STATUS
    stream_id: Optional[str] = Field(None, description="Unique stream identifier")
    status: str = Field(
        ...,
        description="Stream status: initializing, connecting, streaming, error, stopped, etc."
    )
    error_details: Optional[str] = Field(None, description="Error details if status is error")
    app_id: Optional[str] = Field(None, description="ID of the app that requested the stream")
    stats: Optional[Dict[str, Any]] = Field(None, description="Stream statistics")


class CustomMessage(BaseMessage):
    """Generic custom message for app-specific communication"""
    type: str = "custom_message"
    action: str = Field(..., description="Action identifier for the message")
    payload: Any = Field(..., description="Custom data payload")


class ToolCall(BaseModel):
    """AI tool call request"""
    tool_id: str = Field(..., description="ID of the tool being called")
    tool_parameters: Dict[str, Any] = Field(..., description="Parameters for the tool call")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When tool was called")
    user_id: str = Field(..., description="ID of the user who triggered the call")