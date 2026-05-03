from flask import jsonify

class UGCException(Exception):
    """Базовое исключение UGC-сервиса"""
    status_code = 500
    error_code = 'UGC_ERROR'

    def __init__(self, message, details=None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class UnauthorizedError(UGCException):
    status_code = 401
    error_code = 'UNAUTHORIZED'

class ForbiddenError(UGCException):
    status_code = 403
    error_code = 'FORBIDDEN'

class ResourceNotFoundError(UGCException):
    status_code = 404
    error_code = 'RESOURCE_NOT_FOUND'

class MovieNotFoundError(UGCException):
    status_code = 404
    error_code = 'MOVIE_NOT_FOUND'

class InputValidationError(UGCException):
    status_code = 400
    error_code = 'VALIDATION_ERROR'


class BusinessRuleError(UGCException):
    """Нарушение бизнес-правил (дубли, недопустимые статусы и т.д.)"""
    status_code = 400
    error_code = 'BUSINESS_RULE_VIOLATION'

class IntegrationError(UGCException):
    """Django API недоступен или вернул непредвиденную ошибку"""
    status_code = 503
    error_code = 'DJANGO_API_UNAVAILABLE'

def register_error_handlers(app):
    @app.errorhandler(UGCException)
    def handle_ugc_exception(error):
        return jsonify({
            'error': {
                'code': error.error_code,
                'message': error.message,
                'details': error.details
            }
        }), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': {'code': 'NOT_FOUND', 'message': 'Resource not found'}
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        return jsonify({
            'error': {'code': 'INTERNAL_ERROR', 'message': 'Server error'}
        }), 500