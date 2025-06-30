"""
MentraOS Python SDK

A modern, async-first Python SDK for building smartglasses applications on MentraOS.
Provides type-safe WebSocket communication, layout management, event handling, and more.

Example usage:
    from mentra_sdk import AppServer, AppSession, AppServerConfig

    class MyAwesomeApp(AppServer):
        async def on_session(self, session: AppSession, session_id: str, user_id: str):
            await session.layouts.show_text_wall("Hello from Python!")

            @session.events.on_transcription
            async def handle_transcription(data):
                await session.layouts.show_text_wall(f"You said: {data.text}")
"""

__version__ = "2.0.0"

# Core classes
from .app_server import AppServer
from .app_session import AppSession

# Configuration models
from .types.config import AppServerConfig, AppSessionConfig

# Key data types developers commonly need
from .types.events import TranscriptionData, ButtonPress, HeadPosition
from .types.layouts import TextWall, DoubleTextWall, ReferenceCard
from .types.enums import StreamType, LayoutType, ViewType

# Backward compatibility aliases (deprecated)
TpaServer = AppServer  # Deprecated
TpaSession = AppSession  # Deprecated

__all__ = [
    # Core classes
    "AppServer",
    "AppSession",
    # Configuration
    "AppServerConfig",
    "AppSessionConfig",
    # Common data types
    "TranscriptionData",
    "ButtonPress",
    "HeadPosition",
    "TextWall",
    "DoubleTextWall",
    "ReferenceCard",
    # Enums
    "StreamType",
    "LayoutType",
    "ViewType",
    # Deprecated (for compatibility)
    "TpaServer",
    "TpaSession",
]