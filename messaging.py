import os
import requests
from dotenv import load_dotenv

load_dotenv()
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") 
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") 

'''
def send_whatsapp_message(recipient_id, message_text):
    print("📦 PHONE_NUMBER_ID:", PHONE_NUMBER_ID)
    print("🔐 ACCESS_TOKEN:", ACCESS_TOKEN if ACCESS_TOKEN else "None")

    message_text = str(message_text)

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
'''
def send_whatsapp_message(recipient_id, message_text):
    print("📦 PHONE_NUMBER_ID:", PHONE_NUMBER_ID)
    print("🔐 ACCESS_TOKEN:", ACCESS_TOKEN if ACCESS_TOKEN else "None")

    # ✅ Cast message_text safely
    try:
        message_text = str(message_text)
    except Exception as e:
        print(f"❌ Failed to cast message_text to string: {e}")
        message_text = "Message formatting error."

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
    print("🧪 messaging.py - Final message_text type:", type(message_text))
    print("🧪 messaging.py - First 200 characters:", repr(message_text[:200]))

    try:
        response = requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"❌ Exception during requests.post: {e}")
        return

    if response.ok:
        print(f"✅ Sent message to {recipient_id}")
    else:
        print(f"❌ Failed to send message: {response.status_code} {response.text}")
