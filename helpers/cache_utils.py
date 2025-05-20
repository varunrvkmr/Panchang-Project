from datetime import datetime
from models import RituDetail, AyanamDetail, CityDetail
from prokerala import get_solstice_info, get_ritu_info
from datetime import datetime, date
from db import db

def get_cached_ayanam(lat, lon, tz_name, city_id):
    today = date.today()
    existing = (
        AyanamDetail.query
        .filter_by(city_id=city_id)
        .filter(AyanamDetail.start_date <= today, AyanamDetail.end_date >= today)
        .first()
    )
    if existing:
        return {"ayanam_name": existing.ayanam_name}

    # Hardcoded logic
    if today >= date(today.year, 1, 14) and today <= date(today.year, 7, 15):
        ayanam_name = "Uttarayan"
        start_date = date(today.year, 1, 14)
        end_date = date(today.year, 7, 15)
    else:
        ayanam_name = "Dakshinayan"
        # Determine year transition
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
    return {"ayanam_name": ayanam_name}


def get_cached_ritu(lat, lon, tz_name, city_id):
    today = date.today()
    existing = (
        RituDetail.query
        .filter_by(city_id=city_id)
        .filter(RituDetail.start_date <= today, RituDetail.end_date >= today)
        .first()
    )
    if existing:
        return {"ritu_name": existing.ritu_name}

    result = get_ritu_info(lat, lon, tz_name)

    # Choose "drik_ritu" if you prefer astronomical accuracy
    ritu_data = result["drik_ritu"]

    start_date = datetime.fromisoformat(ritu_data["start"]).date()
    end_date = datetime.fromisoformat(ritu_data["end"]).date()

    new_entry = RituDetail(
        ritu_name=ritu_data["vedic_name"],
        city_id=city_id,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(new_entry)
    db.session.commit()
    return {"ritu_name": new_entry.ritu_name}