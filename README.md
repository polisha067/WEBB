# Cinema Project

Django REST API для кинотеатра

## Быстрый старт

```bash
# Запустить проект
docker-compose up --build

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser

# Открыть админку
http://localhost:8000/admin/
```

## Технологии

- Django 4.2
- Django REST Framework
- PostgreSQL
- Docker

## Переменные окружения

Скопируйте `.env.example` в `.env` и настройте

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
- `?genres={id}` — по жанру
- `?release_year={year}` — по году
- `?rating={rating}` — по рейтингу
- `?search={query}` — поиск по названию/описанию
- `?ordering=title,-rating,release_year` — сортировка

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
- `?search={query}` — поиск по названию
- `?ordering=name,created_at` — сортировка

---

### Подписки — Тарифы (`/subscriptions/plans/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/subscriptions/plans/` | Список тарифов | Все |
| GET | `/subscriptions/plans/{id}/` | Детали тарифа | Все |
| POST | `/subscriptions/plans/` | Создать тариф | Admin |

**Параметры:**
- `?search={query}` — поиск по названию
- `?ordering=price,duration_days` — сортировка

---

### Подписки пользователя (`/subscriptions/my/`)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/subscriptions/my/` | Мои подписки | Auth |
| GET | `/subscriptions/my/{id}/` | Детали подписки | Auth (владелец) |
| POST | `/subscriptions/my/` | Купить подписку | Auth |
| POST | `/subscriptions/my/{id}/cancel/` | Отменить подписку | Auth (владелец) |

**Параметры:**
- `?status=active,expired,cancelled` — фильтрация по статусу

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
- `?status=want_to_watch,watching,watched` — фильтрация
- `?search={title}` — поиск по названию фильма
- `?ordering=-added_at,movie__title` — сортировка

**Статусы:**
- `want_to_watch` — Хочу посмотреть
- `watching` — Смотрю
- `watched` — Посмотрел

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

---

## Swagger документация

Открыть UI: `http://localhost:8000/api/docs/`

---

## Структура проекта

```
c:\WEBB/
├── accounts/       # Пользователи, регистрация, логин
├── movies/         # Фильмы, жанры
├── subscriptions/  # Подписки, тарифы
├── watchlist/      # Список просмотра
├── templates/      # HTML шаблоны
├── staticfiles/    # Статика
└── WEBB/           # Настройки проекта
```
