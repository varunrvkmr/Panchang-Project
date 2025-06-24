from flask import Flask, request
from models import db
#from models import User
#from models import db, UserDetail, CityDetail, ApiDetail, MessageLog, RituDetail, AyanamDetail
#from models import db
from location_utils import get_timezone_from_coordinates
from prokerala import get_advanced_panchang, format_panchang_message, get_calendar_metadata, get_solstice_info, get_ritu_info
import os
from messaging import send_whatsapp_message
from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy import text
from helpers.cache_utils import get_cached_ayanam, get_cached_ritu
from helpers.city_utils import get_or_create_city
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, date 

load_dotenv()

# ─── LOGGING SETUP ────────────────────────────────────────────────────────────────
# ensure ./logs exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    when="midnight",
    interval=1,
    backupCount=7,
)
handler.suffix = "%Y-%m-%d"
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))

# configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# remove any default handlers (so we don’t double-log to console)
root_logger.handlers.clear()
# add our file handler and also log to console
root_logger.addHandler(handler)
root_logger.addHandler(logging.StreamHandler())
# ─────────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./panchangam.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")


db.init_app(app)
migrate = Migrate(app, db)
from models import UserDetail, CityDetail, ApiDetail, MessageLog, RituDetail, AyanamDetail

VERIFY_TOKEN = "test123"
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_requests():
    if request.method == "POST":
        logging.info(f"Request: {request.method} {request.path} {request.get_json()}")
    else:
        logging.info(f"Request: {request.method} {request.path} {request.args}")

@app.route("/", methods=["GET"])
def home():
    return "It works!", 200

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                for msg in messages:
                    sender = msg.get("from")
                    msg_type = msg.get("type")

                    # ✅ User shared location
                    if msg_type == "location":
                        lat = msg["location"]["latitude"]
                        lon = msg["location"]["longitude"]
                        tz = get_timezone_from_coordinates(lat, lon)

                        user = UserDetail.query.filter_by(phone_number=sender).first()
                        if not user:
                            user = UserDetail(
                                phone_number=sender,
                                created_on=datetime.utcnow(),
                                obsoleted_on=date(2099, 12, 31)
                            )
                            db.session.add(user)

                        # Determine nearest city and its ID
                        city = get_or_create_city(lat, lon)
                        city_id = city.city_id if city else None
                        user.city_id = city_id

                        user.latitude = lat
                        user.longitude = lon
                        user.timezone = tz
                        db.session.commit()

                        logging.info(f"✅ Saved location for {sender}: {lat}, {lon} → {tz}")

                        try:
                            '''
                            panchang_data = get_advanced_panchang(lat=lat, lng=lon, tz_name=tz)
                            #panchang_data = 'panchang data'
                            #print("✅ panchang_data received")
                            logging.info("✅ panchang_data received")

                            calendar_info = get_calendar_metadata(tz_name=tz)
                            #print("✅ calendar_info received")
                            logging.info("✅ calendar_info received")

                            ayanam = get_cached_ayanam(lat, lon, tz, city_id)
                            #ayanam = 'ayanam'
                            #print("✅ ayanam received:", ayanam, "| type:", type(ayanam))
                            logging.info(f"✅ ayanam received: {ayanam} | type: {type(ayanam)}")

                            ritu = get_cached_ritu(lat, lon, tz, city_id)
                            #print("✅ ritu received:", ritu, "| type:", type(ritu))
                            logging.info(f"✅ ritu received: {ritu} | type: {type(ritu)}")

                            message = format_panchang_message(
                                data=panchang_data,
                                calendar_info=calendar_info,
                                ayanam=ayanam,
                                ritu=ritu,
                                timezone_name=tz
                            )
                            '''
                            message = 'first panchang message after subscribing'
                            #print("🧪 Type of message:", type(message))
                            #print("🧪 Preview of message:", message[:100])
                            logging.info(f"🧪 Type of message: {type(message)}")
                            logging.info(f"🧪 Preview of message: {message[:100]}")

                            send_whatsapp_message(sender, message)


                        except Exception as e:
                            #print(f"❌ Failed to send Panchang message: {e}")
                            logging.error(f"❌ Failed to send Panchang message: {e}")
                            send_whatsapp_message(sender, "You're subscribed! We'll send your daily Panchangam soon. 🕉️")

                    # ✅ Handle plain text like "start"
                    elif msg_type == "text":
                        body = msg["text"]["body"].strip().lower()
                        #print(f"📨 Text received from {sender}: {body}")
                        logging.info(f"📨 Text received from {sender}: {body}")

                        if body == "start":
                            print(f"✅ Detected START command from {sender}")
                            reply = (
                                "Hi there! 👋 I’m your daily Panchangam assistant.\n\n"
                                "To get started, please share your *location* by tapping the 📎 (attach) button and selecting \"Location\"."
                            )
                            send_whatsapp_message(sender, reply)
                        # ─── new unsubscribe logic ──────────────────────────────
                        elif body in {"stop", "unsubscribe", "cancel", "quit"}:
                            user = UserDetail.query.filter_by(phone_number=sender).first()
                            if not user:
                                send_whatsapp_message(
                                    sender,
                                    "Looks like you’re not subscribed. Text ‘start’ to subscribe."
                                )
                            else:
                                now = datetime.utcnow()
                                # if obsoleted_on is *after* now, they're active → we unsubscribe them
                                if user.obsoleted_on and user.obsoleted_on > now:
                                    user.obsoleted_on = now
                                    db.session.commit()
                                    logging.info(f"🚫 Unsubscribed {sender}")
                                    send_whatsapp_message(
                                        sender,
                                        "You’ve been unsubscribed from daily Panchangam. "
                                        "Text ‘start’ anytime to re-subscribe. 🕉️"
                                    )
                                else:
                                    # obsoleted_on is <= now → already unsubscribed
                                    send_whatsapp_message(
                                        sender,
                                        "You’re already unsubscribed. Text ‘start’ to re-subscribe anytime."
                                    )
                        # ────────────────────────────────────────────────────────


    return "OK", 200

@app.route("/test-db")
def test_db():
    try:
        db.session.execute(text("SELECT 1"))
        return "✅ DB Connected!"
    except Exception as e:
        return f"❌ DB Error: {e}"

@app.route("/test-panchang/<phone>")
def test_panchang(phone):
    user = UserDetail.query.filter_by(phone_number=phone).first()
    if not user or not user.latitude or not user.longitude:
        return "User or location not found", 404

    data = get_advanced_panchang(
        lat=user.latitude,
        lng=user.longitude,
        tz_name=user.timezone
    )

    message = format_panchang_message(data)

    # Send to user on WhatsApp
    send_whatsapp_message(user.phone_number, message)

    return {"message": "Sent Panchangam to user."}

if __name__ == "__main__":
    app.run(port=5050, debug=True)
