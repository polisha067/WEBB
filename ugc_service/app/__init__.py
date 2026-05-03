import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from .config import config
from .exceptions import register_error_handlers

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
swagger = Swagger(template={
    'swagger': '2.0',
    'info': {
        'title': 'UGC Service API',
        'description': 'Микросервис пользовательского контента (отзывы, комментарии, рейтинги)',
        'version': '1.0.0'
    },
    'basePath': '/api/v1',
    'schemes': ['http', 'https']
})


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    if config_name not in config:
        config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    limiter.init_app(app)
    swagger.init_app(app)

    # Единый формат ошибок
    register_error_handlers(app)

    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'ugc'}), 200

    from .routes.moderation import moderation_bp
    app.register_blueprint(moderation_bp, url_prefix='/api/v1/moderation')

    return app