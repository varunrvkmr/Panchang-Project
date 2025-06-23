# scheduler.py
from pytz import timezone
from datetime import datetime
import os
import time
import pytz
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from models import db, UserDetail, CityDetail, ApiDetail, MessageLog, RituDetail, AyanamDetail
from location_utils import get_timezone_from_coordinates
from prokerala import (
    get_advanced_panchang,
    format_panchang_message,
    get_calendar_metadata
)
from helpers.cache_utils import get_cached_ayanam, get_cached_ritu
from messaging import send_whatsapp_message
import logging
from logging.handlers import TimedRotatingFileHandler
import scheduler

# Set up log directory
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Daily log file: rotates at midnight, keeps 7 days
log_file = os.path.join(LOG_DIR, "scheduler.log")
file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
file_handler.suffix = "%Y-%m-%d"

# Formatter for logs
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)

# Root logger setup
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, logging.StreamHandler()]  # Also log to console for systemd
)

# Load environment variables
load_dotenv()

# Set up Flask app context (without running the app)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(app)
migrate = Migrate(app, db)

# ---- Scheduler Logic ----

def should_send_now(user):
    """Check if it's 6:30 AM in the user's local timezone."""
    try:
        utc_now = datetime.utcnow()
        local_tz = pytz.timezone(user.timezone)
        local_time = utc_now.astimezone(local_tz)
        return local_time.hour == 6 and local_time.minute == 30
    except Exception as e:
        print(f"⚠️ Error calculating local time for {user.phone_number}: {e}")
        return False

def run_scheduler():
    logging.info("✅ Panchangam Scheduler Started")
    

    with app.app_context():
        while True:
            try:
                #print(f"⏰ Checking users at {datetime.utcnow().isoformat()} UTC")
                logging.info(f"⏰ Checking users at {datetime.utcnow().isoformat()} UTC")
                users = UserDetail.query.all()

                for user in users:
                    if not all([user.phone_number, user.latitude, user.longitude, user.timezone]):
                        #print(f"⚠️ Skipping user {user.phone_number}: Missing data")
                        logging.info(f"⚠️ Skipping user {user.phone_number}: Missing data")
                        continue

                    if should_send_now(user):
                        #print(f"📤 Sending Panchangam to {user.phone_number}")
                        logging.info(f"📤 Sending Panchangam to {user.phone_number}")
                        try:
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

                            send_whatsapp_message(user.phone_number, message)
                            #print(f"✅ Message sent to {user.phone_number}")
                            logging.info("✅ Message sent to {user.phone_number}")

                        except Exception as e:
                            #print(f"❌ Failed to send to {user.phone_number}: {e}")
                            logging.info("✅ Message sent to {user.phone_number}")

            except Exception as e:
                #print(f"❌ Scheduler loop failed: {e}")
                logging.info(f"❌ Scheduler loop failed: {e}")

            # Wait for 15 minutes before checking again
            time.sleep(900)

# ---- Entry Point ----
if __name__ == "__main__":
    run_scheduler()
