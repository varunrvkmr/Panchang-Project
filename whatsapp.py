# whatsapp.py
from flask import request
from twilio.twiml.messaging_response import MessagingResponse

def handle_whatsapp_message():
    msg_body = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From')

    response = MessagingResponse()
    msg = response.message()

    if msg_body == 'start':
        msg.body("Welcome! Please reply with your timezone (e.g., Asia/Kolkata or America/Los_Angeles).")
    elif '/' in msg_body:  # crude way to check for timezones
        # Save/update user
        from app import db, User
        user = User.query.filter_by(phone_number=from_number).first()
        if user:
            user.timezone = msg_body
        else:
            user = User(phone_number=from_number, timezone=msg_body)
            db.session.add(user)
        db.session.commit()
        msg.body("You’re now subscribed! You’ll receive daily Panchangam messages.")
    else:
        msg.body("Please type 'start' to begin or enter your timezone directly.")
    
    return str(response)
