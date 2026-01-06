FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for pymupdf & torch
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    wget \
    curl \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY app/ ./app
COPY static/ ./static

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
