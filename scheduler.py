# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from datetime import datetime
from whatsapp import send_whatsapp_message
from prokerala_api import get_panchangam_for_timezone
from models import db, User

def send_daily_messages():
    users = User.query.all()
    for user in users:
        now = datetime.now(timezone(user.timezone))
        panchang_data = get_panchangam_for_timezone(user.timezone, now.date())
        formatted_msg = format_panchangam(panchang_data)
        send_whatsapp_message(user.phone_number, formatted_msg)

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_daily_messages, trigger="interval", hours=24)
    scheduler.start()
