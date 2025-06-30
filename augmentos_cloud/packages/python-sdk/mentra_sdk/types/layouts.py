"""
Layout models for the MentraOS Python SDK

These models define the structure of different display layouts that can be
shown on smart glasses, including text walls, cards, and bitmap displays.
"""

from typing import Optional, Union
from pydantic import BaseModel, Field
from .base import BaseMessage
from .enums import LayoutType, ViewType, AppToCloudMessageType


class TextWall(BaseModel):
    """Simple text display layout"""
    layout_type: LayoutType = LayoutType.TEXT_WALL
    text: str = Field(..., description="Text content to display")


class DoubleTextWall(BaseModel):
    """Two-line text display layout"""
    layout_type: LayoutType = LayoutType.DOUBLE_TEXT_WALL
    top_text: str = Field(..., description="Text for the top line")
    bottom_text: str = Field(..., description="Text for the bottom line")


class DashboardCard(BaseModel):
    """Dashboard-style card with left and right text"""
    layout_type: LayoutType = LayoutType.DASHBOARD_CARD
    left_text: str = Field(..., description="Text for the left side")
    right_text: str = Field(..., description="Text for the right side")


class ReferenceCard(BaseModel):
    """Reference card with title and content"""
    layout_type: LayoutType = LayoutType.REFERENCE_CARD
    title: str = Field(..., description="Card title")
    text: str = Field(..., description="Card content text")


class BitmapView(BaseModel):
    """Custom bitmap/image display"""
    layout_type: LayoutType = LayoutType.BITMAP_VIEW
    data: str = Field(..., description="Base64 encoded image data")


# Union type for all possible layouts
Layout = Union[
    TextWall,
    DoubleTextWall,
    DashboardCard,
    ReferenceCard,
    BitmapView
]


class DisplayRequest(BaseMessage):
    """Request to display content on smart glasses"""
    type: AppToCloudMessageType = AppToCloudMessageType.DISPLAY_REQUEST
    package_name: str = Field(..., description="App package name")
    view: ViewType = Field(..., description="Target view for display")
    layout: Layout = Field(..., description="Layout content to display")
    duration_ms: Optional[int] = Field(None, description="Display duration in milliseconds")
    force_display: bool = Field(default=False, description="Force display even if another app is active")

    class Config:
        # Enable discriminator for layout union
        use_enum_values = True