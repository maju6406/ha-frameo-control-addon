# GitHub Copilot Prompts for Frameo ADB Control API

This file contains useful prompts for working with GitHub Copilot on this standalone API project.

## General Development

### Understanding the Codebase
```
Explain how the ADB connection lifecycle works in this addon, from initialization to command execution
```

```
What are the key differences between USB and TCP connections in this implementation?
```

```
How does the addon integrate with Home Assistant's add-on system?
```

### Refactoring
```
Refactor the connection management code to use a connection class with USB and TCP implementations
```

```
Extract the ADB command execution logic into a separate module with proper error handling
```

```
Improve error handling in the API endpoints to provide more specific error messages
```

## Feature Development

### Adding New ADB Commands
```
Add an endpoint to get the screen resolution of the connected device using ADB shell commands
```

```
Implement a function to take screenshots from the Frameo device and return them as base64
```

```
Create an endpoint to install an APK file on the device via ADB
```

```
Add support for sending text input to the device using ADB input commands
```

### Connection Management
```
Implement automatic reconnection with exponential backoff when the ADB connection drops
```

```
Add a heartbeat mechanism to check connection health every 30 seconds
```

```
Create a connection pool to support multiple simultaneous device connections
```

```
Implement device discovery via mDNS for wireless ADB connections on the local network
```

### API Enhancements
```
Add WebSocket support for real-time device status updates
```

```
Implement request validation middleware using Pydantic models
```

```
Add rate limiting to prevent API abuse
```

```
Create comprehensive API documentation using OpenAPI/Swagger
```

## Testing & Quality

### Unit Tests
```
Create pytest unit tests for the ADB connection management functions
```

```
Write integration tests for the API endpoints using Quart test client
```

```
Add mock tests for USB device discovery without requiring actual hardware
```

```
Create fixtures for common test scenarios with ADB connections
```

### Error Handling
```
Improve exception handling to distinguish between connection timeouts, device errors, and network issues
```

```
Add retry logic for transient ADB failures with configurable attempts
```

```
Create custom exception classes for different ADB error scenarios
```

## Documentation

### Code Documentation
```
Add comprehensive docstrings to all functions following Google style
```

```
Generate API documentation from the code comments
```

```
Create inline comments explaining the complex USB transport initialization
```

### User Documentation
```
Write a troubleshooting guide for common connection issues
```

```
Create a guide for setting up wireless ADB debugging on Frameo devices
```

```
Document the API with example curl commands for each endpoint
```

## Performance & Optimization

```
Profile the application to identify performance bottlenecks in ADB operations
```

```
Optimize the USB device scanning to reduce discovery time
```

```
Implement caching for device information that doesn't change frequently
```

```
Add connection pooling to reuse established ADB connections
```

## Security

```
Implement request authentication using API tokens
```

```
Add input sanitization for all ADB shell commands to prevent injection
```

```
Create a security audit checklist for the addon
```

```
Implement secure key storage for ADB authentication keys
```

## Docker & Deployment

```
Optimize the Dockerfile to reduce image size using multi-stage builds
```

```
Add health check endpoints for Docker container monitoring
```

```
Enhance docker-compose configuration with additional services
```

```
Implement graceful shutdown handling for the container
```

## Monitoring & Logging

```
Add structured logging with JSON format for better log parsing
```

```
Implement metrics collection for API endpoint usage
```

```
Create a logging configuration file for different log levels per module
```

```
Add request/response logging middleware with sensitive data filtering
```

## Integration Features

### Device Management
```
Add support for managing multiple Frameo devices simultaneously
```

```
Implement device profiles to store connection preferences
```

```
Create a device status monitoring system with health checks
```

## Code Quality

```
Set up pre-commit hooks for linting and formatting with black and flake8
```

```
Add type hints to all functions and enable mypy strict mode
```

```
Create a code coverage report configuration with pytest-cov
```

```
Implement continuous integration workflow with GitHub Actions
```

## Debugging Helpers

```
Add a debug endpoint that returns the current connection state and device information
```

```
Create a logging decorator to trace function calls and execution time
```

```
Implement a debug mode that provides verbose ADB protocol information
```

## Example Complex Prompts

### Complete Feature Implementation
```
Implement a complete feature to monitor Frameo device battery level:
1. Add an ADB command to retrieve battery info
2. Create an API endpoint to expose the battery level
3. Add caching with 5-minute TTL
4. Include proper error handling
5. Add logging
6. Write unit tests
```

### Architecture Improvement
```
Redesign the connection management to support:
1. Connection pooling for multiple devices
2. Automatic reconnection with exponential backoff
3. Health monitoring with periodic checks
4. Clean separation of USB and TCP transports
5. Thread-safe operations
6. Proper resource cleanup on shutdown
```

### Full API Endpoint
```
Create a complete API endpoint to execute custom shell commands:
1. POST /execute with JSON body containing command
2. Input validation and sanitization
3. Command timeout handling
4. Response with stdout, stderr, and exit code
5. Security checks to prevent dangerous commands
6. Rate limiting
7. Comprehensive logging
8. Error responses with appropriate status codes
9. Unit tests
10. API documentation
```

## Quick Fixes

```
Fix the race condition in connection initialization
```

```
Resolve the USB device not found error when scanning
```

```
Fix memory leak in long-running connections
```

```
Correct the async/await usage in the USB transport wrapper
```
