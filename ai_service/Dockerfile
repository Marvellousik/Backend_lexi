FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (ffmpeg for audio conversion, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ai_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ai_service /app/ai_service

ENV PYTHONPATH=/app
ENV PORT=5005

EXPOSE 5005

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5005/health || exit 1

CMD ["python", "-m", "ai_service.cmd.main"]

