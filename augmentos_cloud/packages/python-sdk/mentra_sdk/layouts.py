"""
Layout management for the MentraOS Python SDK

Provides methods for displaying content on smart glasses using different
layout types like text walls, cards, and bitmap views.
"""

from typing import Optional, Callable, Awaitable, Any
from .types.layouts import (
    TextWall,
    DoubleTextWall,
    DashboardCard,
    ReferenceCard,
    BitmapView,
    DisplayRequest
)
from .types.enums import ViewType
from .types.messages import AppToCloudMessage
from .logger import get_logger

logger = get_logger(__name__)


class LayoutManager:
    """
    Manages display layouts for smart glasses

    Provides convenient methods for showing different types of content
    on smart glasses displays using various layout formats.
    """

    def __init__(self, session: "AppSession"):
        self._session = session
        self._package_name = session.config.package_name
        self.logger = logger.bind(
            component="LayoutManager",
            package_name=self._package_name,
            session_id=getattr(session, 'session_id', 'unknown')
        )

    async def _send_display_request(
        self,
        layout: Any,
        view: ViewType = ViewType.MAIN,
        duration_ms: Optional[int] = None,
        force_display: bool = False
    ) -> None:
        """
        Send a display request to the smart glasses

        Args:
            layout: Layout object to display
            view: Target view for display
            duration_ms: Display duration in milliseconds
            force_display: Force display even if another app is active
        """
        request = DisplayRequest(
            package_name=self._package_name,
            view=view,
            layout=layout,
            duration_ms=duration_ms,
            force_display=force_display
        )

        await self._session.send(request)

        self.logger.debug(
            "Display request sent",
            layout_type=layout.layout_type,
            view=view,
            duration_ms=duration_ms
        )

    async def show_text_wall(
        self,
        text: str,
        view: ViewType = ViewType.MAIN,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Display a simple text wall

        Args:
            text: Text content to display
            view: Target view for display
            duration_ms: Display duration in milliseconds
        """
        layout = TextWall(text=text)
        await self._send_display_request(layout, view, duration_ms)

    async def show_double_text_wall(
        self,
        top_text: str,
        bottom_text: str,
        view: ViewType = ViewType.MAIN,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Display a two-line text wall

        Args:
            top_text: Text for the top line
            bottom_text: Text for the bottom line
            view: Target view for display
            duration_ms: Display duration in milliseconds
        """
        layout = DoubleTextWall(top_text=top_text, bottom_text=bottom_text)
        await self._send_display_request(layout, view, duration_ms)

    async def show_dashboard_card(
        self,
        left_text: str,
        right_text: str,
        view: ViewType = ViewType.MAIN,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Display a dashboard-style card with left and right text

        Args:
            left_text: Text for the left side
            right_text: Text for the right side
            view: Target view for display
            duration_ms: Display duration in milliseconds
        """
        layout = DashboardCard(left_text=left_text, right_text=right_text)
        await self._send_display_request(layout, view, duration_ms)

    async def show_reference_card(
        self,
        title: str,
        text: str,
        view: ViewType = ViewType.MAIN,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Display a reference card with title and content

        Args:
            title: Card title
            text: Card content text
            view: Target view for display
            duration_ms: Display duration in milliseconds
        """
        layout = ReferenceCard(title=title, text=text)
        await self._send_display_request(layout, view, duration_ms)

    async def show_bitmap_view(
        self,
        data: str,
        view: ViewType = ViewType.MAIN,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Display a custom bitmap/image

        Args:
            data: Base64 encoded image data
            view: Target view for display
            duration_ms: Display duration in milliseconds
        """
        layout = BitmapView(data=data)
        await self._send_display_request(layout, view, duration_ms)

    # Convenience methods with different parameter styles

    async def text(
        self,
        content: str,
        duration: Optional[int] = None,
        view: ViewType = ViewType.MAIN
    ) -> None:
        """
        Convenience method for displaying text

        Args:
            content: Text to display
            duration: Display duration in milliseconds
            view: Target view for display
        """
        await self.show_text_wall(content, view, duration)

    async def card(
        self,
        title: str,
        content: str,
        duration: Optional[int] = None,
        view: ViewType = ViewType.MAIN
    ) -> None:
        """
        Convenience method for displaying a reference card

        Args:
            title: Card title
            content: Card content
            duration: Display duration in milliseconds
            view: Target view for display
        """
        await self.show_reference_card(title, content, view, duration)

    async def split_text(
        self,
        top: str,
        bottom: str,
        duration: Optional[int] = None,
        view: ViewType = ViewType.MAIN
    ) -> None:
        """
        Convenience method for displaying split text

        Args:
            top: Top line text
            bottom: Bottom line text
            duration: Display duration in milliseconds
            view: Target view for display
        """
        await self.show_double_text_wall(top, bottom, view, duration)

    async def dashboard(
        self,
        left: str,
        right: str,
        duration: Optional[int] = None,
        view: ViewType = ViewType.MAIN
    ) -> None:
        """
        Convenience method for displaying dashboard card

        Args:
            left: Left side text
            right: Right side text
            duration: Display duration in milliseconds
            view: Target view for display
        """
        await self.show_dashboard_card(left, right, view, duration)

    async def image(
        self,
        base64_data: str,
        duration: Optional[int] = None,
        view: ViewType = ViewType.MAIN
    ) -> None:
        """
        Convenience method for displaying an image

        Args:
            base64_data: Base64 encoded image data
            duration: Display duration in milliseconds
            view: Target view for display
        """
        await self.show_bitmap_view(base64_data, view, duration)

    # Utility methods

    async def clear(self, view: ViewType = ViewType.MAIN) -> None:
        """
        Clear the display by showing empty text

        Args:
            view: Target view to clear
        """
        await self.show_text_wall("", view, 100)  # Brief empty display

    async def flash_message(
        self,
        message: str,
        duration: int = 2000,
        view: ViewType = ViewType.MAIN
    ) -> None:
        """
        Show a message briefly then clear

        Args:
            message: Message to display
            duration: How long to show the message (default: 2 seconds)
            view: Target view for display
        """
        await self.show_text_wall(message, view, duration)