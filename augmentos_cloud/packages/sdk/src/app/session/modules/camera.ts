/**
 * 📷 Camera Module
 *
 * Unified camera functionality for App Sessions.
 * Handles both photo requests and RTMP streaming from connected glasses.
 */

import {
  PhotoRequest,
  PhotoData,
  AppToCloudMessageType,
  RtmpStreamRequest,
  RtmpStreamStopRequest,
  RtmpStreamStatus,
  isRtmpStreamStatus
} from '../../../types';
import {
  VideoConfig,
  AudioConfig,
  StreamConfig,
  StreamStatusHandler
} from '../../../types/rtmp-stream';
import { StreamType } from '../../../types/streams';
import { Logger } from 'pino';

/**
 * Options for photo requests
 */
export interface PhotoRequestOptions {
  /** Whether to save the photo to the device gallery */
  saveToGallery?: boolean;
}

/**
 * Configuration options for an RTMP stream
 */
export interface RtmpStreamOptions {
  /** The RTMP URL to stream to (e.g., rtmp://server.example.com/live/stream-key) */
  rtmpUrl: string;
  /** Optional video configuration settings */
  video?: VideoConfig;
  /** Optional audio configuration settings */
  audio?: AudioConfig;
  /** Optional stream configuration settings */
  stream?: StreamConfig;
}

/**
 * 📷 Camera Module Implementation
 *
 * Unified camera management for App Sessions.
 * Provides methods for:
 * - 📸 Requesting photos from glasses
 * - 📹 Starting/stopping RTMP streams
 * - 🔍 Monitoring photo and stream status
 * - 🧹 Cleanup and cancellation
 *
 * @example
 * ```typescript
 * // Request a photo
 * const photoData = await session.camera.requestPhoto({ saveToGallery: true });
 *
 * // Start streaming
 * await session.camera.startStream({ rtmpUrl: 'rtmp://example.com/live/key' });
 *
 * // Monitor stream status
 * session.camera.onStreamStatus((status) => {
 *   console.log('Stream status:', status.status);
 * });
 *
 * // Stop streaming
 * await session.camera.stopStream();
 * ```
 */
export class CameraModule {
  private send: (message: any) => void;
  private packageName: string;
  private sessionId: string;
  private session?: any; // Reference to AppSession
  private logger: Logger;

  // Photo functionality
  /** Map to store pending photo request promises */
  private pendingPhotoRequests = new Map<string, {
    resolve: (value: PhotoData) => void;
    reject: (reason?: any) => void;
  }>();

  // Streaming functionality
  private isStreaming: boolean = false;
  private currentStreamUrl?: string;
  private currentStreamState?: RtmpStreamStatus;

  /**
   * Create a new CameraModule
   *
   * @param packageName - The App package name
   * @param sessionId - The current session ID
   * @param send - Function to send messages to the cloud
   * @param session - Reference to the parent AppSession (optional)
   * @param logger - Logger instance for debugging
   */
  constructor(packageName: string, sessionId: string, send: (message: any) => void, session?: any, logger?: Logger) {
    this.packageName = packageName;
    this.sessionId = sessionId;
    this.send = send;
    this.session = session;
    this.logger = logger || console as any;
  }

  // =====================================
  // 📸 Photo Functionality
  // =====================================

  /**
   * 📸 Request a photo from the connected glasses
   *
   * @param options - Optional configuration for the photo request
   * @returns Promise that resolves with the actual photo data
   *
   * @example
   * ```typescript
   * // Request a photo
   * const photo = await session.camera.requestPhoto();
   * ```
   */
  async requestPhoto(options?: PhotoRequestOptions): Promise<PhotoData> {
    return new Promise((resolve, reject) => {
      try {
        // Generate unique request ID
        const requestId = `photo_req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

        // Store promise resolvers for when we get the response
        this.pendingPhotoRequests.set(requestId, { resolve, reject });

        // Create photo request message
        const message: PhotoRequest = {
          type: AppToCloudMessageType.PHOTO_REQUEST,
          packageName: this.packageName,
          sessionId: this.sessionId,
          requestId,
          timestamp: new Date(),
          saveToGallery: options?.saveToGallery || false
        };

        // Send request to cloud
        this.send(message);

        this.logger.info({ requestId, saveToGallery: options?.saveToGallery }, `📸 Photo request sent`);

        // Set timeout to avoid hanging promises
        const timeoutMs = 30000; // 30 seconds
        if (this.session && this.session.resources) {
          // Use session's resource tracker for automatic cleanup
          this.session.resources.setTimeout(() => {
            if (this.pendingPhotoRequests.has(requestId)) {
              this.pendingPhotoRequests.get(requestId)!.reject(new Error('Photo request timed out'));
              this.pendingPhotoRequests.delete(requestId);
              this.logger.warn({ requestId }, `📸 Photo request timed out`);
            }
          }, timeoutMs);
        } else {
          // Fallback to regular setTimeout if session not available
          setTimeout(() => {
            if (this.pendingPhotoRequests.has(requestId)) {
              this.pendingPhotoRequests.get(requestId)!.reject(new Error('Photo request timed out'));
              this.pendingPhotoRequests.delete(requestId);
              this.logger.warn({ requestId }, `📸 Photo request timed out`);
            }
          }, timeoutMs);
        }
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        reject(new Error(`Failed to request photo: ${errorMessage}`));
      }
    });
  }

  /**
   * 📥 Handle photo received from /photo-upload endpoint
   *
   * This method is called internally when a photo response is received.
   * It resolves the corresponding pending promise with the photo data.
   *
   * @param photoData - The photo data received
   * @internal This method is used internally by AppSession
   */
  handlePhotoReceived(photoData: PhotoData): void {
    const { requestId } = photoData;
    const pendingRequest = this.pendingPhotoRequests.get(requestId);

    if (pendingRequest) {
      this.logger.info({ requestId }, `📸 Photo received for request ${requestId}`);

      // Resolve the promise with the photo data
      pendingRequest.resolve(photoData);

      // Clean up
      this.pendingPhotoRequests.delete(requestId);
    } else {
      this.logger.warn({ requestId }, `📸 Received photo for unknown request ID: ${requestId}`);
    }
  }

  /**
   * 🔍 Check if there's a pending photo request for the given request ID
   *
   * @param requestId - The request ID to check
   * @returns true if there's a pending request
   */
  hasPhotoPendingRequest(requestId: string): boolean {
    return this.pendingPhotoRequests.has(requestId);
  }

  /**
   * 📊 Get the number of pending photo requests
   *
   * @returns Number of pending photo requests
   */
  getPhotoPendingRequestCount(): number {
    return this.pendingPhotoRequests.size;
  }

  /**
   * 📋 Get all pending photo request IDs
   *
   * @returns Array of pending request IDs
   */
  getPhotoPendingRequestIds(): string[] {
    return Array.from(this.pendingPhotoRequests.keys());
  }

  /**
   * ❌ Cancel a pending photo request
   *
   * @param requestId - The request ID to cancel
   * @returns true if the request was cancelled, false if it wasn't found
   */
  cancelPhotoRequest(requestId: string): boolean {
    const pendingRequest = this.pendingPhotoRequests.get(requestId);
    if (pendingRequest) {
      pendingRequest.reject(new Error('Photo request cancelled'));
      this.pendingPhotoRequests.delete(requestId);
      this.logger.info({ requestId }, `📸 Photo request cancelled`);
      return true;
    }
    return false;
  }

  /**
   * 🧹 Cancel all pending photo requests
   *
   * @returns Number of requests that were cancelled
   */
  cancelAllPhotoRequests(): number {
    const count = this.pendingPhotoRequests.size;

    for (const [requestId, { reject }] of this.pendingPhotoRequests) {
      reject(new Error('Photo request cancelled - session cleanup'));
      this.logger.info({ requestId }, `📸 Photo request cancelled during cleanup`);
    }

    this.pendingPhotoRequests.clear();
    return count;
  }

  // =====================================
  // 📹 Streaming Functionality
  // =====================================

  /**
   * 📹 Start an RTMP stream to the specified URL
   *
   * @param options - Configuration options for the stream
   * @returns Promise that resolves when the stream request is sent (not when streaming begins)
   *
   * @example
   * ```typescript
   * await session.camera.startStream({
   *   rtmpUrl: 'rtmp://live.example.com/stream/key',
   *   video: { resolution: '1920x1080', bitrate: 5000 },
   *   audio: { bitrate: 128 }
   * });
   * ```
   */
  async startStream(options: RtmpStreamOptions): Promise<void> {
    this.logger.info({ rtmpUrl: options.rtmpUrl }, `📹 RTMP stream request starting`);

    if (!options.rtmpUrl) {
      throw new Error('rtmpUrl is required');
    }

    if (this.isStreaming) {
      this.logger.error({
        currentStreamUrl: this.currentStreamUrl,
        requestedUrl: options.rtmpUrl
      }, `📹 Already streaming error`);
      throw new Error('Already streaming. Stop the current stream before starting a new one.');
    }

    // Create stream request message
    const message: RtmpStreamRequest = {
      type: AppToCloudMessageType.RTMP_STREAM_REQUEST,
      packageName: this.packageName,
      sessionId: this.sessionId,
      rtmpUrl: options.rtmpUrl,
      video: options.video,
      audio: options.audio,
      stream: options.stream,
      timestamp: new Date()
    };

    // Save stream URL for reference
    this.currentStreamUrl = options.rtmpUrl;

    // Send the request
    try {
      this.send(message);
      this.isStreaming = true;

      this.logger.info({ rtmpUrl: options.rtmpUrl }, `📹 RTMP stream request sent successfully`);
      return Promise.resolve();
    } catch (error) {
      this.logger.error({ error, rtmpUrl: options.rtmpUrl }, `📹 Failed to send RTMP stream request`);
      const errorMessage = error instanceof Error ? error.message : String(error);
      return Promise.reject(new Error(`Failed to request RTMP stream: ${errorMessage}`));
    }
  }

  /**
   * 🛑 Stop the current RTMP stream
   *
   * @returns Promise that resolves when the stop request is sent
   *
   * @example
   * ```typescript
   * await session.camera.stopStream();
   * ```
   */
  async stopStream(): Promise<void> {
    this.logger.info({
      isCurrentlyStreaming: this.isStreaming,
      currentStreamUrl: this.currentStreamUrl
    }, `📹 RTMP stream stop request`);

    if (!this.isStreaming) {
      this.logger.info(`📹 Not streaming - no-op`);
      // Not an error - just a no-op if not streaming
      return Promise.resolve();
    }

    // Create stop request message
    const message: RtmpStreamStopRequest = {
      type: AppToCloudMessageType.RTMP_STREAM_STOP,
      packageName: this.packageName,
      sessionId: this.sessionId,
      streamId: this.currentStreamState?.streamId,  // Include streamId if available
      timestamp: new Date()
    };

    // Send the request
    try {
      this.send(message);
      return Promise.resolve();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return Promise.reject(new Error(`Failed to stop RTMP stream: ${errorMessage}`));
    }
  }

  /**
   * 🔍 Check if currently streaming
   *
   * @returns True if a stream is active or initializing
   */
  isCurrentlyStreaming(): boolean {
    return this.isStreaming;
  }

  /**
   * 📍 Get the URL of the current stream (if any)
   *
   * @returns The RTMP URL of the current stream, or undefined if not streaming
   */
  getCurrentStreamUrl(): string | undefined {
    return this.currentStreamUrl;
  }

  /**
   * 📊 Get the current stream status
   *
   * @returns The current stream status, or undefined if not available
   */
  getStreamStatus(): RtmpStreamStatus | undefined {
    return this.currentStreamState;
  }

  /**
   * 📺 Subscribe to RTMP stream status updates
   * This uses the standard stream subscription mechanism
   */
  subscribeToStreamStatusUpdates(): void {
    if (this.session) {
      this.session.subscribe(StreamType.RTMP_STREAM_STATUS);
    } else {
      this.logger.error('Cannot subscribe to status updates: session reference not available');
    }
  }

  /**
   * 📺 Unsubscribe from RTMP stream status updates
   */
  unsubscribeFromStreamStatusUpdates(): void {
    if (this.session) {
      this.session.unsubscribe(StreamType.RTMP_STREAM_STATUS);
    }
  }

  /**
   * 👂 Listen for stream status updates using the standard event system
   * @param handler - Function to call when stream status changes
   * @returns Cleanup function to remove the handler
   *
   * @example
   * ```typescript
   * const cleanup = session.camera.onStreamStatus((status) => {
   *   console.log('Stream status:', status.status);
   *   if (status.status === 'error') {
   *     console.error('Stream error:', status.errorDetails);
   *   }
   * });
   *
   * // Later, cleanup the listener
   * cleanup();
   * ```
   */
  onStreamStatus(handler: StreamStatusHandler): () => void {
    if (!this.session) {
      this.logger.error('Cannot listen for status updates: session reference not available');
      return () => {};
    }

    this.subscribeToStreamStatusUpdates();
    return this.session.on(StreamType.RTMP_STREAM_STATUS, handler);
  }

  /**
   * 🔄 Update internal stream state based on a status message
   * For internal use by AppSession
   * @param message - The status message from the cloud
   * @internal This method is used internally by AppSession
   */
  updateStreamState(message: any): void {
    this.logger.debug({
      messageType: message?.type,
      messageStatus: message?.status,
      currentIsStreaming: this.isStreaming
    }, `📹 Stream state update`);

    // Verify this is a valid stream response
    if (!isRtmpStreamStatus(message)) {
      this.logger.warn({ message }, `📹 Received invalid stream status message`);
      return;
    }

    // Convert to StreamStatus format
    const status: RtmpStreamStatus = {
      type: message.type,
      streamId: message.streamId,
      status: message.status,
      errorDetails: message.errorDetails,
      appId: message.appId,
      stats: message.stats,
      timestamp: message.timestamp || new Date()
    };

    this.logger.info({
      streamId: status.streamId,
      oldStatus: this.currentStreamState?.status,
      newStatus: status.status,
      wasStreaming: this.isStreaming
    }, `📹 Stream status processed`);

    // Update local state based on status
    if (status.status === 'stopped' || status.status === 'error' || status.status === 'timeout') {
      this.logger.info({
        status: status.status,
        wasStreaming: this.isStreaming
      }, `📹 Stream stopped - updating local state`);
      this.isStreaming = false;
      this.currentStreamUrl = undefined;
    }

    // Save the latest status
    this.currentStreamState = status;
  }

  // =====================================
  // 🔧 General Utilities
  // =====================================

  /**
   * 🔧 Update the session ID (used when reconnecting)
   *
   * @param newSessionId - The new session ID
   * @internal This method is used internally by AppSession
   */
  updateSessionId(newSessionId: string): void {
    this.sessionId = newSessionId;
  }

  /**
   * 🧹 Cancel all pending requests and clean up resources
   *
   * @returns Object with counts of cancelled requests
   */
  cancelAllRequests(): { photoRequests: number } {
    const photoRequests = this.cancelAllPhotoRequests();

    // Stop streaming if active
    if (this.isStreaming) {
      this.stopStream().catch((error) => {
        this.logger.error({ error }, 'Error stopping stream during cleanup');
      });
    }

    return { photoRequests };
  }
}

// Re-export types for convenience
export {
  VideoConfig,
  AudioConfig,
  StreamConfig,
  StreamStatusHandler
};