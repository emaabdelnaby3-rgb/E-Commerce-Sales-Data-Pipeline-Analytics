from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt


def require_roles(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            roles = set(claims.get("roles", []))
            if not roles.intersection(set(allowed_roles)):
                return jsonify({"error": "forbidden"}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator
