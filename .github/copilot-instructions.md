# GitHub Copilot Instructions for Frameo ADB Control API

## Project Overview

This is a **standalone REST API server** for controlling Frameo digital photo frames via ADB (Android Debug Bridge). The server runs as a containerized service and provides HTTP endpoints for USB and network communication with Frameo devices.

## Key Technologies & Architecture

- **Language**: Python 3.11+
- **Web Framework**: Quart (async Flask-like framework)
- **ADB Communication**: `adb-shell` library for USB and TCP connections
- **Container**: Docker with Alpine Linux base
- **USB Access**: Requires `libusb` and privileged container or device access
- **Persistence**: `/data` directory for ADB keys

## Project Structure

```
.
├── app.py              # Main Quart API server
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container image definition
├── docker-compose.yml # Docker Compose configuration
├── README.md          # User documentation
└── data/              # ADB keys storage (created at runtime)
```

## Code Style Guidelines

### Python
- Use async/await for I/O operations
- Follow PEP 8 style guide
- Use type hints where practical
- Prefer f-strings for string formatting
- Use logging extensively with appropriate levels (INFO, WARNING, ERROR)
- Handle exceptions gracefully with specific error messages

### API Design
- RESTful endpoints using Quart
- Return JSON responses
- Use appropriate HTTP status codes (200, 400, 500)
- Include error handling for all endpoints

### ADB Operations
- Always use try/except for ADB commands (they can fail)
- Provide clear feedback when device authorization is needed
- Support both USB (synchronous) and TCP (asynchronous) connections
- Use executor for blocking USB operations in async context

## Important Conventions

### Connection Management
- Maintain global `adb_client` for persistent connection
- Track connection type with `is_usb` boolean flag
- Close existing connections before creating new ones
- Use appropriate timeouts for device operations

### Authentication
- Store ADB keys in `/data/adbkey` for persistence
- Generate keys automatically if missing
- Provide clear user prompts for device authorization

### Error Handling
```python
# Always wrap ADB operations
try:
    result = await adb_client.shell("command")
except (AdbConnectionError, AdbTimeoutError) as e:
    _LOGGER.error(f"ADB operation failed: {e}")
    return jsonify({"error": str(e)}), 500
```

### Logging
```python
_LOGGER.info("Normal operation info")
_LOGGER.warning("Non-critical issues")
_LOGGER.error("Errors with details", exc_info=True)
```

## Common Patterns

### Running Sync Functions in Async Context
```python
async def _run_sync(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))

# Usage
result = await _run_sync(blocking_function, arg1, arg2)
```

### API Endpoint Structure
```python
@app.route("/endpoint", methods=["POST"])
async def endpoint_name():
    """Clear docstring explaining the endpoint."""
    _LOGGER.info("Request received for /endpoint")
    try:
        data = await request.get_json()
        # Validate input
        # Perform operation
        return jsonify({"status": "success"})
    except Exception as e:
        _LOGGER.error(f"Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
```

## Docker Deployment

### Container Requirements
- Base: `python:3.11-alpine`
- System packages: `libusb-dev`, `build-base`, `linux-headers`
- Privileged mode or device permissions for USB access
- Volume mount for `/dev/bus/usb`
- Volume mount for `/data` (ADB keys persistence)

### Docker Best Practices
- Use Alpine Linux for smaller image size
- Install system dependencies before Python packages
- Clean up package manager caches
- Single-stage build for simplicity
- Expose port 5000 for API access

## Testing & Debugging

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app directly
python app.py
```

### Container Testing
```bash
# Build locally
docker build -t frameo-adb-api .

# Run with USB access
docker run --privileged -v /dev/bus/usb:/dev/bus/usb \
  -v $(pwd)/data:/data \
  -p 5000:5000 frameo-adb-api

# Or use docker-compose
docker-compose up -d
```

### Common Issues
- **USB not detected**: Check `--privileged` flag or device permissions
- **Auth timeout**: Ensure user accepts USB debugging prompt on device
- **Connection drops**: Implement reconnection logic with exponential backoff

## Dependencies to Consider

### Python Packages
- `quart` - Async web framework
- `adb-shell` - ADB protocol implementation
- `usb1` - libusb Python bindings
- `pure-python-adb` - Alternative ADB library (if needed)

### System Packages
- `libusb-1.0-0` - USB device access
- `android-tools-adb` - ADB utilities (optional)

## API Endpoints to Implement

When adding new features, follow these patterns:

1. **Device Discovery**: GET endpoints returning lists
2. **Device Control**: POST endpoints with JSON body
3. **Device Status**: GET endpoints with device state
4. **Configuration**: GET/POST for settings management

## Security Considerations

- Validate all user inputs
- Use appropriate timeouts to prevent hanging
- Don't expose sensitive device information unnecessarily
- ADB keys should remain in `/data` directory only
- Implement rate limiting if exposed to wider network

## Documentation Standards

- Update README.md for user-facing changes
- Use docstrings for all functions and endpoints
- Comment complex ADB operations
- Provide example API requests/responses
- Document required device permissions

## Version Management

- Follow semantic versioning
- Update CHANGELOG for notable changes
- Tag releases in git
- Consider multi-architecture Docker builds for broader compatibility
