from . import db

class RituDetail(db.Model):
    __tablename__ = 'ritu_detail'

    ritu_id = db.Column(db.Integer, primary_key=True)
    ritu_name = db.Column(db.String(100))
    city_id = db.Column(db.Integer, db.ForeignKey('city_detail.city_id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
