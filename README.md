# Frameo Control API

A standalone REST API server and CLI tool for controlling Frameo digital photo frames via ADB (Android Debug Bridge). This project provides both a simple HTTP interface and a powerful command-line tool for communicating with Frameo devices over USB or network connections.

## Key Features

* **USB & Network Support:** Connect to Frameo devices via USB or wireless ADB
* **Wireless Operation:** After one-time USB setup, control entirely over WiFi
* **RESTful API:** Simple JSON-based API for device control
* **Stateful Connection:** Maintains active connection for responsive control
* **Photo Upload:** Upload photos directly to your Frameo
* **Docker Ready:** Containerized deployment with USB device access
* **ADB Authentication:** Automatic key generation and management
* **CLI Tool:** Powerful command-line interface for easy automation

## 📡 WiFi Support

**Yes, everything works over WiFi!** After a one-time USB setup to enable wireless ADB, you can:
- Control your frame from anywhere on your network
- Upload photos wirelessly
- Automate with home automation systems
- No USB cable needed for daily use

```bash
# One-time USB setup
frameo-cli connect usb ABC123
frameo-cli tcpip

# Then use WiFi forever
frameo-cli connect network 192.168.1.100
frameo-cli upload photo.jpg
```

**[Complete WiFi Setup Guide →](WIFI.md)**

## Quick Start

### Using Docker

```bash
# Build the image
docker build -t frameo-control-api .

# Run with USB access
docker run -d \
  --name frameo-control-api \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  -v $(pwd)/data:/data \
  -p 5000:5000 \
  frameo-adb-api
```

### Using Docker Compose

```bash
docker-compose up -d
```

### Serving Documentation

To serve the interactive API documentation:

```bash
# Option 1: Using the provided script
./serve-docs.sh

# Option 2: Using Docker Compose (includes nginx)
docker-compose --profile docs up -d

# Option 3: Using Python directly
python3 -m http.server 8080
```

Then access:
- API: http://localhost:5000
- Swagger UI: http://localhost:8080/docs/
- ReDoc: http://localhost:8080/docs/redoc.html

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The API will be available at `http://localhost:5000`

## 🖥️ Command-Line Interface

A powerful CLI tool is available for easy interaction with the API:

```bash
# Install the CLI
./install-cli.sh

# Quick examples
frameo-cli devices                    # List USB devices
frameo-cli connect usb ABC123         # Connect to device
frameo-cli wake                       # Wake the frame
frameo-cli next                       # Next photo
frameo-cli brightness 150             # Set brightness
frameo-cli shell "input tap 500 500"  # Custom command
frameo-cli upload photo.jpg           # Upload photo to frame
```

**[View CLI Documentation →](CLI.md)**

## 📖 API Documentation

Multiple documentation formats are available:

### Interactive Documentation
- **[Swagger UI](docs/index.html)** - Interactive API explorer with "Try it out" functionality
- **[ReDoc](docs/redoc.html)** - Beautiful three-panel documentation

To view the interactive docs locally:
```bash
# Serve with Python
python3 -m http.server 8080
# Then visit: http://localhost:8080/docs/

# Or with Node.js
npx http-server -p 8080
```

### Reference Documentation
- **[API.md](API.md)** - Complete API reference with Python/JavaScript examples
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world use cases and practical examples
- **[CLI.md](CLI.md)** - Command-line interface documentation
- **[WIFI.md](WIFI.md)** - Complete WiFi setup and troubleshooting guide
- **[openapi.yaml](openapi.yaml)** - OpenAPI 3.0 specification for tooling

### Additional Tools
- Import `openapi.yaml` into [Postman](https://www.postman.com/) or [Insomnia](https://insomnia.rest/)
- Generate client SDKs using [OpenAPI Generator](https://openapi-generator.tech/)
- Validate and edit in [Swagger Editor](https://editor.swagger.io/)

## API Endpoints

### Device Discovery

**GET /devices/usb**
- Scan for connected USB ADB devices
- Returns: Array of device serial numbers

```bash
curl http://localhost:5000/devices/usb
```

### Connect to Device

**POST /connect**
- Establish connection to a device
- Body: `{"connection_type": "USB", "serial": "device_serial"}`
- Or: `{"connection_type": "NETWORK", "host": "192.168.1.100", "port": 5555}`

```bash
# USB connection
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{"connection_type": "USB", "serial": "ABC123"}'

# Network connection
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{"connection_type": "NETWORK", "host": "192.168.1.100"}'
```

### Get Device State

**POST /state**
- Get device power state and brightness
- Returns: `{"is_on": true, "brightness": 128}`

```bash
curl -X POST http://localhost:5000/state
```

### Execute Shell Command

**POST /shell**
- Execute arbitrary ADB shell command
- Body: `{"command": "input tap 500 500"}`

```bash
curl -X POST http://localhost:5000/shell \
  -H "Content-Type: application/json" \
  -d '{"command": "input tap 500 500"}'
```

### File Upload

**POST /upload**
- Upload photos to your Frameo device
- Multipart form data with file field

```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@photo.jpg"
```

### Enable Wireless ADB

**POST /tcpip**
- Enable wireless debugging (requires USB connection)
- Returns: Port number for wireless connection

```bash
curl -X POST http://localhost:5000/tcpip
```

## Configuration

### USB Access

For USB connections, the container needs:
- `--privileged` flag or specific device permissions
- `/dev/bus/usb` volume mount

### ADB Keys

ADB authentication keys are automatically generated and stored in `/data/adbkey`. On first connection, you'll need to accept the authorization prompt on your Frameo device.

### Environment Variables

- `PORT`: API server port (default: 5000)

## Development

### Project Structure

```
.
├── app.py              # Main API server
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container definition
├── docker-compose.yml # Docker Compose config
└── data/              # ADB keys storage
```

### Requirements

- Python 3.11+
- libusb (for USB connections)
- adb-shell library
- Quart web framework

## Troubleshooting

### USB Device Not Found
- Ensure USB debugging is enabled on the Frameo device
- Check that the container has proper USB access permissions
- Verify device is connected: `lsusb`

### Authorization Timeout
- Accept the "Allow USB Debugging" prompt on the device screen
- Check that ADB keys are properly stored in `/data`

### Connection Drops
- Check USB cable quality
- Verify network connectivity for wireless ADB
- Review logs for specific error messages

## Integration

This API can be integrated with:
- Home automation systems (Home Assistant, OpenHAB, Node-RED, etc.)
- Custom scripts and applications
- Web interfaces
- Mobile apps

## License

See [LICENSE](LICENSE) file for details.