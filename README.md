# Cinema Project

Django REST API + FastAPI (Microservice) - Третий спринт

- **Спринт 2**: Сервисный слой, кастомные exceptions, permissions, тесты на Django
- **Спринт 3**: FastAPI в роли API-шлюза (BFF) поверх Django
  - Асинхронное проксирование запросов к монолиту с Retry-логикой
  - Гибридная аутентификация: FastAPI JWT (Bearer) + Django Token
  - Фоновые задачи (Background Tasks) для тяжелых операций
  - Единый формат ошибок (JSON)
  - Покрытие тестами (Pytest, HTTPX, Mocking)
- **Спринт 4**: UGC-микросервис на Flask (Отзывы, Комментарии, Рейтинги)
  - Независимая БД PostgreSQL 15 (`ugc_db`)
  - Интеграция с основным монолитом (Django API) для проверки авторизации и фильмов
  - Swagger UI и полная изоляция домена пользовательского контента

## Быстрый старт

```bash
# Клонировать репозиторий
git clone <repo-url>
cd cinema_project

# Создать .env (пример ниже)
cp .env.example .env

# Запустить проект
docker-compose up --build

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser
```

После запуска проект доступен:

| Ресурс | URL |
|---|---|
| **Веб-сайт (Django SSR)** | `http://localhost:8000/` |
| **Админка (Django)** | `http://localhost:8000/admin/` |
| **FastAPI Swagger (API docs)** | `http://localhost:8001/docs` |
| **Django Swagger (Internal)** | `http://localhost:8000/api/docs/` |
| **UGC Swagger (Flask)** | `http://localhost:5001/apidocs/` |

## Технологии

- **Django 4.2** - веб-фреймворк
- **Django REST Framework 3.14** - API
- **PostgreSQL 15** (Docker)
- **Docker & Docker Compose**
- **Swagger / OpenAPI** (drf-spectacular)
- **Token-аутентификация** (DRF authtoken)
- **CORS** (django-cors-headers)
- **django-filter** + поиск + сортировка

## Переменные окружения

Скопируйте `.env.example` в `.env` и настройте под себя.

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `DJANGO_SECRET_KEY` | секретный ключ Django | `django-insecure-...` |
| `DEBUG` | режим отладки | `True` |
| `ALLOWED_HOSTS` | разрешённые хосты | `localhost,127.0.0.1,...` |
| `POSTGRES_DB` | имя БД | `cinema_db` |
| `POSTGRES_USER` | пользователь БД | `cinema_user` |
| `POSTGRES_PASSWORD` | пароль БД | `cinema_password` |
| `POSTGRES_HOST` | хост БД | `db` |
| `POSTGRES_PORT` | порт БД | `5432` |
| `CORS_ALLOWED_ORIGINS` | разрешённые origins | `http://localhost:8000,...` |

---

## Структура проекта (третий спринт)

```
project/
├── fastapi_service/     # FastAPI API-шлюз (JWT, Proxy, Background Tasks)
│   ├── app/
│   │   ├── api/         # Роутеры (auth, protected, health)
│   │   ├── core/        # Безопасность, БД, Конфиг
│   │   ├── schemas/     # Pydantic схемы
│   │   └── services/    # Асинхронные HTTP клиенты к Django
│   └── tests/           # Pytest тесты
├── ugc_service/         # Flask UGC Микросервис (Отзывы, Комменты, Рейтинги)
│   ├── app/
│   │   ├── models/      # SQLAlchemy модели
│   │   ├── routes/      # Blueprint-ы API
│   │   ├── schemas/     # Marshmallow / Pydantic схемы
│   │   └── middleware.py # Проверка токенов через Django
│   └── tests/           # Pytest (интеграционные)
├── accounts/            # регистрация, вход, выход, me
│   ├── services.py      # AccountService
│   ├── exceptions.py    # (использует core.exceptions)
│   └── tests/
├── movies/              # фильмы и жанры
│   ├── services.py      # MovieService
│   └── tests/
├── watchlist/           # список просмотра пользователя
│   ├── services.py      # WatchlistService
│   └── tests/
├── subscriptions/       # тарифы и подписки пользователей
│   ├── services.py      # SubscriptionService
│   └── tests/
├── core/                # общие утилиты
│   ├── conf.py          # единый слой конфигурации
│   ├── exceptions.py    # доменные исключения
│   └── exception_handler.py  # обработчик DRF
├── WEBB/settings/       # настройки Django
│   ├── base.py
│   ├── installed_apps.py
│   ├── middleware.py
│   ├── database.py
│   ├── cors.py
│   ├── templates.py
│   └── rest_framework.py
├── templates/           # шаблоны страниц
├── static/
├── media/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── manage.py
└── .gitignore
```

### Сервисный слой

Вся бизнес-логика вынесена в `services.py` каждого приложения:

| Приложение | Сервис | Методы |
|---|---|---|
| `accounts` | `AccountService` | `register`, `login`, `logout` |
| `movies` | `MovieService` | `get_top_rated`, `get_new_releases` |
| `subscriptions` | `SubscriptionService` | `activate`, `cancel`, `check_expired` |
| `watchlist` | `WatchlistService` | `add`, `remove`, `change_status`, `get_user_watchlist` |

### Доменные исключения (`core/exceptions.py`)

Все бизнес-ошибки наследуются от `DomainException` и автоматически преобразуются в HTTP-ответы через кастомный `exception_handler`.

| Исключение | HTTP-статус | Код ошибки |
|---|---|---|
| `InvalidCredentials` | 401 | `INVALID_CREDENTIALS` |
| `AccountDisabled` | 403 | `ACCOUNT_DISABLED` |
| `UsernameAlreadyExists` | 400 | `USERNAME_ALREADY_EXISTS` |
| `PasswordsDoNotMatch` | 400 | `PASSWORDS_DO_NOT_MATCH` |
| `AlreadySubscribed` | 400 | `ALREADY_SUBSCRIBED` |
| `SubscriptionAlreadyCancelled` | 400 | `SUBSCRIPTION_ALREADY_CANCELLED` |
| `AlreadyInWatchlist` | 400 | `ALREADY_IN_WATCHLIST` |

### Разрешения

- `IsOwnerOrReadOnly` - для watchlist и пользовательских подписок
- `IsAdminUser` - для редактирования фильмов/жанров/тарифов

---

## API Документация (FastAPI - Спринт 3)

Базовый URL: `http://localhost:8001/api/v1/`

### Аутентификация (`/auth/`)
| Метод | URL | Описание | Доступ |
|---|---|---|---|
| POST | `/auth/register` | Регистрация (прокси в Django) | Все |
| POST | `/auth/login` | Вход и получение JWT | Все |
| POST | `/auth/refresh` | Обновление JWT токенов | Все |

### Защищенные роуты (`/protected/`)
*Требуют заголовок `Authorization: Bearer <access_token>`*

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/protected/profile` | Получить профиль пользователя | Auth |
| GET | `/protected/recommendations` | Получить рекомендации фильмов | Auth |
| POST | `/protected/progress/report` | Запуск фоновой задачи отчета | Auth |

### Системные (`/system/`)
| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/ping` | Быстрый ответ сервиса | Все |
| GET | `/system/health` | Проверка БД | Все |
| GET | `/system/ready` | Проверка связи с Django | Все |

---

## API Документация (Flask UGC Микросервис - Спринт 4)

Базовый URL: `http://localhost:5001/api/v1/`

### Отзывы (`/reviews/`)
| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/reviews/?movie_id={id}` | Получить отзывы к фильму | Все |
| GET | `/reviews/{id}/` | Детали отзыва | Все |
| POST | `/reviews/` | Создать отзыв | Auth |
| PATCH | `/reviews/{id}/` | Редактировать отзыв | Автор |
| DELETE| `/reviews/{id}/` | Удалить отзыв | Автор/Модератор |

### Комментарии (`/comments/`)
| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/comments/?movie_id={id}` | Получить дерево комментариев | Все |
| POST | `/comments/` | Создать комментарий (или ответ) | Auth |
| PATCH | `/comments/{id}/` | Редактировать комментарий | Автор |
| DELETE| `/comments/{id}/` | Удалить комментарий | Автор/Модератор |

### Рейтинги (`/ratings/`)
| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/ratings/average/?movie_id={id}` | Средний рейтинг фильма | Все |
| GET | `/ratings/?movie_id={id}` | Все оценки фильма | Все |
| POST | `/ratings/` | Поставить/Обновить оценку (Upsert) | Auth |

### Модерация (`/moderation/`)
| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/moderation/reviews/pending/` | Отзывы ожидающие проверки | Admin |
| PATCH | `/moderation/reviews/{id}/moderate/` | Одобрить/отклонить отзыв | Admin |
| GET | `/moderation/comments/pending/` | Комментарии на проверку | Admin |
| PATCH | `/moderation/comments/{id}/moderate/`| Одобрить/отклонить коммент| Admin |

---

## API Документация (Django - Внутренняя логика)

Базовый URL: `http://localhost:8000/api/`

### Фильмы (`/movies/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/movies/` | Список фильмов (пагинация) | Все |
| GET | `/movies/{id}/` | Детали фильма | Все |
| POST | `/movies/` | Создать фильм | Admin |
| PUT/PATCH | `/movies/{id}/` | Редактировать фильм | Admin |
| DELETE | `/movies/{id}/` | Удалить фильм | Admin |

**Параметры фильтрации:**
- `?genres={id}` - по жанру
- `?release_year={year}` - по году
- `?rating={rating}` - по рейтингу
- `?search={query}` - поиск по названию/описанию
- `?ordering=title,-rating,release_year` - сортировка

---

### Жанры (`/movies/genres/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/movies/genres/` | Список жанров | Все |
| GET | `/movies/genres/{id}/` | Детали жанра | Все |
| POST | `/movies/genres/` | Создать жанр | Admin |
| PUT/PATCH | `/movies/genres/{id}/` | Редактировать жанр | Admin |
| DELETE | `/movies/genres/{id}/` | Удалить жанр | Admin |

**Параметры:**
- `?search={query}` - поиск по названию
- `?ordering=name,created_at` - сортировка

---

### Подписки - Тарифы (`/subscriptions/plans/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/subscriptions/plans/` | Список тарифов | Все |
| GET | `/subscriptions/plans/{id}/` | Детали тарифа | Все |
| POST | `/subscriptions/plans/` | Создать тариф | Admin |

**Параметры:**
- `?search={query}` - поиск по названию
- `?ordering=price,duration_days` - сортировка

---

### Подписки пользователя (`/subscriptions/my/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/subscriptions/my/` | Мои подписки | Auth |
| GET | `/subscriptions/my/{id}/` | Детали подписки | Auth (владелец) |
| POST | `/subscriptions/my/` | Купить подписку | Auth |
| POST | `/subscriptions/my/{id}/cancel/` | Отменить подписку | Auth (владелец) |

**Параметры:**
- `?status=active,expired,cancelled` - фильтрация по статусу

---

### Список просмотра (`/watchlist/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/watchlist/` | Мой список просмотра | Auth |
| GET | `/watchlist/{id}/` | Детали записи | Auth (владелец) |
| POST | `/watchlist/` | Добавить фильм | Auth |
| PUT/PATCH | `/watchlist/{id}/` | Изменить статус | Auth (владелец) |
| DELETE | `/watchlist/{id}/` | Удалить из списка | Auth (владелец) |

**Параметры:**
- `?status=want_to_watch,watching,watched` - фильтрация
- `?search={title}` - поиск по названию фильма
- `?ordering=-added_at,movie__title` - сортировка

**Статусы:**
- `want_to_watch` - Хочу посмотреть
- `watching` - Смотрю
- `watched` - Посмотрел

---

### Аккаунт (`/accounts/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| POST | `/accounts/register/` | Регистрация | Все |
| POST | `/accounts/login/` | Вход | Все |
| POST | `/accounts/logout/` | Выход | Auth |
| GET | `/accounts/me/` | Мои данные | Auth |

---

## Аутентификация

Используйте токен в заголовке:
```
Authorization: Token <ваш-токен>
```

Токен возвращается при регистрации и входе.

---

## Swagger документация

Откройте Swagger UI в браузере:
```
http://localhost:8000/api/docs/
```

---

## Запуск тестов

```bash
# Внутри контейнера
docker-compose exec web python manage.py test

# Проверить конкретное приложение
docker-compose exec web python manage.py test accounts
docker-compose exec web python manage.py test subscriptions
docker-compose exec web python manage.py test watchlist
docker-compose exec web python manage.py test movies
```