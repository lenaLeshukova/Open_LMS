# Используем официальный slim-образ Python 3.12
FROM python:3.12-slim

# Системные переменные для корректной работы Python в Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем системные зависимости для сборки библиотек (включая psycopg для базы данных)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry inside контейнера
RUN curl -sSL https://python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Настраиваем Poetry, чтобы он не создавал виртуальное окружение внутри контейнера
RUN poetry config virtualenvs.create false

# Копируем только файлы зависимостей Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости проекта через Poetry (пропуская dev-зависимости)
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем весь остальной исходный код приложения в контейнер
COPY . .

# Создаем директорию для медиафайлов
RUN mkdir -p /app/media

# Пробрасываем порт, который будет использовать Django
EXPOSE 8000
