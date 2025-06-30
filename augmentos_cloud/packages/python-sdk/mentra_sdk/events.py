"""
Event management for the MentraOS Python SDK

Provides pub/sub event handling for real-time data streams from MentraOS,
including transcription, sensor data, and user interactions.
"""

import asyncio
from collections import defaultdict
from typing import Callable, List, Dict, Any, Optional, Union, Awaitable
import inspect

from .types.enums import StreamType
from .types.events import (
    TranscriptionData,
    TranslationData,
    ButtonPress,
    HeadPosition,
    AudioChunk,
    PhoneNotification,
    LocationUpdate,
    VpsCoordinates,
    CalendarEvent,
    Vad,
    GlassesBatteryUpdate,
    PhoneBatteryUpdate,
    CustomMessage,
    PhotoTaken
)
from .utils import is_valid_language_code, create_transcription_stream, create_translation_stream
from .logger import get_logger

logger = get_logger(__name__)

# Type aliases for event handlers
EventHandler = Callable[[Any], Union[None, Awaitable[None]]]
CleanupFunction = Callable[[], None]


class EventManager:
    """
    Manages event subscriptions and emissions for MentraOS data streams

    Provides a pub/sub system for handling real-time data from smart glasses,
    with support for both sync and async event handlers.
    """

    def __init__(self, session: "AppSession"):
        self._session = session
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._last_transcription_cleanup: Optional[CleanupFunction] = None
        self._last_translation_cleanup: Optional[CleanupFunction] = None
        self.logger = logger.bind(
            component="EventManager",
            session_id=getattr(session, 'session_id', 'unknown')
        )

    async def _ensure_subscription(self, stream_type: str) -> None:
        """
        Ensure the session is subscribed to a stream type

        Args:
            stream_type: Stream type to subscribe to
        """
        if hasattr(self._session, 'subscribe'):
            await self._session.subscribe(stream_type)

    def _add_handler(self, event_type: str, handler: EventHandler) -> CleanupFunction:
        """
        Add an event handler for a specific event type

        Args:
            event_type: Type of event to handle
            handler: Handler function (sync or async)

        Returns:
            Cleanup function to remove the handler
        """
        self._handlers[event_type].append(handler)

        # Subscribe to the stream if this is the first handler
        if len(self._handlers[event_type]) == 1:
            # Schedule subscription for next event loop iteration
            asyncio.create_task(self._ensure_subscription(event_type))

        def cleanup():
            try:
                self._handlers[event_type].remove(handler)
                # If no more handlers, could unsubscribe from stream
                if len(self._handlers[event_type]) == 0:
                    del self._handlers[event_type]
            except ValueError:
                pass  # Handler already removed

        return cleanup

    async def emit(self, event_type: str, data: Any) -> None:
        """
        Emit an event to all registered handlers

        Args:
            event_type: Type of event being emitted
            data: Event data payload
        """
        if event_type not in self._handlers:
            return

        handlers = self._handlers[event_type].copy()  # Avoid modification during iteration

        # Execute all handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    tasks.append(handler(data))
                else:
                    # Run sync handlers in thread pool to avoid blocking
                    tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, data))
            except Exception as e:
                self.logger.error(
                    "Error in event handler",
                    event_type=event_type,
                    error=str(e),
                    exc_info=True
                )

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error("Error executing event handlers", error=str(e))

    # Convenience methods for common event types

    def on_transcription(self, handler: Callable[[TranscriptionData], Any]) -> CleanupFunction:
        """
        Listen for transcription events (default language: en-US)

        Args:
            handler: Function to handle transcription data

        Returns:
            Cleanup function to remove the handler
        """
        return self.on_transcription_for_language("en-US", handler)

    def on_transcription_for_language(
        self,
        language: str,
        handler: Callable[[TranscriptionData], Any]
    ) -> CleanupFunction:
        """
        Listen for transcription events in a specific language

        Args:
            language: Language code (e.g., "en-US", "es-ES")
            handler: Function to handle transcription data

        Returns:
            Cleanup function to remove the handler
        """
        if not is_valid_language_code(language):
            raise ValueError(f"Invalid language code: {language}")

        # Clean up previous language subscription
        if self._last_transcription_cleanup:
            self._last_transcription_cleanup()

        stream_type = create_transcription_stream(language)
        self._last_transcription_cleanup = self._add_handler(stream_type, handler)
        return self._last_transcription_cleanup

    def on_translation_for_language(
        self,
        source_language: str,
        target_language: str,
        handler: Callable[[TranslationData], Any]
    ) -> CleanupFunction:
        """
        Listen for translation events for a specific language pair

        Args:
            source_language: Source language code (e.g., "es-ES")
            target_language: Target language code (e.g., "en-US")
            handler: Function to handle translation data

        Returns:
            Cleanup function to remove the handler
        """
        if not is_valid_language_code(source_language):
            raise ValueError(f"Invalid source language code: {source_language}")
        if not is_valid_language_code(target_language):
            raise ValueError(f"Invalid target language code: {target_language}")

        # Clean up previous translation subscription
        if self._last_translation_cleanup:
            self._last_translation_cleanup()

        stream_type = create_translation_stream(source_language, target_language)
        self._last_translation_cleanup = self._add_handler(stream_type, handler)
        return self._last_translation_cleanup

    def on_button_press(self, handler: Callable[[ButtonPress], Any]) -> CleanupFunction:
        """Listen for button press events"""
        return self._add_handler(StreamType.BUTTON_PRESS, handler)

    def on_head_position(self, handler: Callable[[HeadPosition], Any]) -> CleanupFunction:
        """Listen for head position events"""
        return self._add_handler(StreamType.HEAD_POSITION, handler)

    def on_phone_notification(self, handler: Callable[[PhoneNotification], Any]) -> CleanupFunction:
        """Listen for phone notification events"""
        return self._add_handler(StreamType.PHONE_NOTIFICATION, handler)

    def on_audio_chunk(self, handler: Callable[[AudioChunk], Any]) -> CleanupFunction:
        """Listen for audio chunk events"""
        return self._add_handler(StreamType.AUDIO_CHUNK, handler)

    def on_location_update(self, handler: Callable[[LocationUpdate], Any]) -> CleanupFunction:
        """Listen for location update events"""
        return self._add_handler(StreamType.LOCATION_UPDATE, handler)

    def on_vps_coordinates(self, handler: Callable[[VpsCoordinates], Any]) -> CleanupFunction:
        """Listen for VPS coordinate events"""
        return self._add_handler(StreamType.VPS_COORDINATES, handler)

    def on_calendar_event(self, handler: Callable[[CalendarEvent], Any]) -> CleanupFunction:
        """Listen for calendar events"""
        return self._add_handler(StreamType.CALENDAR_EVENT, handler)

    def on_voice_activity(self, handler: Callable[[Vad], Any]) -> CleanupFunction:
        """Listen for voice activity detection events"""
        return self._add_handler(StreamType.VAD, handler)

    def on_glasses_battery(self, handler: Callable[[GlassesBatteryUpdate], Any]) -> CleanupFunction:
        """Listen for glasses battery update events"""
        return self._add_handler(StreamType.GLASSES_BATTERY_UPDATE, handler)

    def on_phone_battery(self, handler: Callable[[PhoneBatteryUpdate], Any]) -> CleanupFunction:
        """Listen for phone battery update events"""
        return self._add_handler(StreamType.PHONE_BATTERY_UPDATE, handler)

    def on_photo_taken(self, handler: Callable[[PhotoTaken], Any]) -> CleanupFunction:
        """Listen for photo taken events"""
        return self._add_handler(StreamType.PHOTO_TAKEN, handler)

    def on_custom_message(
        self,
        action: str,
        handler: Callable[[Any], Any]
    ) -> CleanupFunction:
        """
        Listen for custom messages with a specific action

        Args:
            action: Action identifier to filter by
            handler: Function to handle the message payload

        Returns:
            Cleanup function to remove the handler
        """
        def message_handler(message: CustomMessage):
            if message.action == action:
                if inspect.iscoroutinefunction(handler):
                    return handler(message.payload)
                else:
                    return handler(message.payload)

        return self._add_handler("custom_message", message_handler)

    def on(self, event_type: str, handler: EventHandler) -> CleanupFunction:
        """
        Generic event handler registration

        Args:
            event_type: Type of event to handle
            handler: Handler function (sync or async)

        Returns:
            Cleanup function to remove the handler
        """
        return self._add_handler(event_type, handler)

    # System event handlers (for session lifecycle)

    def on_connected(self, handler: Callable[[Any], Any]) -> CleanupFunction:
        """Listen for connection events"""
        return self._add_handler("connected", handler)

    def on_disconnected(self, handler: Callable[[Any], Any]) -> CleanupFunction:
        """Listen for disconnection events"""
        return self._add_handler("disconnected", handler)

    def on_error(self, handler: Callable[[Exception], Any]) -> CleanupFunction:
        """Listen for error events"""
        return self._add_handler("error", handler)

    def on_settings_update(self, handler: Callable[[Any], Any]) -> CleanupFunction:
        """Listen for settings update events"""
        return self._add_handler("settings_update", handler)

    def on_setting_change(
        self,
        key: str,
        handler: Callable[[Any, Any], Any]
    ) -> CleanupFunction:
        """
        Listen for changes to a specific setting

        Args:
            key: Setting key to monitor
            handler: Function called with (new_value, previous_value)

        Returns:
            Cleanup function to remove the handler
        """
        previous_value = None

        def settings_handler(settings):
            nonlocal previous_value
            try:
                setting = next((s for s in settings if s.key == key), None)
                if setting:
                    new_value = setting.value
                    if new_value != previous_value:
                        if inspect.iscoroutinefunction(handler):
                            return handler(new_value, previous_value)
                        else:
                            return handler(new_value, previous_value)
                        previous_value = new_value
            except Exception as e:
                self.logger.error(f"Error in setting change handler for key '{key}'", error=str(e))

        # Listen to both settings_update and connected events
        cleanup1 = self.on_settings_update(settings_handler)
        cleanup2 = self.on_connected(settings_handler)

        def combined_cleanup():
            cleanup1()
            cleanup2()

        return combined_cleanup