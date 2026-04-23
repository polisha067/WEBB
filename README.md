# Cinema Project

Django REST API для кинотеатра - второй спринт.

- Сервисный слой на каждое приложение
- Доменные исключения с маппингом на HTTP-статусы
- Кастомные permissions
- Покрытие тестами ключевой бизнес-логики

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
| **Веб-сайт** | `http://localhost:8000/` |
| **Админка** | `http://localhost:8000/admin/` |
| **Swagger (API docs)** | `http://localhost:8000/api/docs/` |

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

## Структура проекта (второй спринт)

```
project/
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

## API Документация

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