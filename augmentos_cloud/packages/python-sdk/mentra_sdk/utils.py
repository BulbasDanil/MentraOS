"""
Utility classes and functions for the MentraOS Python SDK

Provides helper classes for resource management, cleanup handling,
and other common functionality used throughout the SDK.
"""

import asyncio
import weakref
from typing import Callable, List, Optional, Any, Union, Protocol
from contextlib import asynccontextmanager
import uuid


class Disposable(Protocol):
    """Protocol for objects that can be disposed/cleaned up"""
    def dispose(self) -> None:
        """Dispose of the resource"""
        ...


class AsyncDisposable(Protocol):
    """Protocol for objects that can be disposed asynchronously"""
    async def dispose(self) -> None:
        """Dispose of the resource asynchronously"""
        ...


CleanupFunction = Callable[[], None]
AsyncCleanupFunction = Callable[[], Any]  # Can return None or Awaitable


class ResourceTracker:
    """
    Tracks resources and provides cleanup functionality

    Similar to the TypeScript ResourceTracker but with Python patterns.
    Can be used as a context manager for automatic cleanup.
    """

    def __init__(self):
        self._cleanup_functions: List[CleanupFunction] = []
        self._async_cleanup_functions: List[AsyncCleanupFunction] = []
        self._timers: List[asyncio.TimerHandle] = []
        self._tasks: weakref.WeakSet = weakref.WeakSet()
        self._disposed = False

    def track(self, cleanup: CleanupFunction) -> CleanupFunction:
        """
        Track a cleanup function

        Args:
            cleanup: Function to call during cleanup

        Returns:
            The cleanup function (for convenience)
        """
        if self._disposed:
            raise RuntimeError("ResourceTracker has been disposed")

        self._cleanup_functions.append(cleanup)
        return cleanup

    def track_async(self, cleanup: AsyncCleanupFunction) -> AsyncCleanupFunction:
        """
        Track an async cleanup function

        Args:
            cleanup: Async function to call during cleanup

        Returns:
            The cleanup function (for convenience)
        """
        if self._disposed:
            raise RuntimeError("ResourceTracker has been disposed")

        self._async_cleanup_functions.append(cleanup)
        return cleanup

    def track_disposable(self, disposable: Union[Disposable, AsyncDisposable]) -> CleanupFunction:
        """
        Track a disposable object

        Args:
            disposable: Object with dispose() method

        Returns:
            Cleanup function that calls dispose()
        """
        if hasattr(disposable, 'dispose'):
            if asyncio.iscoroutinefunction(disposable.dispose):
                return self.track_async(disposable.dispose)
            else:
                return self.track(disposable.dispose)
        else:
            raise ValueError("Object does not have a dispose method")

    def track_timer(self, timer: asyncio.TimerHandle) -> CleanupFunction:
        """
        Track an asyncio timer

        Args:
            timer: Timer handle to track

        Returns:
            Cleanup function that cancels the timer
        """
        self._timers.append(timer)

        def cleanup():
            if not timer.cancelled():
                timer.cancel()

        return self.track(cleanup)

    def track_task(self, task: asyncio.Task) -> asyncio.Task:
        """
        Track an asyncio task

        Args:
            task: Task to track

        Returns:
            The task itself
        """
        self._tasks.add(task)
        return task

    def set_timeout(self, callback: Callable, delay: float) -> asyncio.TimerHandle:
        """
        Create and track a timeout

        Args:
            callback: Function to call
            delay: Delay in seconds

        Returns:
            Timer handle
        """
        timer = asyncio.get_event_loop().call_later(delay, callback)
        self.track_timer(timer)
        return timer

    def set_interval(self, callback: Callable, interval: float) -> CleanupFunction:
        """
        Create and track an interval

        Args:
            callback: Function to call repeatedly
            interval: Interval in seconds

        Returns:
            Cleanup function to stop the interval
        """
        cancelled = False

        def interval_callback():
            if not cancelled:
                callback()
                self.set_timeout(interval_callback, interval)

        def cancel():
            nonlocal cancelled
            cancelled = True

        self.set_timeout(interval_callback, interval)
        return self.track(cancel)

    def dispose(self) -> None:
        """Synchronously dispose of all tracked resources"""
        if self._disposed:
            return

        self._disposed = True

        # Cancel all timers
        for timer in self._timers:
            if not timer.cancelled():
                timer.cancel()

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Run all cleanup functions
        for cleanup in self._cleanup_functions:
            try:
                cleanup()
            except Exception as e:
                # Log but don't let one cleanup failure stop others
                print(f"Error in cleanup function: {e}")

        # Clear lists
        self._cleanup_functions.clear()
        self._async_cleanup_functions.clear()
        self._timers.clear()

    async def dispose_async(self) -> None:
        """Asynchronously dispose of all tracked resources"""
        if self._disposed:
            return

        self._disposed = True

        # Cancel all timers
        for timer in self._timers:
            if not timer.cancelled():
                timer.cancel()

        # Cancel all tasks and wait for them
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"Error waiting for task: {e}")

        # Run all sync cleanup functions
        for cleanup in self._cleanup_functions:
            try:
                cleanup()
            except Exception as e:
                print(f"Error in cleanup function: {e}")

        # Run all async cleanup functions
        for cleanup in self._async_cleanup_functions:
            try:
                result = cleanup()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"Error in async cleanup function: {e}")

        # Clear lists
        self._cleanup_functions.clear()
        self._async_cleanup_functions.clear()
        self._timers.clear()

    @property
    def disposed(self) -> bool:
        """Check if the tracker has been disposed"""
        return self._disposed

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disposes resources"""
        self.dispose()


@asynccontextmanager
async def async_resource_tracker():
    """
    Async context manager for ResourceTracker

    Usage:
        async with async_resource_tracker() as tracker:
            tracker.track(some_cleanup_function)
            # ... do work ...
        # Resources are automatically cleaned up
    """
    tracker = ResourceTracker()
    try:
        yield tracker
    finally:
        await tracker.dispose_async()


def generate_id() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())


def ws_url_to_http_url(ws_url: str) -> str:
    """
    Convert WebSocket URL to HTTP URL

    Args:
        ws_url: WebSocket URL (ws:// or wss://)

    Returns:
        HTTP URL (http:// or https://)
    """
    if ws_url.startswith("wss://"):
        return ws_url.replace("wss://", "https://", 1)
    elif ws_url.startswith("ws://"):
        return ws_url.replace("ws://", "http://", 1)
    else:
        raise ValueError(f"Invalid WebSocket URL: {ws_url}")


def is_valid_language_code(code: str) -> bool:
    """
    Check if a language code is valid

    Args:
        code: Language code to validate (e.g., "en-US")

    Returns:
        True if valid, False otherwise
    """
    # Basic validation - should be format like "en" or "en-US"
    if not code or not isinstance(code, str):
        return False

    parts = code.split("-")
    if len(parts) == 1:
        # Just language code like "en"
        return len(parts[0]) == 2 and parts[0].isalpha()
    elif len(parts) == 2:
        # Language and region like "en-US"
        return (len(parts[0]) == 2 and parts[0].isalpha() and
                len(parts[1]) == 2 and parts[1].isalpha())

    return False


def create_transcription_stream(language: str) -> str:
    """
    Create a language-specific transcription stream identifier

    Args:
        language: Language code (e.g., "en-US")

    Returns:
        Stream identifier
    """
    if not is_valid_language_code(language):
        raise ValueError(f"Invalid language code: {language}")

    return f"transcription:{language}"


def create_translation_stream(source_language: str, target_language: str) -> str:
    """
    Create a translation stream identifier

    Args:
        source_language: Source language code
        target_language: Target language code

    Returns:
        Stream identifier
    """
    if not is_valid_language_code(source_language):
        raise ValueError(f"Invalid source language code: {source_language}")
    if not is_valid_language_code(target_language):
        raise ValueError(f"Invalid target language code: {target_language}")

    return f"translation:{source_language}:{target_language}"