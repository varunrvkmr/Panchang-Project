# admin.py
from flask import Blueprint, render_template
from models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)
