from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

def format_panchang_message(vaara, timestamp, tithi, nakshatra):
    """
    Formats Panchang details into a structured WhatsApp message.
    """
    return f"""
🌞 *Daily Panchang Update* 🌙

📅 *Date/Time:* {timestamp}
🗓️ *Vaara:* {vaara}

📖 *Tithi Details:*
- Name: {tithi['name']}
- Paksha: {tithi['paksha']}
- Start: {tithi['start']}
- End: {tithi['end']}

✨ *Nakshatra Details:*
- Name: {nakshatra['name']}
- Start: {nakshatra['start']}
- End: {nakshatra['end']}

🙏 Stay blessed and have an auspicious day! 🌟
"""

def send_whatsapp_message(to, vaara, timestamp, tithi, nakshatra):
    """
    Sends a formatted Panchang message and an audio file using Twilio API.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_body = format_panchang_message(vaara, timestamp, tithi, nakshatra)

        # Replace with your ngrok public URL
        audio_url = "https://purely-actual-marmoset.ngrok-free.app/static/audio/nakshatra/Revati.mp3"

        # Send text message
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=f'whatsapp:{to}'
        )

        # Send audio file
        media_message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            media_url=audio_url,
            to=f'whatsapp:{to}'
        )

        return {"status": "success", "sid": message.sid, "media_sid": media_message.sid}
    except Exception as e:
        return {"status": "error", "error": str(e)}




