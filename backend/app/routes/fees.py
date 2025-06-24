from flask import Blueprint

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('/')
def index():
    return "Fees route working"
