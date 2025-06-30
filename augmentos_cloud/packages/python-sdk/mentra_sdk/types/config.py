"""
Configuration models for the MentraOS Python SDK

These models define the configuration structures for AppServer, AppSession,
and app settings, providing type-safe configuration management.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from .enums import AppSettingType, AppType, PermissionType


class AppServerConfig(BaseModel):
    """Configuration for AppServer instances"""

    package_name: str = Field(
        ...,
        description="Unique identifier for your app (e.g., 'org.company.appname')"
    )
    api_key: str = Field(..., description="API key for authentication with MentraOS Cloud")
    port: int = Field(default=7010, description="Port number for the server")
    webhook_path: str = Field(default="/webhook", description="Path for webhook endpoint")
    public_dir: Optional[str] = Field(
        None,
        description="Directory for serving static files (None to disable)"
    )
    health_check: bool = Field(default=True, description="Enable health check endpoint")
    cookie_secret: Optional[str] = Field(
        None,
        description="Secret key for signing session cookies"
    )
    app_instructions: Optional[str] = Field(
        None,
        description="App instructions string shown to the user"
    )

    @validator('port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


class AppSessionConfig(BaseModel):
    """Configuration for AppSession instances"""

    package_name: str = Field(
        ...,
        description="Unique identifier for your app"
    )
    api_key: str = Field(..., description="API key for authentication")
    mentra_os_websocket_url: Optional[str] = Field(
        default="ws://localhost:7002/app-ws",
        description="WebSocket server URL"
    )
    auto_reconnect: bool = Field(
        default=True,
        description="Automatically attempt to reconnect on disconnect"
    )
    max_reconnect_attempts: int = Field(
        default=3,
        description="Maximum number of reconnection attempts"
    )
    reconnect_delay: int = Field(
        default=1000,
        description="Base delay between reconnection attempts in ms"
    )
    user_id: str = Field(..., description="User ID for tracking sessions")


class Permission(BaseModel):
    """App permission definition"""
    type: PermissionType = Field(..., description="Type of permission")
    description: Optional[str] = Field(None, description="Human-readable description")


class ToolParameterSchema(BaseModel):
    """Schema for tool parameters"""
    type: str = Field(..., description="Parameter type (string, number, boolean)")
    description: str = Field(..., description="Parameter description")
    enum: Optional[List[str]] = Field(None, description="Allowed values for enum types")
    required: bool = Field(default=False, description="Whether parameter is required")


class ToolSchema(BaseModel):
    """Schema for app tools/capabilities"""
    id: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Tool description")
    activation_phrases: Optional[List[str]] = Field(
        None,
        description="Phrases that activate this tool"
    )
    parameters: Optional[Dict[str, ToolParameterSchema]] = Field(
        None,
        description="Tool parameters schema"
    )


class DeveloperProfile(BaseModel):
    """Developer/organization profile information"""
    company: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None


class BaseAppSetting(BaseModel):
    """Base class for all app settings"""
    key: str = Field(..., description="Setting key identifier")
    label: str = Field(..., description="Human-readable label")
    value: Optional[Any] = Field(None, description="User's selected value")
    default_value: Optional[Any] = Field(None, description="System default value")


class ToggleSetting(BaseAppSetting):
    """Boolean toggle setting"""
    type: AppSettingType = AppSettingType.TOGGLE
    default_value: bool = Field(False, description="Default boolean value")
    value: Optional[bool] = Field(None, description="Current boolean value")


class TextSetting(BaseAppSetting):
    """Text input setting"""
    type: AppSettingType = AppSettingType.TEXT
    default_value: Optional[str] = Field(None, description="Default text value")
    value: Optional[str] = Field(None, description="Current text value")


class SelectOption(BaseModel):
    """Option for select-type settings"""
    label: str = Field(..., description="Display label")
    value: Any = Field(..., description="Option value")


class SelectSetting(BaseAppSetting):
    """Single-select dropdown setting"""
    type: AppSettingType = AppSettingType.SELECT
    options: List[SelectOption] = Field(..., description="Available options")
    default_value: Optional[Any] = Field(None, description="Default selected value")
    value: Optional[Any] = Field(None, description="Current selected value")


class SliderSetting(BaseAppSetting):
    """Numeric slider setting"""
    type: AppSettingType = AppSettingType.SLIDER
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    default_value: float = Field(..., description="Default numeric value")
    value: Optional[float] = Field(None, description="Current numeric value")


# Union type for all possible settings
AppSetting = Union[
    ToggleSetting,
    TextSetting,
    SelectSetting,
    SliderSetting,
    # Add other setting types as needed
]

AppSettings = List[AppSetting]


class AppConfig(BaseModel):
    """Complete app configuration"""
    name: str = Field(..., description="App name")
    description: str = Field(..., description="App description")
    version: str = Field(..., description="App version")
    settings: AppSettings = Field(default_factory=list, description="App settings")
    tools: List[ToolSchema] = Field(default_factory=list, description="App tools")


class AppInfo(BaseModel):
    """App information model"""
    package_name: str = Field(..., description="Unique package identifier")
    name: str = Field(..., description="App display name")
    public_url: str = Field(..., description="Base URL of the app server")
    is_system_app: bool = Field(default=False, description="Is this a system app")
    uninstallable: bool = Field(default=True, description="Can the app be uninstalled")
    webview_url: Optional[str] = Field(None, description="URL for phone UI")
    logo_url: str = Field(..., description="App logo URL")
    app_type: AppType = Field(default=AppType.STANDARD, description="Type of app")
    app_store_id: Optional[str] = Field(None, description="App store identifier")
    developer_id: Optional[str] = Field(None, description="Developer ID (deprecated)")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    permissions: Optional[List[Permission]] = Field(None, description="Required permissions")
    description: Optional[str] = Field(None, description="App description")
    version: Optional[str] = Field(None, description="App version")
    settings: Optional[AppSettings] = Field(None, description="App settings schema")
    tools: Optional[List[ToolSchema]] = Field(None, description="App tools")
    is_public: bool = Field(default=False, description="Is app publicly available")