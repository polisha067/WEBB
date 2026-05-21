import pytest
from app import create_app, db
from app.models.review import Review
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


class TestCreateReview:
    """Тесты для POST /api/v1/reviews/"""

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_success(self, mock_verify, client):
        """Проверка успешного создания отзыва"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 8,
            "text": "Это отличный фильм, мне очень понравился сюжет!"
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 201
        data = response.get_json()
        assert data["movie_id"] == 100
        assert data["rating"] == 8
        assert "id" in data
        assert data["status"] == "pending"

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_with_status(self, mock_verify, client):
        """Проверка создания отзыва со статусом"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 7,
            "text": "Хороший фильм, но есть недостатки.",
            "status": "active"
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "active"

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_rating_too_low(self, mock_verify, client):
        """Проверка валидации: рейтинг меньше 1"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 0,
            "text": "Это отличный фильм, мне очень понравился сюжет!"
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 422
        data = response.get_json()
        assert any(error.get("loc") == ["rating"] for error in data)

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_rating_too_high(self, mock_verify, client):
        """Проверка валидации: рейтинг больше 10"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 15,
            "text": "Это отличный фильм, мне очень понравился сюжет!"
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 422
        data = response.get_json()
        assert any(error.get("loc") == ["rating"] for error in data)

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_text_too_short(self, mock_verify, client):
        """Проверка валидации: текст короче 10 символов"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 8,
            "text": "Коротко"
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 422
        data = response.get_json()
        assert any(error.get("loc") == ["text"] for error in data)

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_no_auth(self, mock_verify, client):
        """Проверка создания отзыва без авторизации"""
        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 8,
            "text": "Это отличный фильм, мне очень понравился сюжет!"
        })

        assert response.status_code == 401

    @patch('app.middleware.django_client.verify_token')
    def test_create_review_invalid_token(self, mock_verify, client):
        """Проверка создания отзыва с невалидным токеном"""
        from app.exceptions import UnauthorizedError
        mock_verify.side_effect = UnauthorizedError("Invalid token")

        response = client.post('/api/v1/reviews/', json={
            "movie_id": 100,
            "rating": 8,
            "text": "Это отличный фильм, мне очень понравился сюжет!"
        }, headers={'Authorization': 'Token invalid_token'})

        assert response.status_code == 401


class TestGetReviews:
    """Тесты для GET /api/v1/reviews/?movie_id=X"""

    def test_get_reviews_success(self, client):
        """Проверка получения списка отзывов (только active)"""
        from app import db

        # Создаем отзывы с разными статусами
        r1 = Review(user_id=1, movie_id=200, rating=8, text="Отличный фильм!", status='active')
        r2 = Review(user_id=2, movie_id=200, rating=5, text="Нормально", status='active')
        r3 = Review(user_id=3, movie_id=200, rating=3, text="Плохо", status='hidden')
        r4 = Review(user_id=4, movie_id=200, rating=7, text="Хорошо", status='pending')

        db.session.add_all([r1, r2, r3, r4])
        db.session.commit()

        response = client.get('/api/v1/reviews/?movie_id=200')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2  # Только active отзывы
        assert all(r["status"] == "active" for r in data)

    def test_get_reviews_no_movie_id(self, client):
        """Проверка ошибки при отсутствии movie_id"""
        response = client.get('/api/v1/reviews/')

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_get_reviews_empty(self, client):
        """Проверка получения пустого списка"""
        response = client.get('/api/v1/reviews/?movie_id=999')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestGetReview:
    """Тесты для GET /api/v1/reviews/{id}/"""

    def test_get_review_success(self, client):
        """Проверка получения деталей отзыва"""
        from app import db

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()

        response = client.get(f'/api/v1/reviews/{review.id}/')

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == review.id
        assert data["movie_id"] == 100
        assert data["rating"] == 8

    def test_get_review_not_found(self, client):
        """Проверка ошибки при несуществующем отзыве"""
        response = client.get('/api/v1/reviews/999/')

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


class TestUpdateReview:
    """Тесты для PATCH /api/v1/reviews/{id}/"""

    @patch('app.middleware.django_client.verify_token')
    def test_update_review_success(self, mock_verify, client):
        """Проверка успешного обновления отзыва автором"""
        from app import db

        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()

        response = client.patch(f'/api/v1/reviews/{review.id}/', json={
            "rating": 9,
            "text": "Еще лучший фильм после повторного просмотра!"
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data["rating"] == 9
        assert data["text"] == "Еще лучший фильм после повторного просмотра!"

    @patch('app.middleware.django_client.verify_token')
    def test_update_review_partial(self, mock_verify, client):
        """Проверка частичного обновления отзыва"""
        from app import db

        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()

        response = client.patch(f'/api/v1/reviews/{review.id}/', json={
            "rating": 10
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data["rating"] == 10
        assert data["text"] == "Отличный фильм!"  # Текст не изменился

    @patch('app.middleware.django_client.verify_token')
    def test_update_review_not_author(self, mock_verify, client):
        """Проверка ошибки при попытке редактирования чужого отзыва"""
        from app import db

        mock_verify.return_value = {'id': 2, 'username': 'other_user'}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()

        response = client.patch(f'/api/v1/reviews/{review.id}/', json={
            "rating": 5
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 403
        data = response.get_json()
        assert "error" in data

    @patch('app.middleware.django_client.verify_token')
    def test_update_review_not_found(self, mock_verify, client):
        """Проверка ошибки при несуществующем отзыве"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.patch('/api/v1/reviews/999/', json={
            "rating": 5
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 404

    @patch('app.middleware.django_client.verify_token')
    def test_update_review_invalid_rating(self, mock_verify, client):
        """Проверка валидации рейтинга при обновлении"""
        from app import db

        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()

        response = client.patch(f'/api/v1/reviews/{review.id}/', json={
            "rating": 15
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 422


class TestDeleteReview:
    """Тесты для DELETE /api/v1/reviews/{id}/"""

    @patch('app.middleware.django_client.verify_token')
    def test_delete_review_by_author(self, mock_verify, client):
        """Проверка удаления отзыва автором"""
        from app import db

        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()
        review_id = review.id

        response = client.delete(f'/api/v1/reviews/{review_id}/', headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

        # Проверяем, что отзыв действительно удален
        deleted_review = Review.query.get(review_id)
        assert deleted_review is None

    @patch('app.middleware.django_client.verify_token')
    def test_delete_review_by_moderator(self, mock_verify, client):
        """Проверка удаления отзыва модератором"""
        from app import db

        mock_verify.return_value = {'id': 99, 'username': 'moderator', 'can_moderate': True}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()
        review_id = review.id

        response = client.delete(f'/api/v1/reviews/{review_id}/', headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

    @patch('app.middleware.django_client.verify_token')
    def test_delete_review_not_authorized(self, mock_verify, client):
        """Проверка ошибки при удалении чужого отзыва без прав модератора"""
        from app import db

        mock_verify.return_value = {'id': 2, 'username': 'other_user', 'can_moderate': False}

        review = Review(user_id=1, movie_id=100, rating=8, text="Отличный фильм!", status='active')
        db.session.add(review)
        db.session.commit()

        response = client.delete(f'/api/v1/reviews/{review.id}/', headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 403
        data = response.get_json()
        assert "error" in data

    @patch('app.middleware.django_client.verify_token')
    def test_delete_review_not_found(self, mock_verify, client):
        """Проверка ошибки при несуществующем отзыве"""
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.delete('/api/v1/reviews/999/', headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 404

    def test_delete_review_no_auth(self, client):
        """Проверка удаления без авторизации"""
        response = client.delete('/api/v1/reviews/1/')

        assert response.status_code == 401