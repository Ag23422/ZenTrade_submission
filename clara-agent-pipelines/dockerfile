# Base Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for whisper/audio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
