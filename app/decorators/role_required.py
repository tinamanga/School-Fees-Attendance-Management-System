from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role != required_role:
                return jsonify({"message": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper
