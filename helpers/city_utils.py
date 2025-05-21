import os
from opencage.geocoder import OpenCageGeocode
from models import CityDetail
from models import db

# Load API key from environment
geocoder = OpenCageGeocode(os.getenv("OPENCAGE_API_KEY"))

def get_or_create_city(lat, lon):
    try:
        result = geocoder.reverse_geocode(lat, lon)
    except Exception as e:
        print(f"❌ Reverse geocoding failed: {e}")
        return None

    if not result:
        print("❌ No results from OpenCage.")
        return None

    components = result[0]['components']
    city_name = components.get('city') or components.get('town') or components.get('village')
    state = components.get('state')
    country = components.get('country')
    timezone = result[0].get('annotations', {}).get('timezone', {}).get('name')

    if not city_name:
        print("❌ Could not determine city name from OpenCage result.")
        return None

    # Try to find existing city
    city = CityDetail.query.filter_by(
        city=city_name,
        state=state,
        country=country
    ).first()

    if city:
        return city

    # Otherwise, create a new city record
    new_city = CityDetail(
        city=city_name,
        state=state,
        country=country,
        timezone=timezone,
        latitude=lat,
        longitude=lon
    )
    db.session.add(new_city)
    db.session.commit()
    print(f"✅ Created new city: {city_name}, {state}, {country}")
    return new_city
