# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (including bash)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements and install Python dependencies as root
COPY requirements.txt .
# Use the extra PyTorch CPU index for torch+cpu wheels
RUN pip install --upgrade pip && \
    pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt && \
    rm -rf /root/.cache /tmp/*

# Create a non-root user for security
RUN adduser --disabled-password appuser

WORKDIR /app

# Copy FastAPI app code
COPY app/ ./app

# Make sure appuser owns /app (optional, but safe)
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Start Uvicorn ASGI server using Python module style (prod-ready)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
