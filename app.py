from flask import Flask, jsonify, request, render_template
import requests
import time
from dotenv import load_dotenv
import os
import sys
import json
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.panchang_api import get_advanced_panchang
from openweather_api import get_coordinates

# Load credentials from .env
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.prokerala.com/token"
BASE_API_URL = "https://api.prokerala.com/v2/astrology/panchang"

app = Flask(__name__)


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
        # Load the filtered dataset (cached for efficiency in production)
        with open('utils/data/us_cities.json', 'r') as f:
            cities = json.load(f)

        # Filter cities based on user query
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
if __name__ == '__main__':
    app.run(debug=True)
