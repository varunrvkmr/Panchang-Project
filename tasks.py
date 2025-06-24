# tasks.py

import os
import logging
from datetime import datetime, date, time

import pytz
from celery import Celery
from celery.schedules import crontab
from flask import Flask

from models import db, UserDetail
from prokerala import (
    get_advanced_panchang,
    format_panchang_message,
    get_calendar_metadata,
)
from helpers.cache_utils import get_cached_ayanam, get_cached_ritu
from messaging import send_whatsapp_message

# ─── Flask context for SQLAlchemy ────────────────────────────────────────────────
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(flask_app)

# ─── Celery setup ────────────────────────────────────────────────────────────────
celery = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
)
celery.conf.update(
    timezone='UTC',
    enable_utc=True,
)

# ─── Build UTC-based cron entries for each user timezone ─────────────────────────
with flask_app.app_context():
    # get distinct timezones
    rows = (
        db.session
          .query(UserDetail.timezone)
          .filter(UserDetail.timezone.isnot(None))
          .distinct()
          .all()
    )
    timezones = [tz for (tz,) in rows]

# We'll use "today" just to read the current UTC offset (handles DST right now)
today = date.today()

beat_schedule = {}
for tz_name in timezones:
    # localize today's 06:30 in that tz
    local_tz = pytz.timezone(tz_name)
    #local_dt = local_tz.localize(datetime.combine(today, time(6, 30)))
    local_dt = local_tz.localize(datetime.combine(today, time(2, 55)))
    # convert to UTC
    utc_dt = local_dt.astimezone(pytz.utc)

    utc_hour   = utc_dt.hour
    utc_minute = utc_dt.minute

    beat_schedule[f'send-panchang-{tz_name}'] = {
        'task': 'tasks.send_for_timezone',
        'schedule': crontab(hour=utc_hour, minute=utc_minute),
        'args': (tz_name,),
    }

celery.conf.beat_schedule = beat_schedule

# ─── Task definition ────────────────────────────────────────────────────────────

@celery.task
def send_for_timezone(timezone_name: str):
    """
    Send the Panchangam message to all users in the given timezone,
    firing at the UTC‐converted 06:30 local time.
    """
    with flask_app.app_context():
        #users = UserDetail.query.filter_by(timezone=timezone_name).all()
        now = datetime.utcnow()
        users = (
            UserDetail.query
            .filter(
                UserDetail.timezone == timezone_name,
                UserDetail.obsoleted_on > now
            )
            .all()
        )
        for user in users:
            if not all([user.phone_number, user.latitude, user.longitude]):
                logging.warning(f"⚠️ Skipping {user.phone_number}: missing data")
                continue

            try:
                # fetch all pieces
                '''
                panchang_data = get_advanced_panchang(
                    lat=user.latitude,
                    lng=user.longitude,
                    tz_name=user.timezone
                )
                calendar_info = get_calendar_metadata(tz_name=user.timezone)
                ayanam = get_cached_ayanam(
                    user.latitude, user.longitude, user.timezone, user.city_id
                )
                ritu = get_cached_ritu(
                    user.latitude, user.longitude, user.timezone, user.city_id
                )
                
                message = format_panchang_message(
                    data=panchang_data,
                    calendar_info=calendar_info,
                    ayanam=ayanam,
                    ritu=ritu,
                    timezone_name=user.timezone
                )
                '''
                message = 'daily test message'

                send_whatsapp_message(user.phone_number, message)
                logging.info(f"✅ Panchang sent to {user.phone_number} ({timezone_name})")
            except Exception as e:
                logging.error(f"❌ Failed for {user.phone_number}: {e}")
