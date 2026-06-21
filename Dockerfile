# Base runtime image for the Flask API.
FROM python:3.12-slim

# Keep Python output unbuffered and bind the API to all interfaces in containers.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=5000

WORKDIR /app

# Run the container as a non-root user.
RUN adduser --disabled-password --gecos "" appuser

# Install Python dependencies separately to improve layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy only the application code needed at runtime.
COPY app ./app
COPY run.py .

# Pre-create the log directory and hand ownership to the runtime user.
RUN mkdir -p logs \
    && chown -R appuser:appuser /app

USER appuser

# Expose the Flask port
EXPOSE 5000

# Start the Flask API server on the container port.
CMD ["python", "run.py", "serve"]
