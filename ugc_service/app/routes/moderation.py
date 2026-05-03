from flask import Blueprint, request, jsonify
from flasgger import swag_from
from .. import db
from ..models import Review, Comment
from ..middleware import require_admin

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/reviews/pending/', methods=['GET'])
@require_admin
@swag_from('moderation.yaml', endpoint='get_pending_reviews')
def get_pending_reviews():
    """Получить отзывы на модерации с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    pagination = Review.query.filter_by(status='pending') \
        .order_by(Review.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'count': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'next': pagination.next_num if pagination.has_next else None,
        'prev': pagination.prev_num if pagination.has_prev else None,
        'results': [r.to_dict() for r in pagination.items]
    }), 200


@moderation_bp.route('/reviews/<int:review_id>/moderate/', methods=['PATCH'])
@require_admin
@swag_from('moderation.yaml', endpoint='moderate_review')
def moderate_review(review_id):
    """Сменить статус отзыва (active / hidden)"""
    review = Review.query.get_or_404(review_id)
    data = request.get_json()

    new_status = data.get('status')
    if new_status not in ['active', 'hidden']:
        return jsonify({'error': 'Invalid status'}), 400

    review.status = new_status
    db.session.commit()

    return jsonify({'message': 'Status updated', 'review': review.to_dict()}), 200


@moderation_bp.route('/comments/pending/', methods=['GET'])
@require_admin
@swag_from('moderation.yaml', endpoint='get_pending_comments')
def get_pending_comments():
    """Получить комментарии на модерации с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    pagination = Comment.query.filter_by(status='pending') \
        .order_by(Comment.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'count': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'next': pagination.next_num if pagination.has_next else None,
        'prev': pagination.prev_num if pagination.has_prev else None,
        'results': [c.to_dict() for c in pagination.items]
    }), 200


@moderation_bp.route('/comments/<int:comment_id>/moderate/', methods=['PATCH'])
@require_admin
@swag_from('moderation.yaml', endpoint='moderate_comment')
def moderate_comment(comment_id):
    """Сменить статус комментария (active / hidden)"""
    comment = Comment.query.get_or_404(comment_id)
    data = request.get_json()

    new_status = data.get('status')
    if new_status not in ['active', 'hidden']:
        return jsonify({'error': 'Invalid status'}), 400

    comment.status = new_status
    db.session.commit()

    return jsonify({'message': 'Status updated', 'comment': comment.to_dict()}), 200