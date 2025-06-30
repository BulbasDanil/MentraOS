"""
Enumeration types for the MentraOS Python SDK

All enums use StrEnum for Python 3.11+ compatibility and string enum for older versions.
This allows enums to be used interchangeably as enum members or strings.
"""

import sys
from typing import Any

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    # Compatibility for Python 3.9/3.10
    from enum import Enum

    class StrEnum(str, Enum):
        """String enumeration for Python < 3.11 compatibility"""
        def __new__(cls, value: str) -> Any:
            obj = str.__new__(cls, value)
            obj._value_ = value
            return obj


class AppType(StrEnum):
    """Types of MentraOS applications"""
    SYSTEM_DASHBOARD = "system_dashboard"  # Special UI placement, system functionality
    BACKGROUND = "background"              # Can temporarily take control of display
    STANDARD = "standard"                  # Regular app (default)


class AppState(StrEnum):
    """Application lifecycle states"""
    NOT_INSTALLED = "not_installed"  # Initial state
    INSTALLED = "installed"          # Installed but never run
    BOOTING = "booting"              # Starting up
    RUNNING = "running"              # Active and running
    STOPPED = "stopped"              # Manually stopped
    ERROR = "error"                  # Error state


class Language(StrEnum):
    """Supported languages for transcription and translation"""
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    RU = "ru"
    ZH = "zh"
    JA = "ja"
    KO = "ko"


class LayoutType(StrEnum):
    """Types of display layouts available in AR view"""
    TEXT_WALL = "text_wall"
    DOUBLE_TEXT_WALL = "double_text_wall"
    DASHBOARD_CARD = "dashboard_card"
    REFERENCE_CARD = "reference_card"
    BITMAP_VIEW = "bitmap_view"


class ViewType(StrEnum):
    """Target views for display content"""
    DASHBOARD = "dashboard"   # Regular dashboard (main/expanded)
    ALWAYS_ON = "always_on"   # Persistent overlay dashboard
    MAIN = "main"             # Regular app content


class AppSettingType(StrEnum):
    """Types of app settings"""
    TOGGLE = "toggle"
    TEXT = "text"
    SELECT = "select"
    SLIDER = "slider"
    GROUP = "group"
    TEXT_NO_SAVE_BUTTON = "text_no_save_button"
    SELECT_WITH_SEARCH = "select_with_search"
    MULTISELECT = "multiselect"
    TITLE_VALUE = "titleValue"


class StreamType(StrEnum):
    """Types of real-time data streams from MentraOS"""
    # Core user interaction streams
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    BUTTON_PRESS = "button_press"
    HEAD_POSITION = "head_position"
    PHONE_NOTIFICATION = "phone_notification"

    # System status streams
    GLASSES_BATTERY_UPDATE = "glasses_battery_update"
    PHONE_BATTERY_UPDATE = "phone_battery_update"
    GLASSES_CONNECTION_STATE = "glasses_connection_state"

    # Location and spatial streams
    LOCATION_UPDATE = "location_update"
    VPS_COORDINATES = "vps_coordinates"

    # Audio/video streams
    VAD = "vad"  # Voice Activity Detection
    AUDIO_CHUNK = "audio_chunk"
    VIDEO = "video"
    RTMP_STREAM_STATUS = "rtmp_stream_status"

    # Calendar and notifications
    CALENDAR_EVENT = "calendar_event"
    NOTIFICATION_DISMISSED = "notification_dismissed"

    # Media and capture
    PHOTO_TAKEN = "photo_taken"

    # App lifecycle
    START_APP = "start_app"
    STOP_APP = "stop_app"
    OPEN_DASHBOARD = "open_dashboard"

    # Special stream types
    ALL = "all"
    WILDCARD = "*"

    # System streams
    MENTRAOS_SETTINGS_UPDATE_REQUEST = "mentraos_settings_update_request"
    CORE_STATUS_UPDATE = "core_status_update"


class DashboardMode(StrEnum):
    """Dashboard display modes"""
    MAIN = "main"           # Full dashboard experience
    EXPANDED = "expanded"   # More space for app content


# Message type enums for WebSocket communication
class GlassesToCloudMessageType(StrEnum):
    """Message types sent from glasses to cloud"""
    # Control actions
    CONNECTION_INIT = "connection_init"
    REQUEST_SETTINGS = "request_settings"
    START_APP = "start_app"
    STOP_APP = "stop_app"
    DASHBOARD_STATE = "dashboard_state"
    OPEN_DASHBOARD = "open_dashboard"

    # Media responses
    PHOTO_RESPONSE = "photo_response"

    # RTMP streaming
    RTMP_STREAM_STATUS = "rtmp_stream_status"
    KEEP_ALIVE_ACK = "keep_alive_ack"

    # Events and data (using StreamType values)
    BUTTON_PRESS = StreamType.BUTTON_PRESS
    HEAD_POSITION = StreamType.HEAD_POSITION
    GLASSES_BATTERY_UPDATE = StreamType.GLASSES_BATTERY_UPDATE
    PHONE_BATTERY_UPDATE = StreamType.PHONE_BATTERY_UPDATE
    GLASSES_CONNECTION_STATE = StreamType.GLASSES_CONNECTION_STATE
    LOCATION_UPDATE = StreamType.LOCATION_UPDATE
    VPS_COORDINATES = StreamType.VPS_COORDINATES
    VAD = StreamType.VAD
    PHONE_NOTIFICATION = StreamType.PHONE_NOTIFICATION
    NOTIFICATION_DISMISSED = StreamType.NOTIFICATION_DISMISSED
    CALENDAR_EVENT = StreamType.CALENDAR_EVENT
    MENTRAOS_SETTINGS_UPDATE_REQUEST = StreamType.MENTRAOS_SETTINGS_UPDATE_REQUEST
    CORE_STATUS_UPDATE = StreamType.CORE_STATUS_UPDATE
    PHOTO_TAKEN = StreamType.PHOTO_TAKEN


class CloudToGlassesMessageType(StrEnum):
    """Message types sent from cloud to glasses"""
    # Responses
    CONNECTION_ACK = "connection_ack"
    CONNECTION_ERROR = "connection_error"
    AUTH_ERROR = "auth_error"

    # Updates
    DISPLAY_EVENT = "display_event"
    APP_STATE_CHANGE = "app_state_change"
    MICROPHONE_STATE_CHANGE = "microphone_state_change"
    PHOTO_REQUEST = "photo_request"
    SETTINGS_UPDATE = "settings_update"

    # RTMP streaming
    START_RTMP_STREAM = "start_rtmp_stream"
    STOP_RTMP_STREAM = "stop_rtmp_stream"
    KEEP_RTMP_STREAM_ALIVE = "keep_rtmp_stream_alive"

    # Dashboard updates
    DASHBOARD_MODE_CHANGE = "dashboard_mode_change"
    DASHBOARD_ALWAYS_ON_CHANGE = "dashboard_always_on_change"

    WEBSOCKET_ERROR = "websocket_error"


class AppToCloudMessageType(StrEnum):
    """Message types sent from app to cloud"""
    # Commands
    CONNECTION_INIT = "tpa_connection_init"
    SUBSCRIPTION_UPDATE = "subscription_update"

    # Requests
    DISPLAY_REQUEST = "display_event"
    PHOTO_REQUEST = "photo_request"

    # RTMP streaming
    RTMP_STREAM_REQUEST = "rtmp_stream_request"
    RTMP_STREAM_STOP = "rtmp_stream_stop"

    # Dashboard requests
    DASHBOARD_CONTENT_UPDATE = "dashboard_content_update"
    DASHBOARD_MODE_CHANGE = "dashboard_mode_change"
    DASHBOARD_SYSTEM_UPDATE = "dashboard_system_update"

    # App-to-App Communication
    APP_BROADCAST_MESSAGE = "app_broadcast_message"
    APP_DIRECT_MESSAGE = "app_direct_message"
    APP_USER_DISCOVERY = "app_user_discovery"
    APP_ROOM_JOIN = "app_room_join"
    APP_ROOM_LEAVE = "app_room_leave"


class CloudToAppMessageType(StrEnum):
    """Message types sent from cloud to app"""
    # Responses
    CONNECTION_ACK = "tpa_connection_ack"
    CONNECTION_ERROR = "tpa_connection_error"

    # Updates
    APP_STOPPED = "app_stopped"
    SETTINGS_UPDATE = "settings_update"

    # Dashboard updates
    DASHBOARD_MODE_CHANGED = "dashboard_mode_changed"
    DASHBOARD_ALWAYS_ON_CHANGED = "dashboard_always_on_changed"

    # Stream data
    DATA_STREAM = "data_stream"

    # Media responses
    PHOTO_RESPONSE = "photo_response"
    RTMP_STREAM_STATUS = "rtmp_stream_status"

    WEBSOCKET_ERROR = "websocket_error"

    # Permissions
    PERMISSION_ERROR = "permission_error"

    # General purpose messaging
    CUSTOM_MESSAGE = "custom_message"

    # App-to-App Communication Responses
    APP_MESSAGE_RECEIVED = "app_message_received"
    APP_USER_JOINED = "app_user_joined"
    APP_USER_LEFT = "app_user_left"
    APP_ROOM_UPDATED = "app_room_updated"
    APP_DIRECT_MESSAGE_RESPONSE = "app_direct_message_response"


class PermissionType(StrEnum):
    """Types of permissions apps can request"""
    MICROPHONE = "MICROPHONE"
    LOCATION = "LOCATION"
    CALENDAR = "CALENDAR"

    # Legacy notification permission (backward compatibility)
    NOTIFICATIONS = "NOTIFICATIONS"

    # New granular notification permissions
    READ_NOTIFICATIONS = "READ_NOTIFICATIONS"
    POST_NOTIFICATIONS = "POST_NOTIFICATIONS"

    ALL = "ALL"


class WebhookRequestType(StrEnum):
    """Types of webhook requests"""
    SESSION_REQUEST = "session_request"
    STOP_REQUEST = "stop_request"
    SERVER_REGISTRATION = "server_registration"
    SERVER_HEARTBEAT = "server_heartbeat"
    SESSION_RECOVERY = "session_recovery"