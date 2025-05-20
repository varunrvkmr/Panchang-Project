from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user_detail import UserDetail
from .city_detail import CityDetail
from .api_detail import ApiDetail
from .message_log import MessageLog
from .ritu_detail import RituDetail
from .ayanam_detail import AyanamDetail
