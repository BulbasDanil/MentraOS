"""
Dashboard models for the MentraOS Python SDK

These models define the structure for dashboard functionality, including
content updates, mode changes, and system dashboard management.
"""

from typing import Protocol, List
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseMessage
from .enums import DashboardMode, AppToCloudMessageType


class DashboardSystemUpdate(BaseMessage):
    """System dashboard section update"""
    type: AppToCloudMessageType = AppToCloudMessageType.DASHBOARD_SYSTEM_UPDATE
    package_name: str = Field(..., description="App package identifier")
    section: str = Field(..., description="Dashboard section: topLeft, topRight, bottomLeft, bottomRight")
    content: str = Field(..., description="Content to display in section")


class DashboardSystemAPI(Protocol):
    """Interface for system dashboard management (only for system dashboard app)"""

    def set_top_left(self, content: str) -> None:
        """Set content for the top left section of the dashboard"""
        ...

    def set_top_right(self, content: str) -> None:
        """Set content for the top right section of the dashboard"""
        ...

    def set_bottom_left(self, content: str) -> None:
        """Set content for the bottom left section of the dashboard"""
        ...

    def set_bottom_right(self, content: str) -> None:
        """Set content for the bottom right section of the dashboard"""
        ...

    def set_view_mode(self, mode: DashboardMode) -> None:
        """Set the current dashboard mode"""
        ...


class DashboardContentAPI(Protocol):
    """Interface for dashboard content management (available to all apps)"""

    def write(self, content: str, targets: List[DashboardMode] = None) -> None:
        """Write content to dashboard

        Args:
            content: Content to display
            targets: Optional list of dashboard modes to target (defaults to [MAIN])
        """
        ...

    def write_to_main(self, content: str) -> None:
        """Write content to main dashboard mode"""
        ...

    def write_to_expanded(self, content: str) -> None:
        """Write content to expanded dashboard mode"""
        ...

    async def get_current_mode(self) -> DashboardMode | str:
        """Get current active dashboard mode"""
        ...

    def on_mode_change(self, callback) -> callable:
        """Register for mode change notifications

        Args:
            callback: Function to call when mode changes

        Returns:
            Cleanup function to unregister callback
        """
        ...


class DashboardAPI(Protocol):
    """Main dashboard API interface"""

    # Content API (available to all apps)
    content: DashboardContentAPI

    # System API (only available for system dashboard app)
    system: DashboardSystemAPI | None