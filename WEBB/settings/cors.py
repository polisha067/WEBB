# CORS настройки для фронтенда

import os

CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')

CORS_ALLOW_CREDENTIALS = True