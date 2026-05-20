import pytest
from app import create_app, db
from app.models.rating import Rating
from unittest.mock import patch

@pytest.fixture
def app():
    """Создаем тестовое приложение с тестовым конфигом"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Тестовый клиент для имитации HTTP-запросов"""
    return app.test_client()

@patch('app.middleware.django_client.verify_token')
def test_create_rating_success(mock_verify, client):
    """Проверка успешного создания оценки"""
    mock_verify.return_value = {'id': 1, 'username': 'test_user'}
    
    response = client.post('/api/v1/ratings/', json={
        "movie_id": 100,
        "score": 8
    }, headers={'Authorization': 'Token fake_token'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["movie_id"] == 100
    assert data["score"] == 8
    assert "id" in data

@patch('app.middleware.django_client.verify_token')
def test_create_rating_validation_error(mock_verify, client):
    """Проверка работы Pydantic валидации (оценка > 10)"""
    mock_verify.return_value = {'id': 1, 'username': 'test_user'}
    
    response = client.post('/api/v1/ratings/', json={
        "movie_id": 100,
        "score": 15
    }, headers={'Authorization': 'Token fake_token'})
    
    assert response.status_code == 422
    data = response.get_json()
    assert any(error.get("loc") == ["score"] for error in data)

def test_get_movie_ratings(client):
    """Проверка получения списка оценок фильма"""
    from app.models.rating import Rating
    from app import db
    
    rating = Rating(user_id=1, movie_id=200, score=5)
    db.session.add(rating)
    db.session.commit()
    
    # Проверяем наш публичный GET-роут
    response = client.get('/api/v1/ratings/?movie_id=200')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["movie_id"] == 200

def test_get_average_rating(client):
    """Проверка правильности подсчета среднего рейтинга"""
    from app.models.rating import Rating
    from app import db
    
    r1 = Rating(user_id=1, movie_id=300, score=10)
    r2 = Rating(user_id=2, movie_id=300, score=8)
    r3 = Rating(user_id=3, movie_id=300, score=6)
    db.session.add_all([r1, r2, r3])
    db.session.commit()

    response = client.get('/api/v1/ratings/average/?movie_id=300')
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["movie_id"] == 300
    assert data["average_score"] == 8.0
    assert data["total_votes"] == 3