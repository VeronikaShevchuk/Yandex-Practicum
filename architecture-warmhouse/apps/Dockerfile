FROM python:3.11-slim

WORKDIR /smart_home

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY smart_home/ ./smart_home/

# Создаем не-root пользователя для безопасности
RUN useradd --create-home --shell /bin/bash smart_home
USER smart_home

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["uvicorn", "smart_home.main:app", "--host", "0.0.0.0", "--port", "8080"]