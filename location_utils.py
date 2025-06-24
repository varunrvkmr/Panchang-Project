# location_utils.py

import logging
from timezonefinder import TimezoneFinder

# ─── Create a subclass that disables H3 shortcuts ───────────────────────────────
class SafeTimezoneFinder(TimezoneFinder):
    def get_shortcut_polys(self, lng: float, lat: float):
        # Skip the H3 path entirely
        return []

# Force the in‐memory shapefile lookup and skip H3
tf = SafeTimezoneFinder(in_memory=True)

def get_timezone_from_coordinates(lat: float, lon: float) -> str:
    """
    Returns the IANA timezone name for the given coordinates,
    falling back to 'UTC' on any error.
    """
    try:
        tz = tf.timezone_at(lat=lat, lng=lon)
        return tz or "UTC"
    except Exception as e:
        logging.error(f"Timezone lookup failed for ({lat}, {lon}), defaulting to UTC: {e}")
        return "UTC"
