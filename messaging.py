import os
import requests

WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")  # e.g., "628578460336829"
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")  # Your long-lived token from Meta

def send_whatsapp_message(recipient_id, message_text):
    url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        print(f"✅ Sent message to {recipient_id}")
    else:
        print(f"❌ Failed to send message: {response.status_code} {response.text}")
