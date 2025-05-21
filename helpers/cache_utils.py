from datetime import datetime
from models import RituDetail, AyanamDetail, CityDetail
from prokerala import get_solstice_info, get_ritu_info
from datetime import datetime, date
from models import db

def get_cached_ayanam(lat, lon, tz_name, city_id):
    today = date.today()
    existing = (
        AyanamDetail.query
        .filter_by(city_id=city_id)
        .filter(AyanamDetail.start_date <= today, AyanamDetail.end_date >= today)
        .first()
    )
    if existing:
        return existing.ayanam_name  # ✅ return string

    if today >= date(today.year, 1, 14) and today <= date(today.year, 7, 15):
        ayanam_name = "Uttarayan"
        start_date = date(today.year, 1, 14)
        end_date = date(today.year, 7, 15)
    else:
        ayanam_name = "Dakshinayan"
        if today.month >= 7:
            start_date = date(today.year, 7, 16)
            end_date = date(today.year + 1, 1, 13)
        else:
            start_date = date(today.year - 1, 7, 16)
            end_date = date(today.year, 1, 13)

    new_entry = AyanamDetail(
        ayanam_name=ayanam_name,
        city_id=city_id,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(new_entry)
    db.session.commit()
    return ayanam_name  # ✅ return string

def get_cached_ritu(lat, lon, tz_name, city_id):
    today = date.today()
    existing = (
        RituDetail.query
        .filter_by(city_id=city_id)
        .filter(RituDetail.start_date <= today, RituDetail.end_date >= today)
        .first()
    )
    if existing:
        return existing.ritu_name  # ✅ return cached string

    print("cache-utils.py - Fetching ritu data")
    result = get_ritu_info(lat=lat, lon=lon, tz_name=tz_name) # Now returns full dict
    print("cache-utils.py - Result from get_ritu_info:", result)

    # Safely extract ritu data
    ritu_data = result.get("drik_ritu")
    if not ritu_data:
        print("cache-utils.py - ❌ Missing 'drik_ritu' in response!")
        return "Unknown Ritu"

    print("cache-utils.py - ritu_data:", ritu_data)

    ritu_name = str(ritu_data.get("vedic_name", "Unknown"))
    start = ritu_data.get("start")
    end = ritu_data.get("end")

    if not start or not end:
        print("❌ Missing start/end dates in ritu_data")
        return ritu_name

    try:
        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date()
    except ValueError as e:
        print("❌ Error parsing start/end dates:", e)
        return ritu_name

    new_entry = RituDetail(
        ritu_name=ritu_name,
        city_id=city_id,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(new_entry)
    db.session.commit()
    print("✅ Ritu cached:", ritu_name)
    return ritu_name  # ✅ return string