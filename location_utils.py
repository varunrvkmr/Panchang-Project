from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

def get_timezone_from_coordinates(lat, lon):
    return tf.timezone_at(lng=lon, lat=lat) or "UTC"
