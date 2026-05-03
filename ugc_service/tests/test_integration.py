import pytest
from app import create_app, db
from app.utils.django_client import django_client
from app.models import Review, Comment
from app.exceptions import UnauthorizedError, IntegrationError


@pytest.fixture
def app():
    """Создаёт тестовое приложение с SQLite в памяти"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'DJANGO_API_URL': 'http://test-django/api',
        'SECRET_KEY': 'test-secret-key'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_verify_token_success(app, requests_mock):
    """Успешная верификация токена через Django"""
    user_data = {'id': 1, 'username': 'admin', 'can_moderate': True}
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json=user_data,
        status_code=200,
        request_headers={'Authorization': 'Token valid_token'}
    )
    with app.app_context():
        result = django_client.verify_token('valid_token')
        assert result['can_moderate'] is True
        assert result['username'] == 'admin'


def test_verify_token_invalid(app, requests_mock):
    """Django возвращает 401 при невалидном токене"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        status_code=401
    )
    with app.app_context():
        with pytest.raises(UnauthorizedError, match="Invalid token"):
            django_client.verify_token('bad_token')


def test_verify_token_django_unavailable(app, requests_mock):
    """Django недоступен - IntegrationError"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        exc=ConnectionError("Django is down")
    )
    with app.app_context():
        with pytest.raises(IntegrationError, match="Auth service unavailable"):
            django_client.verify_token('any_token')


def test_movie_exists_true(app, requests_mock):
    """Фильм существует в Django (200)"""
    requests_mock.get('http://test-django/api/movies/123/', status_code=200)
    with app.app_context():
        assert django_client.movie_exists(123) is True


def test_movie_exists_false(app, requests_mock):
    """Фильм не найден в Django (404)"""
    requests_mock.get('http://test-django/api/movies/999/', status_code=404)
    with app.app_context():
        assert django_client.movie_exists(999) is False


def test_movie_exists_django_error(app, requests_mock):
    """Django вернул 500 → IntegrationError"""
    requests_mock.get('http://test-django/api/movies/555/', status_code=500)
    with app.app_context():
        with pytest.raises(IntegrationError):
            django_client.movie_exists(555)


def test_moderation_pending_success(client, requests_mock, app):
    """Админ получает список на модерации (200)"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 1, 'username': 'admin', 'can_moderate': True},
        status_code=200
    )
    with app.app_context():
        Review.query.delete()
        db.session.commit()

    response = client.get(
        '/api/v1/moderation/reviews/pending/',
        headers={'Authorization': 'Token admin_token'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'results' in data
    assert 'count' in data


def test_moderation_pending_forbidden(client, requests_mock):
    """Обычный юзер получает 403 Forbidden"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 2, 'username': 'user', 'can_moderate': False},
        status_code=200
    )
    response = client.get(
        '/api/v1/moderation/reviews/pending/',
        headers={'Authorization': 'Token user_token'}
    )
    assert response.status_code == 403
    assert response.get_json()['error']['code'] == 'FORBIDDEN'


def test_moderation_without_token(client):
    """Запрос без токена - 401 Unauthorized"""
    response = client.get('/api/v1/moderation/reviews/pending/')
    assert response.status_code == 401
    assert response.get_json()['error']['code'] == 'UNAUTHORIZED'

def test_moderation_comments_pending_success(client, requests_mock, app):
    """Админ получает список комментариев на модерации (200)"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 1, 'username': 'admin', 'can_moderate': True},
        status_code=200
    )
    with app.app_context():
        Comment.query.delete()
        db.session.commit()

    response = client.get(
        '/api/v1/moderation/comments/pending/',
        headers={'Authorization': 'Token admin_token'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'results' in data
    assert 'count' in data


def test_moderation_comments_forbidden(client, requests_mock):
    """Обычный юзер не может модерировать комментарии (403)"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 2, 'username': 'user', 'can_moderate': False},
        status_code=200
    )
    response = client.get(
        '/api/v1/moderation/comments/pending/',
        headers={'Authorization': 'Token user_token'}
    )
    assert response.status_code == 403

def test_moderate_review_success(client, requests_mock, app):
    """Админ успешно меняет статус отзыва"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 1, 'username': 'admin', 'can_moderate': True},
        status_code=200
    )
    with app.app_context():
        review = Review(
            user_id=1, movie_id=1, rating=8,
            text='Great movie!', status='pending'
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    response = client.patch(
        f'/api/v1/moderation/reviews/{review_id}/moderate/',
        json={'status': 'active'},
        headers={'Authorization': 'Token admin_token'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['review']['status'] == 'active'


def test_moderate_review_invalid_status(client, requests_mock, app):
    """Невалидный статус - 400"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 1, 'username': 'admin', 'can_moderate': True},
        status_code=200
    )
    with app.app_context():
        review = Review(
            user_id=1, movie_id=1, rating=8,
            text='Test', status='pending'
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    response = client.patch(
        f'/api/v1/moderation/reviews/{review_id}/moderate/',
        json={'status': 'invalid_status'},
        headers={'Authorization': 'Token admin_token'}
    )
    assert response.status_code == 400


def test_moderate_review_not_found(client, requests_mock):
    """Отзыв не найден - 404"""
    requests_mock.get(
        'http://test-django/api/accounts/verify/',
        json={'id': 1, 'username': 'admin', 'can_moderate': True},
        status_code=200
    )
    response = client.patch(
        '/api/v1/moderation/reviews/99999/moderate/',
        json={'status': 'active'},
        headers={'Authorization': 'Token admin_token'}
    )
    assert response.status_code == 404