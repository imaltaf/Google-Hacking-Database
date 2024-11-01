# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Set environment variables for Telegram bot
ENV TELEGRAM_TOKEN="your_telegram_token"
ENV CHAT_ID="your_chat_id"

# Expose port 5000 for Flask server
EXPOSE 5000

# Run the main script
CMD ["python", "main.py"]