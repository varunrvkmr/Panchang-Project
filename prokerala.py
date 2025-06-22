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

'''
def get_ritu_info(lat, lon, dt=None, tz_name="Asia/Kolkata", ayanamsa=1):
    from pytz import timezone
    print("📅 Computing datetime for ritu request...")
    print("🧪 get_ritu_info called with tz_name:", tz_name, "| type:", type(tz_name))
    if dt is None:
        dt = datetime.now(timezone(tz_name))

    dt = dt.replace(microsecond=0)
    datetime_str = dt.isoformat()
    coordinates = f"{lat},{lon}"

    print("🧭 Coordinates:", coordinates)
    print("🕒 Timestamp:", datetime_str)

    try:
        token = get_access_token()
        print("🪪 Access token retrieved:", token[:10], "...")
    except Exception as e:
        print("❌ Failed to get access token:", e)
        raise

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "datetime": datetime_str,
        "coordinates": coordinates,
        "ayanamsa": ayanamsa,
        "la": "en"
    }

    print("🌐 Sending request to Prokerala /ritu API")
    try:
        response = requests.get("https://api.prokerala.com/v2/astrology/ritu", headers=headers, params=params)
    except Exception as e:
        print("❌ Exception during Ritu API request:", e)
        raise

    print("📨 Response status code:", response.status_code)

    if response.ok:
        print("📦 Raw Ritu API Response:", response.json())
        return response.json()["data"]
    else:
        print("❌ Ritu API Error Body:", response.text)
        raise Exception(f"Ritu API Error: {response.status_code}")
'''
def get_ritu_info(lat, lon, dt=None, tz_name="Asia/Kolkata", ayanamsa=1):
    print("⚠️ Using hardcoded Ritu API response instead of live call.")

    # Simulated real response from Prokerala's /ritu endpoint
    simulated_response = {
        "vedic_ritu": {
            "id": 0,
            "name": "Spring",
            "vedic_name": "Vasant",
            "start": "2025-04-28T11:22:14+05:30",
            "end": "2025-06-26T11:22:13+05:30"
        },
        "drik_ritu": {
            "id": 1,
            "name": "Summer",
            "vedic_name": "Grishma",
            "start": "2025-05-15T00:00:00+05:30",
            "end": "2025-07-15T23:59:59+05:30"
        }
    }

    return simulated_response  # ✅ behaves like real API data



'''
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
'''
def format_panchang_message(data, calendar_info=None, ayanam=None, ritu=None, timezone_name=None):
    print("🧪 Types before message formatting:")
    print("📅 panchang_data:", type(data))
    print("📆 calendar_info:", type(calendar_info))
    print("🧭 ayanam:", type(ayanam))
    print("🌼 ritu:", type(ritu))

    lines = []

    lines.append("*Today's Panchangam*")
    
    if timezone_name:
        lines.append(f"Timezone: {timezone_name}")

    if calendar_info:
        lines.append(f"Calendar: {calendar_info.get('calendar')}")
        lines.append(f"Month: {calendar_info.get('month_name')}")
        lines.append(f"Year: {calendar_info.get('year_name')}")

    if ayanam:
        lines.append(f"Ayanam: {ayanam}")

    if ritu:
        lines.append(f"Ritu: {ritu}")

    lines.append(f"Vaara: {data.get('vaara', 'N/A')}")
    lines.append(f"Tithi: {', '.join(data.get('tithi', []))}")
    lines.append(f"Nakshatra: {', '.join(data.get('nakshatra', []))}")
    lines.append(f"Yoga: {', '.join(data.get('yoga', []))}")
    lines.append(f"Karana: {', '.join(data.get('karana', []))}")

    lines.append("\nAuspicious Periods:")
    if data.get("auspicious"):
        for a in data["auspicious"]:
            time_range = format_time_range(a["start"], a["end"], tz_name=timezone_name)
            lines.append(f"- {a['name']}: {time_range}")
    else:
        lines.append("None listed.")

    lines.append("\nInauspicious Periods:")
    if data.get("inauspicious"):
        for i in data["inauspicious"]:
            time_range = format_time_range(i["start"], i["end"], tz_name=timezone_name)
            lines.append(f"- {i['name']}: {time_range}")
    else:
        lines.append("None listed.")

    # Combine and trim to 1024 characters max (WhatsApp limit)
    message = "\n".join(lines).strip()

    # Optional: hard cap the message length
    if len(message) > 1024:
        message = message[:1010].rstrip() + "\n... [truncated]"

    return message


def parse_panchang_data(data):
    def safe_name(x):
        return str(x.get("name", "Unknown")) if isinstance(x, dict) else str(x)

    def safe_period(p):
        if isinstance(p, list) and len(p) > 0:
            return p[0].get("start", ""), p[0].get("end", "")
        return "", ""

    return {
        "vaara": str(data.get("vaara", "Unknown")),
        "tithi": [safe_name(t) for t in data.get("tithi", [])],
        "nakshatra": [safe_name(n) for n in data.get("nakshatra", [])],
        "karana": [safe_name(k) for k in data.get("karana", [])],
        "yoga": [safe_name(y) for y in data.get("yoga", [])],
        "auspicious": [
            {
                "name": safe_name(a),
                "start": safe_period(a.get("period", []))[0],
                "end": safe_period(a.get("period", []))[1]
            }
            for a in data.get("auspicious_period", [])
        ],
        "inauspicious": [
            {
                "name": safe_name(i),
                "start": safe_period(i.get("period", []))[0],
                "end": safe_period(i.get("period", []))[1]
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