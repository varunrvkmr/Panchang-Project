from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os
import sys
import json
from datetime import datetime, timezone
from flask import send_from_directory

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.panchang_api import get_advanced_panchang
from openweather_api import get_coordinates
from utils.whatsapp_sender import send_whatsapp_message

# Load credentials from .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.prokerala.com/token"
BASE_API_URL = "https://api.prokerala.com/v2/astrology/panchang"

app = Flask(__name__)

# Audio Mapping
AUDIO_FILES = {
    "vaara": {
        "Monday": "/static/audio/vaara/Monday.mp3",
        "Tuesday": "/static/audio/vaara/Tuesday.mp3"
    },
    "tithi": {
        "Trayodashi": "/static/audio/tithi/Trayodashi.mp3",
        "Pratipada": "/static/audio/tithi/Pratipada.mp3",
    },
    "nakshatra": {
        "Purva Ashadha": "/static/audio/nakshatra/Purva_Ashadha.mp3",
        "Revati": "/static/audio/nakshatra/Revati.mp3",
    }
}

@app.route('/get_audio_sources', methods=['GET'])
def get_audio_sources():
    """Fetch audio sources using predefined mappings."""
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        datetime_str = request.args.get('datetime')

        if not all([lat, lng, datetime_str]):
            return jsonify({"error": "Missing required parameters"}), 400

        data = get_advanced_panchang(lat, lng, datetime_str)

        vaara = data['data']['vaara']
        tithi_list = data['data']['tithi']
        nakshatra_list = data['data']['nakshatra']
        print("Raw vaara: ", vaara)
        print("Raw tithi_list: ", tithi_list)
        print("Raw nakshatra_list: ", nakshatra_list)

        # Select the first Tithi and Nakshatra
        selected_tithi = tithi_list[0]
        selected_nakshatra = nakshatra_list[0]

        print("Processed selected_tithi: ", selected_tithi)
        print("Processed selected_nakshatra: ", selected_nakshatra)

        # Extract readable timings
        selected_tithi_start = format_iso_to_readable(selected_tithi['start'])
        selected_tithi_end = format_iso_to_readable(selected_tithi['end'])
        selected_nakshatra_start = format_iso_to_readable(selected_nakshatra['start'])
        selected_nakshatra_end = format_iso_to_readable(selected_nakshatra['end'])

        audio_files = {
            "vaara": AUDIO_FILES['vaara'].get(vaara, "/static/audio/default.mp3"),
            "tithi": AUDIO_FILES['tithi'].get(selected_tithi['name'], "/static/audio/default.mp3"),
            "nakshatra": AUDIO_FILES['nakshatra'].get(selected_nakshatra['name'], "/static/audio/default.mp3"),
        }

        return jsonify({
            "audio_files": audio_files,
            "selected_tithi": {
                "name": selected_tithi['name'],
                "paksha": selected_tithi['paksha'],
                "start": selected_tithi_start,
                "end": selected_tithi_end
            },
            "selected_nakshatra": {
                "name": selected_nakshatra['name'],
                "start": selected_nakshatra_start,
                "end": selected_nakshatra_end
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    """Serve the front-end page."""
    return render_template('index.html')

@app.route('/search_cities', methods=['GET'])
def search_cities():
    """Search US cities based on user input."""
    query = request.args.get('query', '').lower().strip()

    if not query:
        return jsonify([]), 200

    try:
        with open('utils/data/us_cities.json', 'r') as f:
            cities = json.load(f)

        matching_cities = [
            {
                "city": city["city"],
                "state": city["state"],
                "latitude": city["latitude"],
                "longitude": city["longitude"]
            }
            for city in cities
            if query in city["city"].lower()
        ]

        # Return the top 10 matches
        return jsonify(matching_cities[:10]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_city_suggestions', methods=['GET'])
def get_city_suggestions():
    """Fetch city suggestions and their coordinates based on user input."""
    query = request.args.get('query', '').strip()

    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    try:
        # Split the query into components (e.g., city, state, country)
        parts = query.split(',')
        city = parts[0].strip()
        state = parts[1].strip() if len(parts) > 1 else None
        country = parts[2].strip() if len(parts) > 2 else None

        # Fetch coordinates using the OpenWeather API
        results = get_coordinates(city, state, country)

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_advanced_panchang', methods=['GET'])
def fetch_advanced_panchang():
    """Fetch Panchang details, auspicious times, and inauspicious times."""
    try:
        # Extract query parameters
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        datetime_str = request.args.get('datetime')
        ayanamsa = request.args.get('ayanamsa', 1)  # Default to Lahiri

        if not all([lat, lng, datetime_str]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the consolidated API function
        data = get_advanced_panchang(lat, lng, datetime_str, ayanamsa)

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/send_whatsapp_message', methods=['POST'])
def trigger_whatsapp_message():
    """
    Trigger a WhatsApp message with Panchang details and an audio file.
    """
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        vaara = data.get('vaara')
        timestamp = data.get('timestamp')
        tithi = data.get('tithi')
        nakshatra = data.get('nakshatra')
        media_url = data.get('media_url', "https://purely-actual-marmoset.ngrok-free.app/static/audio/nakshatra/Purva_Ashadha.mp3")

        if not phone_number or not vaara or not timestamp or not tithi or not nakshatra:
            return jsonify({"error": "Missing required parameters"}), 400

        result = send_whatsapp_message(phone_number, vaara, timestamp, tithi, nakshatra)

        if result['status'] == 'success':
            return jsonify({
                "message": "WhatsApp message sent successfully!",
                "sid": result['sid'],
                "media_sid": result.get('media_sid')
            }), 200
        else:
            return jsonify({"error": result['error']}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
def format_iso_to_readable(iso_timestamp):
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        print("processed timestamp: ", dt.strftime('%d-%m-%Y %I:%M %p'))
        return dt.strftime('%d-%m-%Y %I:%M %p')
    except ValueError:
        return iso_timestamp  # Return original if parsing fails
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

