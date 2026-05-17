import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
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


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    if config_name not in config:
        config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Swagger конфигурация
    app.config['SWAGGER'] = {
        'title': 'UGC Service API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'Микросервис пользовательского контента (отзывы, комментарии, рейтинги)',
    }
    app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "securityDefinitions": {
            "TokenAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Введите токен в формате: Token <ваш_токен>"
            }
        }
    }

    Swagger(app, config=swagger_config)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Обработчики ошибок
    register_error_handlers(app)

    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'ugc'}), 200

    # Регистрация blueprint'ов
    from .routes.moderation import moderation_bp
    app.register_blueprint(moderation_bp, url_prefix='/api/v1/moderation')

    # Логирование (опционально)
    if not app.debug:
        log_dir = Path(app.root_path).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / 'app.log', maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info(f'UGC Service started with config: {config_name}')

    return app