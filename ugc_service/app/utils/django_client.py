import requests
import logging
from flask import current_app
from ..exceptions import MovieNotFoundError, IntegrationError, UnauthorizedError

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 5.0

    def movie_exists(self, movie_id: int) -> bool:
        """Проверяет существование фильма в Django API"""
        base_url = current_app.config.get('DJANGO_API_URL', 'http://web:8000/api')
        url = f"{base_url}/movies/{movie_id}/"

        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                logger.error(
                    f"Django API returned unexpected status {response.status_code} "
                    f"for movie {movie_id}: {response.text[:200]}"
                )
                raise IntegrationError(
                    f"Django API returned {response.status_code}",
                    details={'movie_id': movie_id, 'status': response.status_code}
                )

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Django API at {base_url}: {e}")
            raise IntegrationError(
                "Cannot connect to Django API",
                details={'url': url, 'error': str(e)}
            )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout connecting to Django API for movie {movie_id}: {e}")
            raise IntegrationError(
                "Timeout connecting to Django API",
                details={'movie_id': movie_id, 'url': url}
            )
        except requests.RequestException as e:
            logger.error(f"Request error to Django API: {e}")
            raise IntegrationError(
                "Request failed to Django API",
                details={'error': str(e)}
            )

    def get_movie(self, movie_id: int) -> dict:
        """Получает данные фильма из Django API"""
        base_url = current_app.config.get('DJANGO_API_URL', 'http://web:8000/api')
        url = f"{base_url}/movies/{movie_id}/"

        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise MovieNotFoundError(f"Movie {movie_id} not found")
            else:
                logger.error(
                    f"Django API returned unexpected status {response.status_code} "
                    f"for movie {movie_id}"
                )
                raise IntegrationError(
                    f"Django API returned {response.status_code}",
                    details={'movie_id': movie_id, 'status': response.status_code}
                )

        except (MovieNotFoundError, IntegrationError):
            raise
        except requests.RequestException as e:
            logger.error(f"Failed to fetch movie {movie_id} from Django API: {e}")
            raise IntegrationError(
                "Failed to fetch movie from Django API",
                details={'movie_id': movie_id, 'error': str(e)}
            )

    def verify_token(self, token: str) -> dict:
        """Проверяет токен через новый эндпоинт Django и возвращает права"""
        base_url = current_app.config.get('DJANGO_API_URL')
        url = f"{base_url}/accounts/verify/"
        headers = {'Authorization': f'Token {token}'}

        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise UnauthorizedError("Invalid token")
            else:
                raise IntegrationError("Django API error")
        except requests.RequestException as e:
            logger.error(f"Auth service connection failed: {e}")
            raise IntegrationError("Auth service unavailable")


# Singleton
django_client = DjangoAPIClient()