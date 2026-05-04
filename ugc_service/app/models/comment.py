from datetime import datetime
from .. import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    movie_id = db.Column(db.Integer, nullable=False, index=True)
    parent_id = db.Column(db.Integer, nullable=True)  # Для ответов на комментарии
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'parent_id': self.parent_id,
            'text': self.text,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }