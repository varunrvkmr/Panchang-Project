import os
import requests
import time
from urllib.parse import quote
from datetime import datetime
from dateutil import parser
import pytz
from pytz import timezone

# Constants from your .env
CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")
TOKEN_URL = "https://api.prokerala.com/token"
BASE_ADVANCED_API_URL = "https://api.prokerala.com/v2/astrology/panchang/advanced"

# Cache access token
access_token = None
token_expiry = 0

def get_access_token():
    global access_token, token_expiry

    if access_token and time.time() < token_expiry:
        return access_token  # Use cached token

    response = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        token_expiry = time.time() + token_data['expires_in'] - 60  # Add buffer
        return access_token
    else:
        raise Exception("❌ Failed to fetch access token from Prokerala")

def get_advanced_panchang(lat, lng, dt=None, ayanamsa=1, tz_name="Asia/Kolkata"):
    if dt is None:
        tz = timezone(tz_name)
        dt = datetime.now(tz)


    dt = dt.replace(microsecond=0)
    datetime_str = dt.isoformat()  # Must include timezone info

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "ayanamsa": ayanamsa,
        "coordinates": f"{lat},{lng}",
        "datetime": datetime_str,
        "la": "en"
    }

    response = requests.get(BASE_ADVANCED_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return parse_panchang_data(response.json()["data"])
    else:
        raise Exception(f"API Error: {response.status_code}, {response.text}")

def get_calendar_metadata(dt=None, tz_name="Asia/Kolkata", calendar_type="shaka-samvat"):
    from pytz import timezone
    if dt is None:
        dt = datetime.now(timezone(tz_name))

    dt_str = dt.strftime("%Y-%m-%d")  # Just date, no time

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "date": dt_str,
        "calendar": calendar_type,
        "la": "en"
    }

    response = requests.get("https://api.prokerala.com/v2/calendar", headers=headers, params=params)
    if response.ok:
        data = response.json()["data"]["calendar_date"]
        return {
            "calendar": data.get("name"),
            "year_name": data.get("year_name"),
            "month_name": data.get("month_name")
        }
    else:
        raise Exception(f"Calendar API Error: {response.status_code}, {response.text}")

def get_solstice_info(lat, lon, dt=None, tz_name="Asia/Kolkata", ayanamsa=1):
    from pytz import timezone
    if dt is None:
        dt = datetime.now(timezone(tz_name))

    dt = dt.replace(microsecond=0)
    datetime_str = dt.isoformat()
    coordinates = f"{lat},{lon}"

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": ayanamsa,
        "la": "en"
    }

    response = requests.get("https://api.prokerala.com/v2/astrology/solstice", headers=headers, params=params)
    if response.ok:
        solstice = response.json()["data"]["solstice"]
        return f"{solstice['name']}/{solstice['vedic_name']}"
    else:
        raise Exception(f"Solstice API Error: {response.status_code}, {response.text}")

def get_ritu_info(lat, lon, dt=None, tz_name="Asia/Kolkata", ayanamsa=1):
    from pytz import timezone
    if dt is None:
        dt = datetime.now(timezone(tz_name))

    dt = dt.replace(microsecond=0)
    datetime_str = dt.isoformat()
    coordinates = f"{lat},{lon}"

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": ayanamsa,
        "la": "en"
    }

    response = requests.get("https://api.prokerala.com/v2/astrology/ritu", headers=headers, params=params)
    if response.ok:
        data = response.json()["data"]
        ritu = data.get("vedic_ritu")  # or use drik_ritu if preferred
        return f"{ritu['name']}/{ritu['vedic_name']}"
    else:
        raise Exception(f"Ritu API Error: {response.status_code}, {response.text}")


def format_panchang_message(data, calendar_info=None, ayanam=None, ritu=None, timezone_name=None):
    lines = []

    lines.append("📿 *Today's Panchangam* 📿")
    
    if timezone_name:
        lines.append(f"🕒 *Timezone:* {timezone_name}")

    if calendar_info:
        lines.append(f"📛 *Calendar:* {calendar_info.get('calendar')}")
        lines.append(f"🗓️ *Month:* {calendar_info.get('month_name')}")
        lines.append(f"📅 *Year:* {calendar_info.get('year_name')}")

    if ayanam:
        lines.append(f"🌞 *Ayanam:* {ayanam}")

    if ritu:
        lines.append(f"🪷 *Ritu:* {ritu}")

    lines.append(f"📅 *Vaara:* {data.get('vaara', 'N/A')}")
    lines.append(f"🌘 *Tithi:* {', '.join(data.get('tithi', []))}")
    lines.append(f"✨ *Nakshatra:* {', '.join(data.get('nakshatra', []))}")
    lines.append(f"🧘 *Yoga:* {', '.join(data.get('yoga', []))}")
    lines.append(f"🌀 *Karana:* {', '.join(data.get('karana', []))}")

    lines.append("\n✅ *Auspicious Periods:*")
    if data.get("auspicious"):
        for a in data["auspicious"]:
            time_range = format_time_range(a["start"], a["end"], tz_name=timezone_name)
            lines.append(f"- {a['name']}: {time_range}")
    else:
        lines.append("None listed.")

    lines.append("\n🚫 *Inauspicious Periods:*")
    if data.get("inauspicious"):
        for i in data["inauspicious"]:
            time_range = format_time_range(i["start"], i["end"], tz_name=timezone_name)
            lines.append(f"- {i['name']}: {time_range}")
    else:
        lines.append("None listed.")

    return "\n".join(lines)



def parse_panchang_data(data):
    return {
        "vaara": data.get("vaara"),
        "tithi": [t["name"] for t in data.get("tithi", [])],
        "nakshatra": [n["name"] for n in data.get("nakshatra", [])],
        "karana": [k["name"] for k in data.get("karana", [])],
        "yoga": [y["name"] for y in data.get("yoga", [])],
        "auspicious": [
            {
                "name": a["name"],
                "start": a["period"][0]["start"],
                "end": a["period"][0]["end"]
            }
            for a in data.get("auspicious_period", [])
        ],
        "inauspicious": [
            {
                "name": i["name"],
                "start": i["period"][0]["start"],
                "end": i["period"][0]["end"]
            }
            for i in data.get("inauspicious_period", [])
        ]
    }


def format_time_range(start, end, tz_name="Asia/Kolkata"):
    try:
        start_dt = parser.isoparse(start).astimezone(timezone(tz_name))
        end_dt = parser.isoparse(end).astimezone(timezone(tz_name))
        start_str = start_dt.strftime("%I:%M %p").lstrip("0")
        end_str = end_dt.strftime("%I:%M %p").lstrip("0")
        return f"{start_str} → {end_str}"
    except Exception as e:
        return f"{start} → {end}"