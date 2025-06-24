from flask import Blueprint

students_bp = Blueprint('students', __name__)

@students_bp.route('/')
def index():
    return "Students route working"
