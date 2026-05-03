import requests
import logging
from flask import current_app
from ..exceptions import MovieNotFoundError

logger = logging.getLogger(__name__)

class DjangoAPIClient:
    def __init__(self):
        # Создаем сессию для переиспользования TCP-соединений (Keep-Alive)
        self.session = requests.Session()
        # Стандартный таймаут, чтобы запросы не вешали приложение
        self.timeout = 5.0

    def movie_exists(self, movie_id: int) -> bool:
        """Проверяет существование фильма в Django API"""
        # Берем URL из конфига Flask
        base_url = current_app.config.get('DJANGO_API_URL', 'http://web:8000/api')
        url = f"{base_url}/movies/{movie_id}/"

        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                # Если Django вернул 500 или другую ошибку
                logger.error(f"Django API returned status {response.status_code} for movie {movie_id}")
                return False

        except requests.exceptions.ConnectionError:
            logger.warning(f"Cannot connect to Django API at {base_url}")
            return False
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout connecting to Django API for movie {movie_id}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking movie {movie_id}: {e}")
            return False

# Singleton (один экземпляр на все приложение)
django_client = DjangoAPIClient()