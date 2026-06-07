# 💬 dZENcode Comments

SPA-додаток для коментарів із вкладеними відповідями, real-time оновленням через WebSocket, CAPTCHA та підтримкою файлів.

## Стек технологій

**Бекенд:**
- Python 3.13 / Django 6.0 / Django REST Framework
- PostgreSQL 17
- Django Channels 4 + Daphne (WebSocket/ASGI)
- Celery 5.4 + Redis 7 (черга задач)
- django-redis (кешування)
- djangorestframework-simplejwt (JWT авторизація)
- django-simple-captcha
- Pillow (обробка зображень)
- Docker + Docker Compose

**Фронтенд:**
- Vue 3 (Composition API + TypeScript)
- Tailwind CSS
- Axios
- lucide-vue-next

---

## Функціонал

- ✅ Додавання коментарів з полями: User Name, E-mail, Home page, текст, файл
- ✅ Вкладені відповіді (каскадне відображення без обмежень глибини)
- ✅ CAPTCHA для кожного коментаря
- ✅ Дозволені HTML-теги у тексті: `<a>`, `<code>`, `<i>`, `<strong>` — з перевіркою валідності XHTML
- ✅ Панель форматування тексту з кнопками [i], [strong], [code], [a]
- ✅ Попередній перегляд повідомлення перед відправкою
- ✅ Прикріплення файлів: JPG, PNG, GIF (авторесайз до 320×240), TXT (до 100 КБ)
- ✅ Lightbox для перегляду зображень у повному розмірі
- ✅ Сортування за User Name, E-mail, датою (за зростанням і спаданням)
- ✅ Пагінація — 25 коментарів на сторінку, LIFO за замовчуванням
- ✅ Real-time оновлення через WebSocket — новий коментар з'являється без перезавантаження
- ✅ Черга задач Celery — WebSocket відправка відбувається асинхронно через Redis
- ✅ Кешування списку коментарів через Redis (1 хвилина)
- ✅ JWT авторизація для захисту API
- ✅ Темна/світла тема із збереженням у localStorage
- ✅ Захист від XSS (валідація тегів на сервері) та SQL-ін'єкцій (Django ORM)

---

## Швидкий старт

### Вимоги

- Встановлений [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Запуск

```bash
# 1. Склонуй репозиторій
git clone https://github.com/Nikkeen22/dzencode-comments.git
cd dzencode-comments

# 2. Запусти всі контейнери (міграції застосовуються автоматично)
docker compose up --build
```

Після запуску відкрий у браузері:
- **Фронтенд:** http://localhost:5173
- **API бекенду:** http://localhost:8000/api/
- **Адмін-панель Django:** http://localhost:8000/admin/

> Перший запуск займає 1–2 хвилини, поки збираються Docker-образи.

### Зупинка

```bash
docker compose down
```

### Повне очищення разом із базою даних

```bash
docker compose down -v
```

---

## Архітектура

```
docker compose up --build запускає 5 контейнерів:

┌─────────────────┐     ┌──────────────────┐
│  Vue 3 (5173)   │────▶│  Django/Daphne   │
│   фронтенд      │  WS │  (8000)          │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │PostgreSQL│ │  Redis   │ │  Celery  │
             │  (5432)  │ │  (6379)  │ │  worker  │
             └──────────┘ └──────────┘ └──────────┘
```

- **PostgreSQL** — зберігає коментарі
- **Redis** — черга Celery + кеш + WebSocket channel layer
- **Celery worker** — асинхронно відправляє WebSocket повідомлення після створення коментаря

---

## Структура проекту

```
dzencode-comments/
├── core/                        # Налаштування Django
│   ├── settings.py              # Redis, Celery, JWT, Cache
│   ├── urls.py                  # Маршрути + JWT ендпоінти
│   ├── celery.py                # Налаштування Celery
│   ├── __init__.py              # Завантаження Celery при старті
│   ├── asgi.py                  # ASGI + WebSocket через Channels
│   └── wsgi.py
├── comments/                    # Основний додаток
│   ├── models.py                # Модель Comment
│   ├── serializers.py           # Валідація даних + CAPTCHA
│   ├── views.py                 # REST API ViewSet + кешування
│   ├── tasks.py                 # Celery task для WebSocket
│   ├── consumers.py             # WebSocket consumer
│   ├── routing.py               # WebSocket маршрути
│   └── urls.py                  # REST маршрути
├── frontend/                    # Vue 3 SPA
│   ├── Dockerfile
│   └── src/
│       ├── components/
│       │   ├── CommentForm.vue
│       │   ├── CommentItem.vue
│       │   ├── CommentList.vue
│       │   └── CaptchaWidget.vue
│       ├── api/comments.ts
│       └── types/comment.ts
├── schema.mwb                   # Схема БД (MySQL Workbench)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## API

| Метод | URL | Опис |
|-------|-----|------|
| GET | `/api/comments/` | Список коментарів (кешований) |
| POST | `/api/comments/` | Створити коментар |
| GET | `/api/captcha/refresh/` | Отримати нову CAPTCHA |
| POST | `/api/auth/token/` | Отримати JWT токен |
| POST | `/api/auth/token/refresh/` | Оновити JWT токен |
| WS | `ws://localhost:8000/ws/comments/` | WebSocket real-time |

**Параметри GET `/api/comments/`:**

| Параметр | Опис | Приклад |
|----------|------|---------|
| `page` | Номер сторінки | `?page=2` |
| `ordering` | Поле сортування | `?ordering=-created_at` |

---

## JWT авторизація

Отримати токен через Django admin користувача:
```bash
POST http://localhost:8000/api/auth/token/
Content-Type: application/json

{"username": "admin", "password": "пароль"}
```

Відповідь:
```json
{"access": "eyJ...", "refresh": "eyJ..."}
```

Використання токена:
```
Authorization: Bearer eyJ...
```

---

## Змінні середовища

| Змінна | Опис |
|--------|------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Хости через кому |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | PostgreSQL |
| `REDIS_URL` | URL Redis (за замовч. `redis://redis:6379/0`) |
| `CORS_ALLOWED_ORIGINS` | URL фронтенду через кому |

---

## Схема бази даних

Файл `schema.mwb` у корені репозиторію — схема БД у форматі MySQL Workbench.

Відкрити: `File → Open Model → schema.mwb`

Містить:
- Таблицю `comments_comment` з усіма полями
- Таблицю `captcha_captchastore`
- Foreign Key `fk_comment_parent`: `parent_id → id` (`ON DELETE CASCADE`)

---
