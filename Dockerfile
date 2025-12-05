FROM python:3.11-alpine

# Install system dependencies for USB and ADB
RUN apk add --no-cache \
    libusb-dev \
    build-base \
    linux-headers

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml .
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir -e .

# Create data directory for ADB keys
RUN mkdir -p /data

# Expose API port
EXPOSE 5000

# Run the application using the installed command
CMD ["frameo-api"]
