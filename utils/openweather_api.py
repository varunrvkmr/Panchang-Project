import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not OPENWEATHER_API_KEY:
    raise ValueError("OpenWeather API key not found. Please set it in the .env file.")

def get_coordinates(city, state=None, country=None, limit=5):
    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    query_params = {
        "q": f"{city},{state or ''},{country or ''}",
        "limit": limit,
        "appid": OPENWEATHER_API_KEY
    }

    try:
        response = requests.get(base_url, params=query_params)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"No results found for the location: {city}, {state}, {country}")

        # Return relevant location details
        return [
            {
                "name": loc.get("name"),
                "state": loc.get("state"),
                "country": loc.get("country"),
                "latitude": loc.get("lat"),
                "longitude": loc.get("lon")
            }
            for loc in data
        ]

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch coordinates: {str(e)}")