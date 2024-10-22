# Use the official Python slim image as the base
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and to ensure stdout and stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for Playwright and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright browsers with dependencies
RUN playwright install --with-deps

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Set environment variables (These should be overridden in docker-compose.yaml for security)
ENV OPENAI_API_KEY=your-openai-api-key

# Default command (can be overridden by docker-compose)
CMD ["bash"]

