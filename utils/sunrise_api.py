import requests
from config import SUNRISE_API_URL

def get_sunrise_sunset(lat, lng, date):
    params = {"lat": lat, "lng": lng, "date": date}
    response = requests.get(SUNRISE_API_URL, params=params)
    return response.json()['results']
