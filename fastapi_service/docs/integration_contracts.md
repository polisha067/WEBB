# Контракты интеграции FastAPI <-> Django

## 1. Общая архитектура взаимодействия
- FastAPI взаимодействует с основным Django-приложением строго через HTTP/REST
- Все межсервисные вызовы выполняются асинхронно с использованием `httpx.AsyncClient`
- Коммуникация происходит внутри общей Docker-сети по внутренним DNS-именам контейнеров (например, `http://web:8000/api`)
- FastAPI не имеет прямого доступа к базе данных Django. Все данные о пользователях и продуктах запрашиваются через публичный API Django

## 2. DTO (Data Transfer Objects)

### Регистрация / Вход (POST /api/accounts/register/, POST /api/accounts/login/)
Ответ обёрнут в единый формат с мета-информацией:
```json
{
  "status": "success",
  "message": "Пользователь успешно зарегистрирован",
  "user": {
    "username": "string",
    "email": "string"
  },
  "token": "drf_token_key_string"
}
```

### Данные текущего пользователя (GET /api/accounts/me/)
Прямой ответ сериализатора UserSerializer:
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

### Выход (POST /api/accounts/logout/)
```json
{
  "status": "success",
  "message": "Выход выполнен успешно"
}
```

Техническое примечание:
- Django использует DRF Token Authentication. FastAPI верифицирует сессию, передавая токен в заголовке `Authorization: Token <key>` к эндпоинту `/api/accounts/me/`
- Pydantic-модели в FastAPI должны строго соответствовать приведённым структурам для корректной авто-валидации и генерации OpenAPI

## 3. Маппинг ошибок

| Django HTTP Status | FastAPI HTTP Status | FastAPI Error Code   | Описание                                      |
|--------------------|---------------------|----------------------|-----------------------------------------------|
| 400 Bad Request    | 400                 | VALIDATION_ERROR     | Ошибка валидации входных данных               |
| 401 Unauthorized   | 401                 | UNAUTHORIZED         | Токен отсутствует, просрочен или невалиден    |
| 403 Forbidden      | 403                 | FORBIDDEN            | Недостаточно прав для выполнения операции     |
| 404 Not Found      | 404                 | NOT_FOUND            | Ресурс не найден в Django                     |
| 429 Too Many Requests | 429              | RATE_LIMITED         | Превышен лимит запросов                       |
| 500 Server Error   | 502/503             | DJANGO_API_ERROR     | Внутренняя ошибка Django или недоступность    |

Все ошибки в FastAPI возвращаются в едином формате, установленном в Спринте 2:
```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Человекочитаемое описание ошибки"
  }
}
```

## 4. Политика повторных попыток (Retry Policy)
- Timeout: 5.0 секунд на один запрос (настраивается в .env)
- Retries: 2 попытки при ошибках сети (ConnectionError, Timeout) или ответах 5xx
- Backoff: Экспоненциальная задержка: 1s -> 2s
- Circuit Breaker: После 5 последовательных ошибок - отключение вызова на 30 секунд, возврат клиенту 503 Service Unavailable
- Идемпотентность: GET-запросы безопасны. POST/PUT/PATCH требуют заголовка X-Request-ID для отслеживания дублей и предотвращения повторной обработки

## 5. Правила асинхронной безопасности (Async-Safety Rules)

ЗАПРЕЩЕНО в async-контексте:
- time.sleep() -> использовать await asyncio.sleep()
- requests.get/post() -> использовать httpx.AsyncClient
- Синхронные драйверы БД (psycopg2, mysqlclient) -> только asyncpg, aiomysql
- Блокирующие вызовы ОС или тяжёлые CPU-вычисления без run_in_executor
- Чтение/запись файлов синхронными методами внутри обработчиков запросов

РАЗРЕШЕНО:
- await httpx.AsyncClient().request(...)
- await session.execute(...) (Async SQLAlchemy)
- BackgroundTasks для отложенных операций (запускаются строго после return ответа клиенту)
- asyncio.gather() для параллельных независимых вызовов
- aiofiles для асинхронной работы с файловой системой

## 6. Контекст логирования
Каждый лог межсервисного взаимодействия должен содержать структурированные поля:
```json
{
  "request_id": "uuid-v4",
  "trace_id": "optional-jaeger-id",
  "user_id": 123,
  "target_service": "django_core",
  "endpoint": "GET /api/accounts/me/",
  "status_code": 200,
  "duration_ms": 145,
  "retry_count": 0,
  "error": null
}
```
Логи выводятся в stdout в формате JSON для последующего сбора системами мониторинга

## 7. Версионирование API
- Базовый путь бизнес-эндпоинтов: /api/v1/
- Изменения, ломающие обратную совместимость -> новая мажорная версия (/api/v2/)
- Инфраструктурные эндпоинты (/system/health, /system/ready) находятся вне версионирования
- Заголовок Accept-Version опционален для клиентов, используется для канареечных развёртываний
- Все изменения в контрактах DTO должны сопровождаться обновлением OpenAPI-спецификации и уведомлением команды интеграции

