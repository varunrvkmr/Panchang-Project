import os
import requests
import time
from dotenv import load_dotenv

# Load client credentials securely
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.prokerala.com/token"
BASE_ADVANCED_API_URL = "https://api.prokerala.com/v2/astrology/panchang/advanced"

# Token cache
access_token = None
token_expiry = 0

def get_access_token():
    global access_token, token_expiry
    if access_token and time.time() < token_expiry:
        return access_token  # Reuse cached token
    
    response = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        token_expiry = time.time() + token_data['expires_in'] - 60  # Buffer of 1 minute
        return access_token
    else:
        raise Exception("Failed to get access token")

def get_advanced_panchang(lat, lng, datetime, ayanamsa=1):
    """
    Fetch Panchang, auspicious times, and inauspicious times in a single API call.
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "ayanamsa": ayanamsa,  # Lahiri
        "coordinates": f"{lat},{lng}",
        "datetime": datetime
    }

    response = requests.get(BASE_ADVANCED_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code}, {response.text}")
