from . import db

class MessageLog(db.Model):
    __tablename__ = 'message_log'

    message_id = db.Column(db.Integer, primary_key=True)
    message_text = db.Column(db.JSON)
    city_id = db.Column(db.Integer, db.ForeignKey('city_detail.city_id'))
    api_id = db.Column(db.Integer, db.ForeignKey('api_detail.api_id'))
    create_date = db.Column(db.DateTime)
