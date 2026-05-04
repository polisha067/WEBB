from functools import wraps
from flask import request, jsonify
from .utils.django_client import django_client
from .exceptions import UnauthorizedError, ForbiddenError, IntegrationError

def require_auth(f):
    """Базовая проверка: пользователь авторизован"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return jsonify({'error': {'code': 'UNAUTHORIZED', 'message': 'Token required'}}), 401

        token = auth_header.replace('Token ', '')
        try:
            request.current_user = django_client.verify_token(token)
        except UnauthorizedError:
            return jsonify({'error': {'code': 'UNAUTHORIZED', 'message': 'Invalid token'}}), 401
        except IntegrationError:
            return jsonify({'error': {'code': 'SERVICE_UNAVAILABLE', 'message': 'Auth service down'}}), 503

        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Проверка на админа (is_staff или is_superuser)"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if not request.current_user.get('can_moderate', False):
            return jsonify({
                'error': {'code': 'FORBIDDEN', 'message': 'Admin rights required'}
            }), 403
        return f(*args, **kwargs)
    return decorated_function