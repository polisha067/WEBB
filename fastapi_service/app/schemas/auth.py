from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


class UserCreate(BaseModel):
    """Схема регистрации пользователя"""
    username: str = Field(..., min_length=3, max_length=50, examples=["new_user"])
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8, examples=["StrongPass123!"])
    password_confirm: str = Field(..., min_length=8, examples=["StrongPass123!"])

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain uppercase letter and digit")
        return v


class LoginRequest(BaseModel):
    """Схема входа"""
    username: str = Field(..., examples=["dev_user"])
    password: str = Field(..., examples=["MyPass123"])


class TokenResponse(BaseModel):
    """Ответ с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class RefreshRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class TokenPayload(BaseModel):
    """Полезная нагрузка JWT"""
    sub: str
    username: str
    exp: int
    type: str  