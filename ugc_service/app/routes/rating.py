from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from sqlalchemy import func
from datetime import datetime, timezone
from flasgger import swag_from

from .. import db
from ..models.rating import Rating
from ..schemas.rating import RatingCreate, AverageRatingResponse
from ..middleware import require_auth
from ..utils.django_client import django_client

rating_bp = Blueprint('ratings', __name__)

@rating_bp.route('/', methods=['POST'])
@require_auth
@swag_from('../specs/rating.yaml')
def create_or_update_rating():
    """Поставить или обновить оценку (Upsert)"""
    try:
        data = RatingCreate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 422

    user_id = request.current_user.get('id') 

    if not user_id:
        return jsonify({"error": "User ID not found in token"}), 401

    # Проверка: существует ли фильм в Django
    try:
        if not django_client.movie_exists(data.movie_id):
            return jsonify({"error": "Фильм не найден в основной базе данных"}), 404
    except Exception as e:
        return jsonify({"error": "Не удалось проверить фильм (сервис недоступен)"}), 503

    rating = Rating.query.filter_by(movie_id=data.movie_id, user_id=user_id).first()

    if rating:
        rating.score = data.score
        rating.created_at = datetime.now(timezone.utc)
    else:
        rating = Rating(user_id=user_id, movie_id=data.movie_id, score=data.score)
        db.session.add(rating)

    db.session.commit()
    return jsonify(rating.to_dict()), 200


@rating_bp.route('/', methods=['GET'])
@swag_from('../specs/rating.yaml')
def get_movie_ratings():
    """Список всех оценок фильма"""
    movie_id = request.args.get('movie_id', type=int)
    if not movie_id:
        return jsonify({"error": "Параметр movie_id обязателен"}), 400

    ratings = Rating.query.filter_by(movie_id=movie_id).all()
    return jsonify([r.to_dict() for r in ratings]), 200


@rating_bp.route('/average/', methods=['GET'])
@swag_from('../specs/rating.yaml')
def get_average_rating():
    """Получить средний рейтинг фильма"""
    movie_id = request.args.get('movie_id', type=int)
    if not movie_id:
        return jsonify({"error": "Параметр movie_id обязателен"}), 400

    result = db.session.query(
        func.avg(Rating.score).label('average'),
        func.count(Rating.id).label('count')
    ).filter_by(movie_id=movie_id).first()

    total_votes = result.count if result and result.count else 0
    average_score = round(float(result.average), 1) if result and result.average else 0.0

    response_data = AverageRatingResponse(
        movie_id=movie_id,
        average_score=average_score,
        total_votes=total_votes
    )

    return jsonify(response_data.model_dump() if hasattr(response_data, 'model_dump') else response_data.dict()), 200