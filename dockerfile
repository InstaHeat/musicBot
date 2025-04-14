FROM python:3.9-slim

# Устанавливаем зависимости и FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Запускаем бота
CMD ["python", "bot.py"]