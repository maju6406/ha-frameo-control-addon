# Frameo ADB Control API Documentation

## Overview

The Frameo ADB Control API provides a RESTful interface for controlling Frameo digital photo frames via ADB (Android Debug Bridge). This API enables programmatic control over USB and network connections.

**Base URL**: `http://localhost:5000`

## Table of Contents

- [Authentication](#authentication)
- [Connection Flow](#connection-flow)
- [Endpoints](#endpoints)
  - [Discovery](#discovery)
  - [Connection](#connection)
  - [State](#state)
  - [Control](#control)
  - [File Transfer](#file-transfer)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Authentication

ADB authentication is handled automatically using RSA keys stored in `/data/adbkey`. Keys are generated automatically on first run.

**First Connection**: When connecting to a new device for the first time, you must accept the "Allow USB Debugging" prompt on the Frameo device screen. The device will remember this authorization for future connections.

## Connection Flow

1. **Discover USB Devices** (optional for USB connections)
   ```bash
   GET /devices/usb
   ```

2. **Connect to Device**
   ```bash
   POST /connect
   ```

3. **Control Device**
   - Use `/state` to read device information
   - Use `/shell` to execute commands
   - Use `/tcpip` to enable wireless debugging

## Endpoints

### Discovery

#### `GET /devices/usb`

Scans for and returns all connected USB ADB devices.

**Response**: `200 OK`
```json
["ABC123DEF456", "XYZ789GHI012"]
```

**Response**: `200 OK` (No devices)
```json
[]
```

**Response**: `500 Internal Server Error`
```json
{
  "error": "Error finding USB devices: ..."
}
```

**Example**:
```bash
curl http://localhost:5000/devices/usb
```

---

### Connection

#### `POST /connect`

Establishes a persistent connection to a Frameo device. Only one device can be connected at a time.

**Connection Types**:
- **USB**: Connect via USB cable (requires serial number)
- **Network**: Connect via Wi-Fi/Ethernet (requires IP address)

**Request Body** (USB):
```json
{
  "connection_type": "USB",
  "serial": "ABC123DEF456"
}
```

**Request Body** (Network):
```json
{
  "connection_type": "NETWORK",
  "host": "192.168.1.100",
  "port": 5555
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `connection_type` | string | Yes | "USB" or "NETWORK" |
| `serial` | string | For USB | Device serial number from `/devices/usb` |
| `host` | string | For Network | IP address or hostname |
| `port` | integer | No | ADB port (default: 5555) |

**Response**: `200 OK`
```json
{
  "status": "connected"
}
```

**Response**: `400 Bad Request`
```json
{
  "error": "USB connection requires a serial number."
}
```

**Response**: `500 Internal Server Error`
```json
{
  "error": "Connection failed: Device not found"
}
```

**Examples**:
```bash
# USB connection
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{
    "connection_type": "USB",
    "serial": "ABC123DEF456"
  }'

# Network connection
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{
    "connection_type": "NETWORK",
    "host": "192.168.1.100"
  }'
```

---

#### `POST /tcpip`

Enables wireless ADB debugging on the connected device. Requires an active USB connection.

**Prerequisites**:
- Device must be connected via USB
- Device and API server must be on the same network

**Workflow**:
1. Connect device via USB using `/connect`
2. Call `/tcpip` to enable wireless debugging
3. Note the device's IP address
4. Disconnect USB cable
5. Connect wirelessly using `/connect` with the IP address

**Response**: `200 OK`
```json
{
  "result": "TCP/IP enabled on port 5555"
}
```

**Response**: `400 Bad Request`
```json
{
  "error": "A USB connection is required for this action."
}
```

**Response**: `500 Internal Server Error`
```json
{
  "error": "ADB Error on tcpip command: ..."
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/tcpip
```

---

### State

#### `POST /state`

Retrieves the current power state and brightness level of the connected device.

**Response**: `200 OK`
```json
{
  "is_on": true,
  "brightness": 128
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `is_on` | boolean | Device power state (true = awake, false = asleep) |
| `brightness` | integer | Screen brightness level (0-255) |

**Response**: `503 Service Unavailable`
```json
{
  "error": "Device is not connected or available."
}
```

**Response**: `500 Internal Server Error`
```json
{
  "error": "Shell command failed: ..."
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/state
```

---

### Control

#### `POST /shell`

Executes an arbitrary ADB shell command on the connected device.

**Request Body**:
```json
{
  "command": "input tap 500 500"
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | ADB shell command to execute |

**Common Commands**:

| Command | Description | Example |
|---------|-------------|---------|
| `input tap X Y` | Tap screen at coordinates | `input tap 500 500` |
| `input swipe X1 Y1 X2 Y2 [ms]` | Swipe gesture | `input swipe 100 500 900 500 300` |
| `input text "string"` | Input text | `input text Hello` |
| `input keyevent CODE` | Send key event | `input keyevent KEYCODE_HOME` |
| `am start -n package/activity` | Launch app | `am start -n com.frameo.app/.MainActivity` |
| `pm list packages` | List packages | `pm list packages` |
| `dumpsys battery` | Battery info | `dumpsys battery` |
| `dumpsys power` | Power state | `dumpsys power` |
| `wm size` | Screen size | `wm size` |
| `wm density` | Screen density | `wm density` |

**Key Codes** (partial list):
- `KEYCODE_HOME` - Home button
- `KEYCODE_BACK` - Back button
- `KEYCODE_POWER` - Power button
- `KEYCODE_VOLUME_UP` - Volume up
- `KEYCODE_VOLUME_DOWN` - Volume down
- `KEYCODE_MENU` - Menu button

**Response**: `200 OK`
```json
{
  "result": "Physical size: 1920x1080\n"
}
```

**Response**: `400 Bad Request`
```json
{
  "error": "Command not provided"
}
```

**Response**: `503 Service Unavailable`
```json
{
  "error": "Device is not connected or available."
}
```

**Response**: `500 Internal Server Error`
```json
{
  "error": "Shell command failed: ..."
}
```

**Examples**:
```bash
# Tap the screen
curl -X POST http://localhost:5000/shell \
  -H "Content-Type: application/json" \
  -d '{"command": "input tap 500 500"}'

# Swipe gesture
curl -X POST http://localhost:5000/shell \
  -H "Content-Type: application/json" \
  -d '{"command": "input swipe 100 500 900 500 300"}'

# Get screen resolution
curl -X POST http://localhost:5000/shell \
  -H "Content-Type: application/json" \
  -d '{"command": "wm size"}'

# Press home button
curl -X POST http://localhost:5000/shell \
  -H "Content-Type: application/json" \
  -d '{"command": "input keyevent KEYCODE_HOME"}'
```

---

### File Transfer

#### `POST /upload`

Upload a photo or file to the Frameo device.

**Request**: `multipart/form-data`

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | The file to upload |
| `destination` | string | No | Destination directory (default: `/sdcard/Frameo`) |

**Response**: `200 OK`
```json
{
  "status": "success",
  "message": "File uploaded to /sdcard/Frameo/photo.jpg",
  "path": "/sdcard/Frameo/photo.jpg"
}
```

**Response**: `400 Bad Request`
```json
{
  "error": "No file provided"
}
```

**Response**: `503 Service Unavailable`
```json
{
  "error": "Device is not connected or available."
}
```

**Examples**:
```bash
# Upload a photo
curl -X POST http://localhost:5000/upload \
  -F "file=@/path/to/photo.jpg"

# Upload to custom directory
curl -X POST http://localhost:5000/upload \
  -F "file=@/path/to/photo.jpg" \
  -F "destination=/sdcard/Pictures"

# Upload multiple photos (bash script)
for photo in *.jpg; do
  curl -X POST http://localhost:5000/upload -F "file=@$photo"
done
```

**Python Example**:
```python
import requests

# Upload single photo
with open('photo.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/upload', files=files)
    print(response.json())

# Upload with custom destination
with open('photo.jpg', 'rb') as f:
    files = {'file': f}
    data = {'destination': '/sdcard/DCIM'}
    response = requests.post('http://localhost:5000/upload', files=files, data=data)
```

---

#### `POST /download`

Download a file from the Frameo device.

**Request Body**:
```json
{
  "path": "/sdcard/screenshot.png"
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Full path to file on device |

**Response**: `200 OK`
- Binary file content with appropriate Content-Disposition header

**Response**: `400 Bad Request`
```json
{
  "error": "No path provided"
}
```

**Examples**:
```bash
# Download a file
curl -X POST http://localhost:5000/download \
  -H "Content-Type: application/json" \
  -d '{"path": "/sdcard/screenshot.png"}' \
  -o screenshot.png

# Download photo from Frameo directory
curl -X POST http://localhost:5000/download \
  -H "Content-Type: application/json" \
  -d '{"path": "/sdcard/Frameo/photo.jpg"}' \
  -o downloaded_photo.jpg
```

**Python Example**:
```python
import requests

# Download a file
response = requests.post(
    'http://localhost:5000/download',
    json={'path': '/sdcard/screenshot.png'}
)

if response.status_code == 200:
    with open('screenshot.png', 'wb') as f:
        f.write(response.content)
    print("File downloaded successfully")
```

---

## Error Handling

All endpoints return JSON responses. Common error codes:

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `400` | Bad Request - Missing or invalid parameters |
| `500` | Internal Server Error - ADB connection failed, device error |
| `503` | Service Unavailable - No device connected |

**Error Response Format**:
```json
{
  "error": "Descriptive error message"
}
```

**Common Errors**:

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Device is not connected or available." | No active connection | Call `/connect` first |
| "USB connection requires a serial number." | Missing serial in request | Provide serial from `/devices/usb` |
| "Network connection requires a host." | Missing host in request | Provide IP address |
| "Connection failed: Device not found" | Device not accessible | Check USB connection or IP address |
| "Command not provided" | Missing command in `/shell` | Include command in request body |
| "A USB connection is required for this action." | Trying `/tcpip` without USB | Connect via USB first |

---

## Examples

### Complete Workflow: USB to Wireless

```bash
# 1. Discover USB devices
curl http://localhost:5000/devices/usb
# Response: ["ABC123DEF456"]

# 2. Connect via USB
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{"connection_type": "USB", "serial": "ABC123DEF456"}'
# Response: {"status": "connected"}

# 3. Check device state
curl -X POST http://localhost:5000/state
# Response: {"is_on": true, "brightness": 128}

# 4. Enable wireless debugging
curl -X POST http://localhost:5000/tcpip
# Response: {"result": "TCP/IP enabled on port 5555"}

# 5. Find device IP (on your network, or check device settings)
# Let's say it's 192.168.1.100

# 6. Disconnect USB cable and connect wirelessly
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{"connection_type": "NETWORK", "host": "192.168.1.100"}'
# Response: {"status": "connected"}

# 7. Control device wirelessly
curl -X POST http://localhost:5000/shell \
  -H "Content-Type: application/json" \
  -d '{"command": "input tap 500 500"}'
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:5000"

class FrameoClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def discover_usb_devices(self):
        """Get list of USB connected devices."""
        response = requests.get(f"{self.base_url}/devices/usb")
        response.raise_for_status()
        return response.json()
    
    def connect_usb(self, serial):
        """Connect to device via USB."""
        response = requests.post(
            f"{self.base_url}/connect",
            json={"connection_type": "USB", "serial": serial}
        )
        response.raise_for_status()
        return response.json()
    
    def connect_network(self, host, port=5555):
        """Connect to device via network."""
        response = requests.post(
            f"{self.base_url}/connect",
            json={"connection_type": "NETWORK", "host": host, "port": port}
        )
        response.raise_for_status()
        return response.json()
    
    def get_state(self):
        """Get device state."""
        response = requests.post(f"{self.base_url}/state")
        response.raise_for_status()
        return response.json()
    
    def shell(self, command):
        """Execute shell command."""
        response = requests.post(
            f"{self.base_url}/shell",
            json={"command": command}
        )
        response.raise_for_status()
        return response.json()
    
    def enable_wireless(self):
        """Enable wireless ADB."""
        response = requests.post(f"{self.base_url}/tcpip")
        response.raise_for_status()
        return response.json()
    
    def tap(self, x, y):
        """Tap screen at coordinates."""
        return self.shell(f"input tap {x} {y}")
    
    def swipe(self, x1, y1, x2, y2, duration=300):
        """Swipe gesture."""
        return self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
    
    def press_key(self, keycode):
        """Press a key."""
        return self.shell(f"input keyevent {keycode}")
    
    def home(self):
        """Press home button."""
        return self.press_key("KEYCODE_HOME")
    
    def back(self):
        """Press back button."""
        return self.press_key("KEYCODE_BACK")

# Usage
client = FrameoClient()

# Discover and connect
devices = client.discover_usb_devices()
if devices:
    client.connect_usb(devices[0])
    
    # Get state
    state = client.get_state()
    print(f"Device is {'on' if state['is_on'] else 'off'}")
    print(f"Brightness: {state['brightness']}")
    
    # Control device
    client.tap(500, 500)
    client.swipe(100, 500, 900, 500)
    client.home()
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

class FrameoClient {
  constructor(baseUrl = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async discoverUsbDevices() {
    const response = await axios.get(`${this.baseUrl}/devices/usb`);
    return response.data;
  }

  async connectUsb(serial) {
    const response = await axios.post(`${this.baseUrl}/connect`, {
      connection_type: 'USB',
      serial: serial
    });
    return response.data;
  }

  async connectNetwork(host, port = 5555) {
    const response = await axios.post(`${this.baseUrl}/connect`, {
      connection_type: 'NETWORK',
      host: host,
      port: port
    });
    return response.data;
  }

  async getState() {
    const response = await axios.post(`${this.baseUrl}/state`);
    return response.data;
  }

  async shell(command) {
    const response = await axios.post(`${this.baseUrl}/shell`, {
      command: command
    });
    return response.data;
  }

  async enableWireless() {
    const response = await axios.post(`${this.baseUrl}/tcpip`);
    return response.data;
  }

  async tap(x, y) {
    return this.shell(`input tap ${x} ${y}`);
  }

  async swipe(x1, y1, x2, y2, duration = 300) {
    return this.shell(`input swipe ${x1} ${y1} ${x2} ${y2} ${duration}`);
  }

  async pressKey(keycode) {
    return this.shell(`input keyevent ${keycode}`);
  }

  async home() {
    return this.pressKey('KEYCODE_HOME');
  }

  async back() {
    return this.pressKey('KEYCODE_BACK');
  }
}

// Usage
(async () => {
  const client = new FrameoClient();
  
  // Discover and connect
  const devices = await client.discoverUsbDevices();
  if (devices.length > 0) {
    await client.connectUsb(devices[0]);
    
    // Get state
    const state = await client.getState();
    console.log(`Device is ${state.is_on ? 'on' : 'off'}`);
    console.log(`Brightness: ${state.brightness}`);
    
    // Control device
    await client.tap(500, 500);
    await client.swipe(100, 500, 900, 500);
    await client.home();
  }
})();
```

---

## Additional Resources

- **OpenAPI Specification**: See `openapi.yaml` for the complete API specification
- **GitHub Repository**: [ha-frameo-control-addon](https://github.com/HunorLaczko/ha-frameo-control-addon)
- **ADB Documentation**: [Android Debug Bridge](https://developer.android.com/studio/command-line/adb)
