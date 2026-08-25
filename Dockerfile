FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and image analysis
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend .

ENV PYTHONUNBUFFERED=1
ENV DEMO_MODE=true
ENV PORT=8000

EXPOSE 8000

CMD ["python", "-m", "app.main"]
