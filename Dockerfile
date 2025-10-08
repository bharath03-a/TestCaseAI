# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml uv.lock ./

# Install uv for faster package management
RUN pip install uv

# Install Python dependencies using uv
RUN uv sync --frozen

# Copy the entire application
COPY . .

# Install the application in editable mode
RUN uv pip install -e .

# Create necessary directories
RUN mkdir -p /app/data /app/output /tmp/testcase_ai

# Default command
CMD ["python", "run.py"]
