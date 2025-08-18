FROM python:3.12-slim

WORKDIR /app
# Копируем код бота
COPY . .
RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "bot.py"]