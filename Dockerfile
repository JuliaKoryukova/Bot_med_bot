# Базовый образ Python
FROM python:3.9-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остального кода
COPY . .

# Команда запуска бота
CMD ["python", "bot.py"]