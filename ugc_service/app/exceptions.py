from flask import jsonify

class UGCException(Exception):
    status_code = 500
    error_code = 'UGC_ERROR'
    def __init__(self, message, details=None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class MovieNotFoundError(UGCException):
    status_code = 404
    error_code = 'MOVIE_NOT_FOUND'

class ValidationError(UGCException):
    status_code = 400
    error_code = 'VALIDATION_ERROR'

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
        return jsonify({'error': {'code': 'NOT_FOUND', 'message': 'Not found'}}), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({'error': {'code': 'INTERNAL_ERROR', 'message': 'Server error'}}), 500