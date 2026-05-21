from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    """Схема для POST /api/v1/comments/"""

    movie_id: int = Field(..., ge=1, description="ID фильма")
    text: str = Field(..., min_length=10, max_length=3000, description="Текст комментария 10–3000 символов")
    parent_id: Optional[int] = Field(None, ge=1, description="ID родительского комментария для ответа")
    status: Optional[Literal['active', 'hidden', 'pending']] = 'pending'

    model_config = ConfigDict(extra='forbid')


class CommentUpdate(BaseModel):
    """Схема для PATCH /api/v1/comments/{id}/"""

    text: str = Field(..., min_length=10, max_length=3000, description="Новый текст комментария")

    model_config = ConfigDict(extra='forbid')


class CommentResponse(BaseModel):
    """Представление комментария без вложенных ответов"""

    id: int
    user_id: int
    movie_id: int
    parent_id: Optional[int] = None
    text: str
    status: Literal['active', 'hidden', 'pending']
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CommentTreeNode(CommentResponse):
    """Комментарий с вложенными ответами"""

    replies: list['CommentTreeNode'] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
