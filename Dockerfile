# Use Python slim image as the base image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Set PYTHONPATH to include the current working directory
ENV PYTHONPATH=/app

# Install system dependencies required for Playwright and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libasound2 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy the Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pipenv install --deploy --system

# Install Playwright and its dependencies
RUN pip install --no-cache-dir playwright \
    && playwright install --with-deps

# Copy the application files into the container
COPY . .

# Set the command to run the application
CMD ["python", "scrapy_project/main.py"]
