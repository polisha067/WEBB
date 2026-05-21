from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from .. import db
from ..middleware import require_auth
from ..models.comment import Comment
from ..schemas.comment import CommentCreate, CommentUpdate

comments_bp = Blueprint('comments', __name__)


def _build_comment_tree(comments: list[Comment]) -> list[dict]:
    """Собирает список комментариев без вложенных ответов в дерево"""
    nodes: dict[int, dict] = {}
    for comment in comments:
        nodes[comment.id] = comment.to_dict(include_replies=True)

    roots: list[dict] = []
    for comment in comments:
        node = nodes[comment.id]
        if comment.parent_id is None:
            roots.append(node)
            continue
        parent = nodes.get(comment.parent_id)
        if parent is not None:
            parent['replies'].append(node)

    return roots


@comments_bp.route('/', methods=['POST'])
@require_auth
def create_comment():
    """Создать комментарий или ответ на другой комментарий"""
    try:
        data = CommentCreate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 422

    user_id = request.current_user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    if data.parent_id is not None:
        parent = Comment.query.get(data.parent_id)
        if not parent:
            return jsonify({'error': 'Родительский комментарий не найден'}), 404
        if parent.movie_id != data.movie_id:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'parent_id должен относиться к тому же фильму',
                },
            }), 400

    comment = Comment(
        user_id=user_id,
        movie_id=data.movie_id,
        parent_id=data.parent_id,
        text=data.text,
        status=data.status,
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201


@comments_bp.route('/', methods=['GET'])
def get_comments():
    """Список комментариев фильма с вложенностью (только active)."""
    movie_id = request.args.get('movie_id', type=int)
    if not movie_id:
        return jsonify({'error': 'Параметр movie_id обязателен'}), 400

    comments = (
        Comment.query.filter_by(movie_id=movie_id, status='active')
        .order_by(Comment.created_at.asc())
        .all()
    )
    return jsonify(_build_comment_tree(comments)), 200


@comments_bp.route('/<int:comment_id>/', methods=['PATCH'])
@require_auth
def update_comment(comment_id):
    """Редактировать комментарий (только автор)"""
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Комментарий не найден'}), 404

    user_id = request.current_user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    if comment.user_id != user_id:
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Только автор может редактировать комментарий',
            },
        }), 403

    try:
        data = CommentUpdate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 422

    comment.text = data.text
    comment.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(comment.to_dict()), 200


@comments_bp.route('/<int:comment_id>/', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """Удалить комментарий (автор или модератор)"""
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Комментарий не найден'}), 404

    user_id = request.current_user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    is_author = comment.user_id == user_id
    is_moderator = request.current_user.get('can_moderate', False)

    if not is_author and not is_moderator:
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Только автор или модератор может удалить комментарий',
            },
        }), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Комментарий удален'}), 200
