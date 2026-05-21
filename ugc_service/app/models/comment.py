from datetime import datetime, timezone

from .. import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    movie_id = db.Column(db.Integer, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True, index=True)
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    parent = db.relationship('Comment', remote_side=[id], backref='children')

    def to_dict(self, include_replies: bool = False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'parent_id': self.parent_id,
            'text': self.text,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_replies:
            data['replies'] = []
        return data
