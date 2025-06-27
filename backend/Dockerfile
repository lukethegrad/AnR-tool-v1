# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set working directory in the container
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libxshmfence1 \
    libgbm-dev \
    libxrandr2 \
    libxdamage1 \
    libxcomposite1 \
    libxext6 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# 👇 Copy requirements.txt from backend folder (since build context is repo root)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright and its browser dependencies
RUN python -m playwright install --with-deps

# 👇 Copy all backend app files into the container
COPY backend/ .

# Run the Flask app
CMD ["python", "app.py"]
