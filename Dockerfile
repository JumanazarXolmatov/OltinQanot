FROM python:3.10-slim
WORKDIR /app
COPY oltin_qanot_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app/oltin_qanot_bot
CMD ["python", "oltin_qanot_bot/bot.py"]
