from . import db

class UserDetail(db.Model):
    __tablename__ = 'user_detail'

    user_id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(10))
    area_code = db.Column(db.String(10))
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city_detail.city_id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50))
    created_on = db.Column(db.DateTime)
    obsoleted_on = db.Column(db.DateTime)
