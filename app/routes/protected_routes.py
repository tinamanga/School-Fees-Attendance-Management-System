from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.decorators.role_required import role_required


protected_bp = Blueprint("protected", __name__, url_prefix="/protected")

@protected_bp.route("/dashboard")
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    return jsonify(message="Access granted", user_id=user_id), 200



@protected_bp.route("/admin-only", methods=["GET"])
@role_required("admin")
def admin_only_area():
    return jsonify(message="Welcome, admin!"), 200
