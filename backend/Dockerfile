# Use Alpine as the base image
FROM python:3.10-alpine

# Create a non-root user
RUN adduser -D appuser

# Install system dependencies required for psycopg2 and other libraries
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libpq-dev \
    postgresql-dev \
    build-base \
    python3-dev \
    py3-pip

# Check if /usr/bin/python exists before creating the symlink
RUN if [ ! -e /usr/bin/python ]; then ln -s /usr/bin/python3 /usr/bin/python; fi

# Set the working directory
WORKDIR /code

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set permissions for the non-root user
RUN chown -R appuser:appuser /code

# Switch to the non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Set a health check to ensure the container is running properly
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1


# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
