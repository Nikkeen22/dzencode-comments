# Використовуємо офіційний стабільний образ Python
FROM python:3.13-slim

# Встановлюємо системні залежності, необхідні для збірки деяких пакетів (наприклад, psycopg2 або Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Запускаємо оптимізацію для Python (не створювати .pyc файли, не буферизувати логи)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копіюємо файл залежностей і встановлюємо їх
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту в контейнер
COPY . /app/