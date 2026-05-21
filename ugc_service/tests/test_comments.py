import pytest
from unittest.mock import patch

from app import create_app, db
from app.models.comment import Comment


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestCreateComment:
    """POST /api/v1/comments/"""

    @patch('app.middleware.django_client.verify_token')
    def test_create_comment_success(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'text': 'Отличный фильм, Дайнерис крутая как всегда лол',
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['movie_id'] == 100
        assert data['user_id'] == 1
        assert data['parent_id'] is None
        assert data['status'] == 'pending'
        assert 'id' in data

    @patch('app.middleware.django_client.verify_token')
    def test_create_reply_success(self, mock_verify, client):
        mock_verify.return_value = {'id': 2, 'username': 'replier'}

        parent = Comment(
            user_id=1,
            movie_id=100,
            text='Корневой комментарий достаточной длинны',
            status='active',
        )
        db.session.add(parent)
        db.session.commit()

        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'parent_id': parent.id,
            'text': 'Согласен с автором, но дайнерис ваще фу, рыжая покруче',
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['parent_id'] == parent.id
        assert data['movie_id'] == 100

    @patch('app.middleware.django_client.verify_token')
    def test_create_reply_parent_not_found(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'parent_id': 9999,
            'text': 'Ответ на несуществующий комментарий здесь',
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 404

    @patch('app.middleware.django_client.verify_token')
    def test_create_reply_wrong_movie(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        parent = Comment(
            user_id=1,
            movie_id=200,
            text='Комментарий к другому фильму достаточной длины',
            status='active',
        )
        db.session.add(parent)
        db.session.commit()

        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'parent_id': parent.id,
            'text': 'Ответ с неверным movie_id для этого parent',
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @patch('app.middleware.django_client.verify_token')
    def test_create_comment_text_too_short(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'text': 'Коротко',
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 422
        data = response.get_json()
        assert any(error.get('loc') == ['text'] for error in data)

    @patch('app.middleware.django_client.verify_token')
    def test_create_comment_text_too_long(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'test_user'}

        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'text': 'x' * 3001,
        }, headers={'Authorization': 'Token fake_token'})

        assert response.status_code == 422

    @patch('app.middleware.django_client.verify_token')
    def test_create_comment_no_auth(self, mock_verify, client):
        response = client.post('/api/v1/comments/', json={
            'movie_id': 100,
            'text': 'Комментарий без авторизации достаточной длины',
        })

        assert response.status_code == 401


class TestGetComments:
    """GET /api/v1/comments/?movie_id=X"""

    def test_get_comments_nested_tree(self, client):
        root = Comment(
            user_id=1, movie_id=300, text='Корневой комментарий номер один',
            status='active',
        )
        reply = Comment(
            user_id=2, movie_id=300, parent_id=None,
            text='Ответ будет привязан после flush',
            status='active',
        )
        hidden = Comment(
            user_id=3, movie_id=300, text='Скрытый комментарий не должен попасть',
            status='hidden',
        )
        db.session.add_all([root, reply, hidden])
        db.session.flush()

        reply.parent_id = root.id
        nested_reply = Comment(
            user_id=4, movie_id=300, parent_id=reply.id,
            text='Вложенный ответ второго уровня в дереве',
            status='active',
        )
        db.session.add(nested_reply)
        db.session.commit()

        response = client.get('/api/v1/comments/?movie_id=300')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['id'] == root.id
        assert len(data[0]['replies']) == 1
        assert data[0]['replies'][0]['id'] == reply.id
        assert len(data[0]['replies'][0]['replies']) == 1
        assert data[0]['replies'][0]['replies'][0]['id'] == nested_reply.id

    def test_get_comments_only_active(self, client):
        active = Comment(
            user_id=1, movie_id=400,
            text='Активный комментарий виден в списке',
            status='active',
        )
        pending = Comment(
            user_id=2, movie_id=400,
            text='Ожидающий комментарий не виден в списке',
            status='pending',
        )
        db.session.add_all([active, pending])
        db.session.commit()

        response = client.get('/api/v1/comments/?movie_id=400')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['status'] == 'active'

    def test_get_comments_no_movie_id(self, client):
        response = client.get('/api/v1/comments/')
        assert response.status_code == 400

    def test_get_comments_empty(self, client):
        response = client.get('/api/v1/comments/?movie_id=999')
        assert response.status_code == 200
        assert response.get_json() == []


class TestUpdateComment:
    """PATCH /api/v1/comments/{id}/"""

    @patch('app.middleware.django_client.verify_token')
    def test_update_comment_success(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'author'}

        comment = Comment(
            user_id=1, movie_id=100,
            text='Исходный текст комментария автора',
            status='active',
        )
        db.session.add(comment)
        db.session.commit()

        response = client.patch(
            f'/api/v1/comments/{comment.id}/',
            json={'text': 'Обновленный текст комментария после редактирования'},
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == 'Обновленный текст комментария после редактирования'
        assert data['updated_at'] is not None

    @patch('app.middleware.django_client.verify_token')
    def test_update_comment_not_author(self, mock_verify, client):
        mock_verify.return_value = {'id': 2, 'username': 'other'}

        comment = Comment(
            user_id=1, movie_id=100,
            text='Чужой комментарий нельзя редактировать',
            status='active',
        )
        db.session.add(comment)
        db.session.commit()

        response = client.patch(
            f'/api/v1/comments/{comment.id}/',
            json={'text': 'Попытка изменить чужой комментарий здесь'},
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 403

    @patch('app.middleware.django_client.verify_token')
    def test_update_comment_not_found(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'author'}

        response = client.patch(
            '/api/v1/comments/999/',
            json={'text': 'Обновление несуществующего комментария'},
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 404

    @patch('app.middleware.django_client.verify_token')
    def test_update_comment_text_too_short(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'author'}

        comment = Comment(
            user_id=1, movie_id=100,
            text='Исходный текст комментария автора',
            status='active',
        )
        db.session.add(comment)
        db.session.commit()

        response = client.patch(
            f'/api/v1/comments/{comment.id}/',
            json={'text': 'Коротко'},
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 422


class TestDeleteComment:
    """DELETE /api/v1/comments/{id}/"""

    @patch('app.middleware.django_client.verify_token')
    def test_delete_comment_by_author(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'author'}

        comment = Comment(
            user_id=1, movie_id=100,
            text='Комментарий который удалит автор',
            status='active',
        )
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

        response = client.delete(
            f'/api/v1/comments/{comment_id}/',
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 200
        assert Comment.query.get(comment_id) is None

    @patch('app.middleware.django_client.verify_token')
    def test_delete_comment_by_moderator(self, mock_verify, client):
        mock_verify.return_value = {
            'id': 99, 'username': 'moderator', 'can_moderate': True,
        }

        comment = Comment(
            user_id=1, movie_id=100,
            text='Комментарий который удалит модератор',
            status='active',
        )
        db.session.add(comment)
        db.session.commit()

        response = client.delete(
            f'/api/v1/comments/{comment.id}/',
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 200

    @patch('app.middleware.django_client.verify_token')
    def test_delete_comment_forbidden(self, mock_verify, client):
        mock_verify.return_value = {
            'id': 2, 'username': 'other', 'can_moderate': False,
        }

        comment = Comment(
            user_id=1, movie_id=100,
            text='Чужой комментарий нельзя удалить без прав',
            status='active',
        )
        db.session.add(comment)
        db.session.commit()

        response = client.delete(
            f'/api/v1/comments/{comment.id}/',
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 403

    @patch('app.middleware.django_client.verify_token')
    def test_delete_comment_not_found(self, mock_verify, client):
        mock_verify.return_value = {'id': 1, 'username': 'author'}

        response = client.delete(
            '/api/v1/comments/999/',
            headers={'Authorization': 'Token fake_token'},
        )

        assert response.status_code == 404

    def test_delete_comment_no_auth(self, client):
        response = client.delete('/api/v1/comments/1/')
        assert response.status_code == 401
