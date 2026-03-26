# База данных

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'cinema_db'),
        'USER': os.getenv('POSTGRES_USER', 'cinema_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'cinema_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}