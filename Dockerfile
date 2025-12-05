FROM python:3.11-alpine

# Install system dependencies for USB and ADB
RUN apk add --no-cache \
    libusb-dev \
    build-base \
    linux-headers

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create data directory for ADB keys
RUN mkdir -p /data

# Expose API port
EXPOSE 5000

# Run the application
CMD ["python3", "app.py"]
