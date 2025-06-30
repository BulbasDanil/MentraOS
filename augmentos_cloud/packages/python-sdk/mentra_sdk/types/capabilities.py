"""
Device capability models for the MentraOS Python SDK

These models describe the hardware capabilities and features of smart glasses
devices, including cameras, displays, sensors, and input methods.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CameraCapabilities(BaseModel):
    """Camera hardware capabilities"""
    resolution: Optional[Dict[str, int]] = Field(None, description="Camera resolution (width, height)")
    has_hdr: bool = Field(default=False, description="Supports HDR capture")
    has_focus: bool = Field(default=False, description="Supports autofocus")
    video: "VideoCapabilities" = Field(..., description="Video recording capabilities")


class VideoCapabilities(BaseModel):
    """Video recording capabilities"""
    can_record: bool = Field(..., description="Supports video recording")
    can_stream: bool = Field(..., description="Supports live streaming")
    supported_stream_types: Optional[List[str]] = Field(None, description="Supported streaming protocols")
    supported_resolutions: Optional[List[Dict[str, int]]] = Field(
        None,
        description="Supported video resolutions"
    )


class ScreenCapabilities(BaseModel):
    """Display screen capabilities"""
    count: int = Field(default=1, description="Number of displays")
    is_color: bool = Field(default=False, description="Supports color display")
    color: Optional[str] = Field(None, description="Color type: 'green', 'full_color', 'palette'")
    can_display_bitmap: bool = Field(default=False, description="Supports bitmap/image display")
    resolution: Optional[Dict[str, int]] = Field(None, description="Screen resolution")
    field_of_view: Optional[Dict[str, float]] = Field(None, description="FOV in degrees")
    max_text_lines: Optional[int] = Field(None, description="Maximum text lines")
    adjust_brightness: bool = Field(default=False, description="Supports brightness adjustment")


class MicrophoneCapabilities(BaseModel):
    """Microphone capabilities"""
    count: int = Field(default=1, description="Number of microphones")
    has_vad: bool = Field(default=False, description="Supports Voice Activity Detection")


class SpeakerCapabilities(BaseModel):
    """Speaker/audio output capabilities"""
    count: int = Field(default=1, description="Number of speakers")
    is_private: bool = Field(default=False, description="Private audio (e.g., bone conduction)")


class IMUCapabilities(BaseModel):
    """Inertial Measurement Unit capabilities"""
    axis_count: int = Field(default=6, description="Number of axes (3=accel, 6=accel+gyro, 9=full)")
    has_accelerometer: bool = Field(default=True, description="Has accelerometer")
    has_compass: bool = Field(default=False, description="Has compass/magnetometer")
    has_gyroscope: bool = Field(default=True, description="Has gyroscope")


class ButtonInput(BaseModel):
    """Individual button input definition"""
    type: str = Field(..., description="Input type: 'press', 'swipe1d', 'swipe2d'")
    events: List[str] = Field(..., description="Supported events")
    is_capacitive: bool = Field(default=False, description="Capacitive touch button")


class ButtonCapabilities(BaseModel):
    """Physical button input capabilities"""
    count: int = Field(default=0, description="Number of buttons")
    buttons: Optional[List[ButtonInput]] = Field(None, description="Button definitions")


class Light(BaseModel):
    """Individual light definition"""
    is_full_color: bool = Field(..., description="Supports full color")
    color: Optional[str] = Field(None, description="Color type if not full color")


class LightCapabilities(BaseModel):
    """LED/light capabilities"""
    count: int = Field(default=0, description="Number of lights")
    lights: Optional[List[Light]] = Field(None, description="Light definitions")


class PowerCapabilities(BaseModel):
    """Power and battery capabilities"""
    has_external_battery: bool = Field(..., description="Has external battery (case/puck)")


class Capabilities(BaseModel):
    """Complete device capability profile"""
    model_name: str = Field(..., description="Device model name")

    # Camera capabilities
    has_camera: bool = Field(..., description="Device has camera")
    camera: Optional[CameraCapabilities] = Field(None, description="Camera capabilities")

    # Screen capabilities
    has_screen: bool = Field(..., description="Device has display")
    screen: Optional[ScreenCapabilities] = Field(None, description="Screen capabilities")

    # Microphone capabilities
    has_microphone: bool = Field(..., description="Device has microphone")
    microphone: Optional[MicrophoneCapabilities] = Field(None, description="Microphone capabilities")

    # Speaker capabilities
    has_speaker: bool = Field(..., description="Device has speaker")
    speaker: Optional[SpeakerCapabilities] = Field(None, description="Speaker capabilities")

    # IMU capabilities
    has_imu: bool = Field(..., description="Device has IMU sensors")
    imu: Optional[IMUCapabilities] = Field(None, description="IMU capabilities")

    # Button capabilities
    has_button: bool = Field(..., description="Device has physical buttons")
    button: Optional[ButtonCapabilities] = Field(None, description="Button capabilities")

    # Light capabilities
    has_light: bool = Field(..., description="Device has LED lights")
    light: Optional[LightCapabilities] = Field(None, description="Light capabilities")

    # Power capabilities
    power: PowerCapabilities = Field(..., description="Power capabilities")

    # WiFi capabilities
    has_wifi: bool = Field(..., description="Device has WiFi connectivity")


# Fix forward reference
CameraCapabilities.model_rebuild()