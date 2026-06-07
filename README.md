# 💬 dZENcode Comments

SPA-додаток для коментарів із вкладеними відповідями, real-time оновленням через WebSocket, CAPTCHA та підтримкою файлів.

## 🌐 Живий сайт

**http://167.233.30.124**

---

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

## Швидкий старт (локально)

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

## Деплой на сервер

### 1. Змінні середовища

Перед деплоєм встанови змінні середовища для бекенду (у `docker-compose.yml` або через `.env`):

| Змінна | Локально | Production |
|--------|----------|------------|
| `SECRET_KEY` | insecure-key | згенеруй надійний ключ |
| `DEBUG` | `True` | `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `your-domain.com` |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | `https://your-domain.com` |
| `DB_HOST` / `DB_NAME` / ... | значення з compose | значення вашого PostgreSQL |
| `REDIS_URL` | `redis://redis:6379/0` | URL вашого Redis |

### 2. Змінні середовища для фронтенду

Файл `frontend/.env`:

```env
# Локально
VITE_API_URL=http://localhost:8000

# Production (замінити на реальний домен/IP)
VITE_API_URL=http://167.233.30.124
```

> **Важливо:** WebSocket URL автоматично будується з `VITE_API_URL`:
> `http://...` → `ws://...`, `https://...` → `wss://...`
> Тому окремо налаштовувати WS не потрібно.

### 3. Генерація SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Архітектура

```
docker compose up --build запускає 5 контейнерів (локальна розробка):
       > На production сервері додатково працює Nginx як reverse proxy на порту 80.

┌─────────────────┐     ┌──────────────────┐
│  Nginx (80)     │────▶│  Django/Daphne   │
│  Vue 3 (SPA)    │  WS │  (8000)          │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │PostgreSQL│ │  Redis   │ │  Celery  │
             │  (5432)  │ │  (6379)  │ │  worker  │
             └──────────┘ └──────────┘ └──────────┘
```

- **Nginx** — роздає збілдований Vue SPA та проксіює запити до Django
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
│   ├── Dockerfile               # Dev dockerfile
│   ├── Dockerfile.prod          # Production dockerfile (збірка + nginx)
│   ├── .env                     # VITE_API_URL
│   └── src/
│       ├── components/
│       │   ├── CommentForm.vue
│       │   ├── CommentItem.vue
│       │   ├── CommentList.vue
│       │   └── CaptchaWidget.vue
│       ├── api/comments.ts
│       └── types/comment.ts
├── nginx.conf                   # Nginx конфігурація для production
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
| WS | `ws://<host>/ws/comments/` | WebSocket real-time |

**Параметри GET `/api/comments/`:**

| Параметр | Опис | Приклад |
|----------|------|---------|
| `page` | Номер сторінки | `?page=2` |
| `ordering` | Поле сортування | `?ordering=-created_at` |

---

## Змінні середовища (бекенд)

| Змінна | Опис |
|--------|------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Хости через кому |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | PostgreSQL |
| `REDIS_URL` | URL Redis (за замовч. `redis://redis:6379/0`) |
| `CORS_ALLOWED_ORIGINS` | URL фронтенду через кому |

## Змінні середовища (фронтенд)

| Змінна | Опис |
|--------|------|
| `VITE_API_URL` | Базовий URL бекенду. WebSocket будується автоматично: `http` → `ws`, `https` → `wss` |

---

## Схема бази даних

Файл `schema.mwb` у корені репозиторію — схема БД у форматі MySQL Workbench.

Відкрити: `File → Open Model → schema.mwb`

Містить:
- Таблицю `comments_comment` з усіма полями
- Таблицю `captcha_captchastore`
- Foreign Key `fk_comment_parent`: `parent_id → id` (`ON DELETE CASCADE`)