from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from extensions import db
from models import User


def get_current_user():
    """Return the logged-in User (from the JWT), or None."""
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return db.session.get(User, int(user_id))


def roles_required(*allowed_roles):
    """
    401 -> no/invalid/expired token or user no longer exists
    403 -> logged in but role not allowed
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if user is None:
                return jsonify(status="error", message="User not found"), 401
            if user.role not in allowed_roles:
                return jsonify(
                    status="error",
                    message="You do not have permission to perform this action",
                ), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


login_required = roles_required("manager", "cashier")
manager_required = roles_required("manager")
