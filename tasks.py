from celery import Celery
from celery.schedules import crontab
import os
from models import db, UserDetail
from prokerala import get_advanced_panchang, format_panchang_message, get_calendar_metadata
from helpers.cache_utils import get_cached_ayanam, get_cached_ritu
from messaging import send_whatsapp_message
import pytz
from datetime import datetime
import logging
from flask import Flask

# Minimal app for Celery context
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(flask_app)

celery = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
)

celery.conf.update(
    timezone='UTC',
    enable_utc=True,
)

'''
celery.conf.beat_schedule = {
    'send-daily-panchang-every-15min': {
        'task': 'tasks.send_daily_panchang_for_all',
        'schedule': crontab(minute='*/15'),  # every 15 minutes
    }
}
'''
celery.conf.beat_schedule = {
    'send-daily-panchang-every-1min': {
        'task': 'tasks.send_daily_panchang_for_all',
        'schedule': crontab(minute='*/1'),  # run every minute
    }
}

@celery.task
def send_daily_panchang_for_all():
    with flask_app.app_context():
        users = UserDetail.query.all()
        for user in users:
            if not all([user.phone_number, user.latitude, user.longitude, user.timezone]):
                logging.info(f"⚠️ Skipping user {user.phone_number}: Missing data")
                continue

            try:
                utc_now = datetime.utcnow()
                local_tz = pytz.timezone(user.timezone)
                local_time = utc_now.astimezone(local_tz)

                #if local_time.hour == 6 and local_time.minute == 30:
                if True:
                    #logging.info(f"📤 Sending Panchangam to {user.phone_number}")
                    logging.info(f"📤 FORCED send to {user.phone_number}")

                    '''
                    panchang_data = get_advanced_panchang(
                        lat=user.latitude,
                        lng=user.longitude,
                        tz_name=user.timezone
                    )
                    calendar_info = get_calendar_metadata(tz_name=user.timezone)
                    ayanam = get_cached_ayanam(user.latitude, user.longitude, user.timezone, user.city_id)
                    ritu = get_cached_ritu(user.latitude, user.longitude, user.timezone, user.city_id)
                    

                    message = format_panchang_message(
                        data=panchang_data,
                        calendar_info=calendar_info,
                        ayanam=ayanam,
                        ritu=ritu,
                        timezone_name=user.timezone
                    )
                    send_whatsapp_message(user.phone_number, message)
                    logging.info(f"✅ Message sent to {user.phone_number}")
                    '''
                    test_message = (
                        f"🧪 This is a test Panchangam message for {user.phone_number}. "
                        f"Sent at {datetime.utcnow().isoformat()} UTC."
                    )
                    send_whatsapp_message(user.phone_number, test_message)
                    logging.info(f"✅ Test message sent to {user.phone_number}")

            except Exception as e:
                logging.error(f"❌ Failed to send to {user.phone_number}: {e}")
