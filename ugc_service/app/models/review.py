from datetime import datetime
from .. import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    movie_id = db.Column(db.Integer, nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-10
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, hidden
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'rating': self.rating,
            'text': self.text,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }