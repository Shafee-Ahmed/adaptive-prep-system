FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY .env.example .env

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the API server by default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]