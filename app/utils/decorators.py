from functools import wraps
from flask import jsonify, request
from app.models.user import User
import jwt, os


def validate_jwt(f):
    """
    Validates JWT tokens in incoming requests and authenticates users.

    Description:
    This decorator ensures that incoming requests contain a valid JWT token in the 'Authorization' header.
    If a valid token is found, it decodes it to extract user information.
    The wrapped function 'f' is then called with the user object if authentication is successful.

    Usage:
    Apply this decorator to routes that require JWT-based authentication for improved code organization.
    """

    @wraps(f)
    def _verify(*args, **kwargs):
        invalid_msg = {
            'message': 'Invalid token. Registration or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token.',
            'authenticated': False
        }
        print(request.headers)
        auth_headers = request.headers.get('Authorization', '').split()
        print(auth_headers)
        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            user = User.query.filter_by(id=data['user_id']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify


