from . import db

class AyanamDetail(db.Model):
    __tablename__ = 'ayanam_detail'

    ayanam_id = db.Column(db.Integer, primary_key=True)
    ayanam_name = db.Column(db.String(100))
    city_id = db.Column(db.Integer, db.ForeignKey('city_detail.city_id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
