import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_movie_exists(request):
    """Автоматически мокает проверку фильма во всех тестах, кроме интеграционных"""
    if "test_integration" in request.module.__name__:
        yield
    else:
        with patch('app.utils.django_client.DjangoAPIClient.movie_exists', return_value=True) as m:
            yield m
