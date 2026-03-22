# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for gTTS (if needed) and cleanup
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
# (Alternatively, just run pip install directly to skip a requirements.txt)
RUN pip install --no-cache-dir aiogram apscheduler gTTS

# Copy your bot code and data
COPY . .

# Run the bot
CMD ["python", "main.py"]