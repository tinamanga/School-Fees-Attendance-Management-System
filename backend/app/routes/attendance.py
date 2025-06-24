from flask import Blueprint

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
def index():
    return "Attendance route working"
