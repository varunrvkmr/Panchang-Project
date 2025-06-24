# messaging.py

import os
import requests
import logging
from dotenv import load_dotenv

# Load env early
load_dotenv()

WHATSAPP_API_URL   = "https://graph.facebook.com/v18.0"
PHONE_NUMBER_ID    = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN       = os.getenv("WHATSAPP_ACCESS_TOKEN")
URL                = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"

# Configure logging if not already configured by Flask
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

def send_whatsapp_message(recipient_id: str, message_text: str):
    """
    Sends a WhatsApp text message via the Graph API.
    Raises an HTTPError on any non-2xx response.
    """
    # Ensure it's a string
    try:
        message_text = str(message_text)
    except Exception as e:
        logger.error(f"Failed to stringify message_text: {e}")
        message_text = "🚨 Message formatting error."

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    logger.debug(f"Sending to {recipient_id}: {message_text!r}")
    resp = requests.post(URL, headers=headers, json=payload)

    if resp.ok:
        logger.info(f"✅ WhatsApp message sent to {recipient_id}: {resp.json()}")
    else:
        # Log full error and then raise so caller can handle/fail
        logger.error(f"❌ WhatsApp API error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
