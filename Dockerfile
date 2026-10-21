FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["sh", "-c", "flask --app wsgi:app db upgrade && gunicorn --bind 0.0.0.0:$PORT wsgi:app"]
