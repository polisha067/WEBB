from fastapi import APIRouter

router = APIRouter()

# POST /auth/register - регистрация
# POST /auth/login - логин (возврат access + refresh)
# POST /auth/refresh - обновление токена
# POST /auth/logout - выход (опционально)