from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from datetime import datetime, timezone
from flasgger import swag_from

from .. import db
from ..models.review import Review
from ..schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from ..middleware import require_auth, require_admin
from ..utils.django_client import django_client

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/', methods=['POST'])
@require_auth
@swag_from('../specs/reviews.yaml')
def create_review():
    """Создать новый отзыв"""
    try:
        data = ReviewCreate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 422

    user_id = request.current_user.get('id')
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 401

    # Проверка: пользователь может оставить только один отзыв на фильм
    existing_review = Review.query.filter_by(movie_id=data.movie_id, user_id=user_id).first()
    if existing_review:
        return jsonify({"error": "Вы уже оставили отзыв к этому фильму"}), 400

    # Проверка: существует ли фильм в Django
    try:
        if not django_client.movie_exists(data.movie_id):
            return jsonify({"error": "Фильм не найден в основной базе данных"}), 404
    except Exception as e:
        return jsonify({"error": "Не удалось проверить фильм (сервис недоступен)"}), 503

    
    review = Review(
        user_id=user_id,
        movie_id=data.movie_id,
        rating=data.rating,
        text=data.text,
        status=data.status
    )
    db.session.add(review)
    db.session.commit()
    
    return jsonify(review.to_dict()), 201


@reviews_bp.route('/', methods=['GET'])
@swag_from('../specs/reviews.yaml')
def get_reviews():
    """Получить список отзывов для фильма (только active)"""
    movie_id = request.args.get('movie_id', type=int)
    if not movie_id:
        return jsonify({"error": "Параметр movie_id обязателен"}), 400

    reviews = Review.query.filter_by(movie_id=movie_id, status='active').all()
    return jsonify([r.to_dict() for r in reviews]), 200


@reviews_bp.route('/<int:review_id>/', methods=['GET'])
@swag_from('../specs/reviews.yaml')
def get_review(review_id):
    """Получить детали отзыва по ID"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Отзыв не найден"}), 404
    
    return jsonify(review.to_dict()), 200


@reviews_bp.route('/<int:review_id>/', methods=['PATCH'])
@require_auth
@swag_from('../specs/reviews.yaml')
def update_review(review_id):
    """Редактировать отзыв (только автор)"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Отзыв не найден"}), 404

    user_id = request.current_user.get('id')
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 401

    # Проверка: только автор может редактировать
    if review.user_id != user_id:
        return jsonify({"error": {"code": "FORBIDDEN", "message": "Только автор может редактировать отзыв"}}), 403

    try:
        data = ReviewUpdate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 422

    # Обновляем поля если они переданы
    if data.rating is not None:
        review.rating = data.rating
    if data.text is not None:
        review.text = data.text
    
    review.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify(review.to_dict()), 200


@reviews_bp.route('/<int:review_id>/', methods=['DELETE'])
@require_auth
@swag_from('../specs/reviews.yaml')
def delete_review(review_id):
    """Удалить отзыв (автор или модератор)"""
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Отзыв не найден"}), 404

    user_id = request.current_user.get('id')
    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 401

    # Проверка: автор или модератор может удалить
    is_author = review.user_id == user_id
    is_moderator = request.current_user.get('can_moderate', False)
    
    if not is_author and not is_moderator:
        return jsonify({"error": {"code": "FORBIDDEN", "message": "Только автор или модератор может удалить отзыв"}}), 403

    db.session.delete(review)
    db.session.commit()
    
    return jsonify({"message": "Отзыв удален"}), 200