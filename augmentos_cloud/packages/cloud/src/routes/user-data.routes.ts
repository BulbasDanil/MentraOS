import express from 'express';
import sessionService from '../services/session/session.service';
import { StreamType } from '@mentra/sdk';
import subscriptionService from '../services/session/subscription.service';
import { CloudToAppMessageType } from '@mentra/sdk';

const router = express.Router();

// POST /api/user-data/set-datetime
// Body: { userId: string, datetime: string (ISO format) }
router.post('/set-datetime', (req, res) => {
  const { userId, datetime } = req.body;
  if (!userId || !datetime || isNaN(Date.parse(datetime))) {
    return res.status(400).json({ error: 'Missing or invalid userId or datetime (must be ISO string)' });
  }
  const userSession = sessionService.getSessionByUserId(userId);
  if (!userSession) {
    return res.status(404).json({ error: 'User session not found' });
  }
  // Store the datetime in the session (custom property)
  userSession.userDatetime = datetime;

  // Relay custom_message to all Apps subscribed to custom_message
  const subscribedApps = subscriptionService.getSubscribedApps(userSession, StreamType.CUSTOM_MESSAGE);

  const customMessage = {
    type: CloudToAppMessageType.CUSTOM_MESSAGE,
    action: 'update_datetime',
    payload: {
      datetime: datetime,
      section: 'topLeft'
    },
    timestamp: new Date()
  };
  for (const packageName of subscribedApps) {
    const appWebsocket = userSession.appWebsockets.get(packageName);
    if (appWebsocket && appWebsocket.readyState === 1) {
      appWebsocket.send(JSON.stringify(customMessage));
    }
  }

  res.json({ success: true, userId, datetime });
});

export default router;