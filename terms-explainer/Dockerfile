FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for pymupdf
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy project files
COPY app/ ./app
COPY static/ ./static
COPY requirements.txt .
COPY .env .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
