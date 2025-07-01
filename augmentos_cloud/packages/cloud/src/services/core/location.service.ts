import { User, UserI } from '../../models/user.model';
import { sessionService } from '../session/session.service';
import UserSession from '../session/UserSession';
import subscriptionService from '../session/subscription.service';
import { logger as rootLogger } from '../logging/pino-logger';
import WebSocket from 'ws';
import { CloudToAppMessageType, DataStream, LocationUpdate, StreamType } from '@mentra/sdk';

const logger = rootLogger.child({ service: 'location.service' });

const TIER_HIERARCHY = ['reduced', 'threeKilometers', 'kilometer', 'hundredMeters', 'tenMeters', 'high', 'realtime'];

// this service will manage all business logic related to location services,
// including tiered streaming arbitration and intelligent polling
class LocationService {

  // this will be called when an app's subscriptions change
  public async handleSubscriptionChange(userId: string): Promise<void> {
    const user = await User.findOne({ email: userId });
    if (!user) {
      logger.warn({ userId }, "User not found during location subscription change.");
      return;
    }
    
    const previousEffectiveRate = user.effective_location_rate || 'reduced';
    const newEffectiveRate = this._calculateEffectiveRateForUser(user);

    if (newEffectiveRate !== previousEffectiveRate) {
      logger.info({ userId, oldRate: previousEffectiveRate, newRate: newEffectiveRate }, "Effective location rate has changed. Updating database and commanding device.");
      
      user.effective_location_rate = newEffectiveRate;
      await user.save();
      
      const userSession = sessionService.getSessionByUserId(userId);
      if (userSession?.websocket && userSession.websocket.readyState === WebSocket.OPEN) {
        this._sendCommandToDevice(userSession.websocket, 'SET_LOCATION_TIER', { rate: newEffectiveRate });
      } else {
        logger.warn({ userId }, "User session or WebSocket not available to send location tier command.");
      }
    } else {
      logger.info({ userId, rate: newEffectiveRate }, "Location subscriptions changed, but effective rate remains the same. No command sent.");
    }
  }

  // this will be called when an app sends a poll request
  public async handlePollRequest(userId: string, accuracy: string, correlationId: string): Promise<void> {
    const user = await User.findOne({ email: userId });
    if (!user) {
      logger.warn({ userId }, "User not found during location poll request.");
      return;
    }

    const userSession = sessionService.getSessionByUserId(userId);
    if (!userSession) {
      logger.warn({ userId }, "User session not found for poll request.");
      return;
    }
    
    const effectiveRate = user.effective_location_rate || 'reduced';
    const highAccuracyStreamRunning = TIER_HIERARCHY.indexOf(effectiveRate) >= TIER_HIERARCHY.indexOf('high');

    if (highAccuracyStreamRunning) {
        const lastLocation = subscriptionService.getLastLocation(userSession.sessionId);
        if (lastLocation) {
            logger.info({ userId, accuracy }, "Fulfilling poll request from active high-accuracy stream.");
            this._sendPollResponseToTpa(userSession, lastLocation, correlationId);
            return; 
        }
    }

    const maxCacheAge = this._getMaxCacheAgeForAccuracy(accuracy);
    if (user.location?.timestamp) {
        const cacheAge = Date.now() - new Date(user.location.timestamp).getTime();
        if (cacheAge <= maxCacheAge) {
            logger.info({ userId, accuracy, cacheAge, maxCacheAge }, "Fulfilling poll request from cache.");
            this._sendPollResponseToTpa(userSession, user.location, correlationId);
            return;
        }
    }
    
    logger.info({ userId, accuracy }, "No active stream or fresh cache, requesting hardware poll.");
    this._sendCommandToDevice(userSession.websocket, 'REQUEST_SINGLE_LOCATION', { accuracy, correlationId });
  }

  private _getMaxCacheAgeForAccuracy(accuracy: string): number {
    switch (accuracy) {
        case 'realtime': return 1000;
        case 'high': return 10000;
        case 'tenMeters': return 30000;
        case 'hundredMeters': return 60000;
        case 'kilometer': return 300000;
        case 'threeKilometers': return 900000;
        case 'reduced': return 900000;
        default: return 60000;
    }
  }

  private _sendPollResponseToTpa(userSession: UserSession, location: any, correlationId: string): void {
    // This method will need to find the correct App websocket to send the response to.
    // For now, we assume a mechanism exists to relay a message back to all Apps,
    // and the SDK's listener will filter by correlationId.
    const locationUpdatePayload: LocationUpdate = {
        type: StreamType.LOCATION_UPDATE,
        lat: location.latitude || location.lat,
        lng: location.longitude || location.lng,
        correlationId: correlationId
    };

    for (const [packageName, websocket] of userSession.appWebsockets.entries()) {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            const dataStream: DataStream = {
                type: CloudToAppMessageType.DATA_STREAM,
                streamType: StreamType.LOCATION_UPDATE,
                sessionId: `${userSession.userId}-${packageName}`,
                data: locationUpdatePayload,
                timestamp: new Date()
            };
            websocket.send(JSON.stringify(dataStream));
        }
    }
  }

  // this will calculate the highest priority rate from all active subscriptions
  private _calculateEffectiveRateForUser(user: UserI): string {
    const defaultRate = 'reduced';
    if (!user.location_subscriptions || user.location_subscriptions.size === 0) {
      return defaultRate;
    }

    let highestTierIndex = -1;

    for (const subDetails of user.location_subscriptions.values()) {
      const tierIndex = TIER_HIERARCHY.indexOf(subDetails.rate);
      if (tierIndex > highestTierIndex) {
        highestTierIndex = tierIndex;
      }
    }

    return highestTierIndex > -1 ? TIER_HIERARCHY[highestTierIndex] : defaultRate;
  }

  // this will send commands down to the native device client
  private _sendCommandToDevice(ws: WebSocket, type: string, payload: any): void {
    try {
      const message = {
        type: type,
        payload: payload,
        timestamp: new Date().toISOString()
      };
      ws.send(JSON.stringify(message));
      logger.info({ type, payload }, "Successfully sent command to device.");
    } catch (error) {
        logger.error({error, type}, "Failed to send command to device.")
    }
  }
}

// export as a singleton so the rest of the app uses the same instance
export const locationService = new LocationService();
logger.info("Location Service initialized."); 