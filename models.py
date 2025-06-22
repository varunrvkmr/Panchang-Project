from db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(100))  # ✅ Add this
    is_subscribed = db.Column(db.Boolean, default=True)  # ✅ Optional: flag to track active users
    enrolled_on = db.Column(db.DateTime, default=db.func.current_timestamp())
