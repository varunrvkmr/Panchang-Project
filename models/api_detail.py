from . import db

class ApiDetail(db.Model):
    __tablename__ = 'api_detail'

    api_id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(100))
    api_call_string = db.Column(db.String(1000))
    api_param1 = db.Column(db.String(100))
    api_param2 = db.Column(db.String(100))
    api_param3 = db.Column(db.String(100))
    api_param4 = db.Column(db.String(100))
