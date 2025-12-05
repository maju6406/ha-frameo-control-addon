# API Documentation

This directory contains interactive API documentation generated from the OpenAPI specification.

## Available Documentation Formats

### 1. Swagger UI (`index.html`)
Interactive API documentation with "Try it out" functionality.

**Features:**
- Interactive testing of all endpoints
- Request/response examples
- Schema validation
- Try endpoints directly from the browser

**To view:**
```bash
# Option 1: Open directly in browser
open docs/index.html

# Option 2: Serve with Python
python3 -m http.server 8080
# Then visit: http://localhost:8080/docs/

# Option 3: Serve with Node.js
npx http-server -p 8080
# Then visit: http://localhost:8080/docs/
```

### 2. ReDoc (`redoc.html`)
Beautiful three-panel API documentation.

**Features:**
- Clean, professional layout
- Three-panel design
- Search functionality
- Responsive design
- Code samples

**To view:**
```bash
# Serve the docs directory
python3 -m http.server 8080
# Then visit: http://localhost:8080/docs/redoc.html
```

### 3. Markdown Documentation (`../API.md`)
Complete API reference with examples in Markdown format.

**Features:**
- Human-readable documentation
- Python and JavaScript client examples
- Step-by-step workflows
- Troubleshooting guide

**To view:**
```bash
# View in any text editor or Markdown viewer
cat ../API.md
```

## Using with Docker

If you're running the API server with Docker, you can serve the documentation alongside:

```yaml
# Add to docker-compose.yml
services:
  frameo-adb-api:
    # ... existing config ...
  
  docs:
    image: nginx:alpine
    volumes:
      - ./docs:/usr/share/nginx/html/docs
      - ./openapi.yaml:/usr/share/nginx/html/openapi.yaml
      - ./API.md:/usr/share/nginx/html/API.md
    ports:
      - "8080:80"
```

Then access documentation at:
- Swagger UI: http://localhost:8080/docs/
- ReDoc: http://localhost:8080/docs/redoc.html

## Generating Client SDKs

Use the OpenAPI specification to generate client SDKs:

### Using OpenAPI Generator

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate Python client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o clients/python

# Generate JavaScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g javascript \
  -o clients/javascript

# Generate TypeScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o clients/typescript
```

### Using Swagger Codegen

```bash
# Install Swagger Codegen
brew install swagger-codegen

# Generate clients
swagger-codegen generate -i openapi.yaml -l python -o clients/python
swagger-codegen generate -i openapi.yaml -l javascript -o clients/javascript
```

## Importing into API Tools

### Postman
1. Open Postman
2. Click "Import"
3. Select `openapi.yaml`
4. All endpoints will be imported as a collection

### Insomnia
1. Open Insomnia
2. Click "Create" → "Import From" → "File"
3. Select `openapi.yaml`
4. Collection will be imported

### REST Client (VS Code Extension)
Create a `.http` file with requests:

```http
### Discover USB devices
GET http://localhost:5000/devices/usb

### Connect to USB device
POST http://localhost:5000/connect
Content-Type: application/json

{
  "connection_type": "USB",
  "serial": "ABC123DEF456"
}

### Get device state
POST http://localhost:5000/state

### Execute shell command
POST http://localhost:5000/shell
Content-Type: application/json

{
  "command": "input tap 500 500"
}
```

## Validation

Validate the OpenAPI specification:

```bash
# Using Swagger CLI
npm install -g @apidevtools/swagger-cli
swagger-cli validate openapi.yaml

# Using OpenAPI Generator
openapi-generator-cli validate -i openapi.yaml

# Online validator
# Visit: https://editor.swagger.io/
# Paste the openapi.yaml content
```

## Updating Documentation

When you update the API:

1. Update `openapi.yaml` with new endpoints/schemas
2. Validate the spec
3. Update `API.md` with new examples
4. The HTML docs will automatically reflect changes

## Additional Resources

- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [ReDoc Documentation](https://redocly.com/docs/redoc/)
- [OpenAPI Generator](https://openapi-generator.tech/)
