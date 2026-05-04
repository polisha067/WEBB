# Контракты интеграции FastAPI <-> Django

## 1. Архитектура взаимодействия
- Обмен данными строго через HTTP/REST внутри Docker-сети (`http://web:8000/api`)
- Все вызовы из FastAPI выполняются асинхронно через `httpx.AsyncClient`
- FastAPI не имеет прямого доступа к базе данных Django. Данные пользователей, фильмов и подписок запрашиваются через публичный DRF API
- Аутентификация проходит через прокси-верификацию токена в Django (`GET /api/accounts/me/`)

## 2. DTO (Data Transfer Objects)

### Пользователь (GET /api/accounts/me/)
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

### Фильм (GET /api/movies/{id}/)
```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "duration": 120,
  "rating": 8.5,
  "release_year": 2023,
  "genres": [{"id": 1, "name": "Action"}, {"id": 2, "name": "Sci-Fi"}],
  "poster": "https://...",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

### Тарифный план (GET /api/subscriptions/plans/{id}/)
```json
{
  "id": 1,
  "name": "Premium",
  "price": 499.00,
  "duration_days": 30,
  "features": "4K\nБез рекламы\nОфлайн",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Подписка пользователя (GET /api/subscriptions/my/{id}/)
```json
{
  "id": 1,
  "subscription_name": "Premium",
  "purchased_at": "2023-10-01T00:00:00Z",
  "expires_at": "2023-10-31T00:00:00Z",
  "status": "active",
  "is_active": true
}
```

### Элемент списка просмотра (GET /api/watchlists/{id}/)
```json
{
  "id": 1,
  "movie_title": "Inception",
  "status": "want_to_watch",
  "added_at": "2023-10-01T00:00:00Z"
}
```

## 3. Маппинг ошибок
Django возвращает ошибки через `custom_exception_handler` или стандартный DRF:
```json
{"detail": "Человекочитаемое сообщение", "code": "ERROR_CODE"}
```
или
```json
{"detail": "Человекочитаемое сообщение"}
```
FastAPI нормализует все ответы к единому формату Спринта 2:
```json
{"detail": {"code": "ERROR_CODE", "message": "Человекочитаемое сообщение"}}
```

Таблица соответствия статусов:

| Django Status | FastAPI Status | FastAPI Code       | Описание                          |
|---------------|----------------|--------------------|-----------------------------------|
| 400           | 400            | VALIDATION_ERROR   | Ошибка валидации/бизнес-правила   |
| 401           | 401            | UNAUTHORIZED       | Токен невалиден/отсутствует       |
| 403           | 403            | FORBIDDEN          | Недостаточно прав                 |
| 404           | 404            | NOT_FOUND          | Ресурс не найден                  |
| 409           | 409            | CONFLICT           | Нарушение уникальности/инварианта |
| 500           | 503            | DJANGO_API_ERROR   | Внутренняя ошибка Django          |

## 4. Аутентификация и авторизация
- Клиент передаёт заголовок `Authorization: Token <drf_token_key>`
- FastAPI проксирует запрос к `GET /api/accounts/me/` с тем же заголовком
- При успехе (`200 OK`) извлекается payload пользователя и передаётся в контекст запроса
- При `401` или `403` запрос прерывается с соответствующим кодом FastAPI.]
- Swagger UI настроен на формат `Token <key>` (не Bearer)

## 5. Политика повторных попыток (Retry Policy)
- Timeout: 5.0 секунд на один запрос (настраивается в `.env`)
- Retries: 2 попытки при ошибках сети (`httpx.RequestError`) или ответах `5xx`
- Backoff: Экспоненциальная задержка: `1s -> 2s`
- Circuit Breaker: После 5 последовательных ошибок - отключение вызова на 30 секунд, возврат клиенту `503 Service Unavailable`.
- Идемпотентность: GET-запросы безопасны. POST/PUT/PATCH требуют заголовка `X-Request-ID` или `X-Idempotency-Key` для предотвращения дублирования операций на стороне Django

## 6. Правила асинхронной безопасности (Async-Safety Rules)
ЗАПРЕЩЕНО в async-контексте:
- `time.sleep()` > использовать `await asyncio.sleep()`
- `requests.get/post()` -> использовать `httpx.AsyncClient`
- Синхронные драйверы БД (`psycopg2`, `mysqlclient`) -> только `asyncpg`, `aiomysql`
- Блокирующие вызовы ОС или тяжёлые CPU-вычисления без `run_in_executor`
- Чтение/запись файлов синхронными методами внутри обработчиков

РАЗРЕШЕНО:
- `await httpx.AsyncClient().request(...)`
- `await session.execute(...)` (Async SQLAlchemy)
- `BackgroundTasks` для отложенных операций (запускаются строго после `return` ответа)
- `asyncio.gather()` для параллельных независимых вызовов
- `aiofiles` для асинхронной работы с файловой системой

## 7. Контекст логирования
Каждый лог межсервисного взаимодействия выводится в stdout в формате JSON и содержит:
```json
{
  "request_id": "uuid-v4",
  "user_id": 123,
  "target_service": "django_core",
  "endpoint": "GET /api/movies/456",
  "status_code": 200,
  "duration_ms": 145,
  "retry_count": 0,
  "error": null,
  "timestamp": "2024-05-04T15:07:00Z"
}
```

## 8. Версионирование API
- Базовый путь бизнес-эндпоинтов: `/api/v1/`
- Инфраструктурные эндпоинты (`/system/health`, `/system/ready`) находятся вне версионирования
- Изменения, ломающие обратную совместимость (удаление полей, смена типов, переименование путей) -> новая мажорная версия (`/api/v2/`)
- Все DTO строго типизированы через Pydantic и синхронизированы с DRF serializers
- Заголовок `Accept-Version` опционален для клиентов, используется для канареечных развёртываний