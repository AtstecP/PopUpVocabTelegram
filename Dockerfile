# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for gTTS and cleanup
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
# Added python-dotenv so Jarvis can read your token!
RUN pip install --no-cache-dir aiogram apscheduler gTTS python-dotenv

# Copy your bot code and data
COPY . .

# Run the bot (Changed from main.py to bot.py)
CMD ["python", "bot.py"]