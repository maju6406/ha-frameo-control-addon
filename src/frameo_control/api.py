import os
import asyncio
import logging
import re
from functools import partial
from quart import Quart, jsonify, request
import usb1

from adb_shell.adb_device import AdbDeviceUsb
from adb_shell.adb_device_async import AdbDeviceTcpAsync
from adb_shell.transport.usb_transport import UsbTransport
from adb_shell.exceptions import AdbConnectionError, AdbTimeoutError, UsbDeviceNotFoundError
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_LOGGER = logging.getLogger(__name__)

# --- Global State ---
signer = None
adb_client = None
is_usb = False

# --- Helper Functions ---
def _load_or_generate_keys():
    """Load ADB keys from /data/adbkey, or generate them if they don't exist."""
    adb_key_path = "/data/adbkey"
    if not os.path.exists(adb_key_path):
        _LOGGER.info("No ADB key found, generating a new one at %s", adb_key_path)
        os.makedirs("/data", exist_ok=True)
        keygen(adb_key_path)
    _LOGGER.info("Loading ADB key from %s", adb_key_path)
    with open(adb_key_path) as f:
        priv = f.read()
    with open(adb_key_path + ".pub") as f:
        pub = f.read()
    return PythonRSASigner(pub, priv)

async def _run_sync(func, *args, **kwargs):
    """Run a synchronous (blocking) function in an executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))

def _auth_callback_sync(device_client):
    """Log a message when auth is needed. This is only for sync (USB) connections."""
    _LOGGER.info("!!!!!! ACTION REQUIRED !!!!!! Please check your device's screen to 'Allow USB Debugging'.")

# --- Quart Web Application ---
app = Quart(__name__)

@app.before_serving
async def startup():
    """Load ADB keys on startup."""
    global signer
    signer = _load_or_generate_keys()
    _LOGGER.info("Frameo Control API started. Ready to accept connections.")

@app.route("/", methods=["GET"])
async def root():
    """Root endpoint with API information."""
    return jsonify({
        "service": "Frameo Control API",
        "version": "0.1.0",
        "endpoints": {
            "devices": "/devices/usb",
            "connect": "/connect",
            "state": "/state",
            "shell": "/shell",
            "tcpip": "/tcpip",
            "wake": "/wake",
            "sleep": "/sleep",
            "brightness": "/brightness",
            "tap": "/tap",
            "swipe": "/swipe",
            "keyevent": "/keyevent",
            "app": "/app",
            "screenshot": "/screenshot",
            "upload": "/upload",
            "download": "/download"
        }
    })

@app.route("/devices/usb", methods=["GET"])
async def list_usb_devices():
    """
    List all USB-connected devices matching Frameo vendor IDs.
    """
    _LOGGER.info("Request received for /devices/usb")
    try:
        devices = await _run_sync(_find_usb_devices)
        _LOGGER.info("Found %d USB device(s)", len(devices))
        return jsonify({"devices": devices})
    except Exception as e:
        _LOGGER.error("Error listing USB devices: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

def _find_usb_devices():
    """Find all connected USB devices matching known Frameo vendor IDs."""
    VENDOR_IDS = [0x2207, 0x18d1]
    context = usb1.USBContext()
    devices_found = []
    for device in context.getDeviceList(skip_on_error=True):
        vendor_id = device.getVendorID()
        if vendor_id in VENDOR_IDS:
            try:
                serial = device.getSerialNumber()
                devices_found.append({
                    "serial": serial,
                    "vendor_id": hex(vendor_id),
                    "product_id": hex(device.getProductID())
                })
            except Exception as e:
                _LOGGER.warning("Could not read serial for device %s: %s", hex(vendor_id), e)
    return devices_found

@app.route("/connect", methods=["POST"])
async def connect():
    """
    Connect to a device via USB or network.
    
    Body (JSON):
        {
            "type": "usb" | "network",
            "serial": "ABC123" (for usb),
            "host": "192.168.1.100" (for network),
            "port": 5555 (for network, optional)
        }
    """
    global adb_client, is_usb
    _LOGGER.info("Request received for /connect")
    
    try:
        data = await request.get_json()
        conn_type = data.get("type")
        
        # Close existing connection if any
        if adb_client:
            _LOGGER.info("Closing existing connection")
            try:
                if is_usb:
                    await _run_sync(adb_client.close)
                else:
                    await adb_client.close()
            except Exception as e:
                _LOGGER.warning("Error closing previous connection: %s", e)
            adb_client = None
        
        if conn_type == "usb":
            serial = data.get("serial")
            if not serial:
                return jsonify({"error": "Missing 'serial' for USB connection"}), 400
            
            _LOGGER.info("Connecting to USB device with serial: %s", serial)
            device = await _run_sync(_find_usb_device_by_serial, serial)
            if not device:
                return jsonify({"error": f"Device with serial '{serial}' not found"}), 404
            
            adb_client = AdbDeviceUsb(device, auth_callback=_auth_callback_sync)
            await _run_sync(adb_client.connect, rsa_keys=[signer], auth_timeout_s=60)
            is_usb = True
            _LOGGER.info("Successfully connected to USB device: %s", serial)
            return jsonify({"status": "connected", "type": "usb", "serial": serial})
        
        elif conn_type == "network":
            host = data.get("host")
            port = data.get("port", 5555)
            if not host:
                return jsonify({"error": "Missing 'host' for network connection"}), 400
            
            _LOGGER.info("Connecting to network device at %s:%d", host, port)
            adb_client = AdbDeviceTcpAsync(host, port, default_transport_timeout_s=9.0)
            await adb_client.connect(rsa_keys=[signer], auth_timeout_s=60)
            is_usb = False
            _LOGGER.info("Successfully connected to network device: %s:%d", host, port)
            return jsonify({"status": "connected", "type": "network", "host": host, "port": port})
        
        else:
            return jsonify({"error": "Invalid connection type. Use 'usb' or 'network'"}), 400
    
    except (AdbConnectionError, AdbTimeoutError) as e:
        _LOGGER.error("ADB connection failed: %s", e, exc_info=True)
        return jsonify({"error": f"ADB connection failed: {e}"}), 500
    except Exception as e:
        _LOGGER.error("Unexpected error during connection: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

def _find_usb_device_by_serial(serial: str):
    """Find a USB device by serial number."""
    VENDOR_IDS = [0x2207, 0x18d1]
    context = usb1.USBContext()
    for device in context.getDeviceList(skip_on_error=True):
        if device.getVendorID() in VENDOR_IDS:
            try:
                if device.getSerialNumber() == serial:
                    return UsbTransport(device)
            except Exception as e:
                _LOGGER.warning("Error checking device serial: %s", e)
    return None

@app.route("/state", methods=["GET"])
async def get_state():
    """
    Get current device state (screen on/off, brightness, active app).
    """
    _LOGGER.info("Request received for /state")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        # Get screen state
        if is_usb:
            screen_state_raw = await _run_sync(adb_client.shell, "dumpsys power | grep 'Display Power'")
        else:
            screen_state_raw = await adb_client.shell("dumpsys power | grep 'Display Power'")
        
        screen_on = "state=ON" in screen_state_raw or "state=2" in screen_state_raw
        
        # Get brightness
        if is_usb:
            brightness_raw = await _run_sync(adb_client.shell, "settings get system screen_brightness")
        else:
            brightness_raw = await adb_client.shell("settings get system screen_brightness")
        
        try:
            brightness = int(brightness_raw.strip())
        except:
            brightness = None
        
        # Get current app
        if is_usb:
            app_raw = await _run_sync(adb_client.shell, "dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
        else:
            app_raw = await adb_client.shell("dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
        
        app_match = re.search(r'([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+)', app_raw)
        current_app = app_match.group(1) if app_match else None
        
        return jsonify({
            "screen_on": screen_on,
            "brightness": brightness,
            "current_app": current_app
        })
    
    except Exception as e:
        _LOGGER.error("Error getting device state: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/shell", methods=["POST"])
async def shell():
    """
    Execute a shell command on the device.
    
    Body (JSON):
        {
            "command": "ls -la /sdcard"
        }
    """
    _LOGGER.info("Request received for /shell")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        command = data.get("command")
        if not command:
            return jsonify({"error": "Missing 'command'"}), 400
        
        _LOGGER.info("Executing shell command: %s", command)
        if is_usb:
            output = await _run_sync(adb_client.shell, command)
        else:
            output = await adb_client.shell(command)
        
        return jsonify({"output": output})
    
    except Exception as e:
        _LOGGER.error("Error executing shell command: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/tcpip", methods=["POST"])
async def enable_tcpip():
    """
    Enable ADB over TCP/IP on port 5555.
    Requires USB connection to be active.
    """
    _LOGGER.info("Request received for /tcpip")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        _LOGGER.info("Enabling ADB over TCP/IP on port 5555")
        if is_usb:
            result = await _run_sync(adb_client.shell, "setprop service.adb.tcp.port 5555 && stop adbd && start adbd")
        else:
            result = await adb_client.shell("setprop service.adb.tcp.port 5555 && stop adbd && start adbd")
        
        _LOGGER.info("TCP/IP mode enabled. You can now connect via network.")
        return jsonify({"status": "tcpip_enabled", "port": 5555, "output": result})
    
    except Exception as e:
        _LOGGER.error("Error enabling TCP/IP: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/wake", methods=["POST"])
async def wake():
    """Wake the screen (turn it on)."""
    _LOGGER.info("Request received for /wake")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        if is_usb:
            await _run_sync(adb_client.shell, "input keyevent KEYCODE_WAKEUP")
        else:
            await adb_client.shell("input keyevent KEYCODE_WAKEUP")
        return jsonify({"status": "screen_woken"})
    except Exception as e:
        _LOGGER.error("Error waking screen: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/sleep", methods=["POST"])
async def sleep():
    """Put the screen to sleep (turn it off)."""
    _LOGGER.info("Request received for /sleep")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        if is_usb:
            await _run_sync(adb_client.shell, "input keyevent KEYCODE_SLEEP")
        else:
            await adb_client.shell("input keyevent KEYCODE_SLEEP")
        return jsonify({"status": "screen_sleeping"})
    except Exception as e:
        _LOGGER.error("Error putting screen to sleep: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/brightness", methods=["POST"])
async def set_brightness():
    """
    Set screen brightness (0-255).
    
    Body (JSON):
        {
            "level": 150
        }
    """
    _LOGGER.info("Request received for /brightness")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        level = data.get("level")
        if level is None:
            return jsonify({"error": "Missing 'level'"}), 400
        
        level = int(level)
        if not 0 <= level <= 255:
            return jsonify({"error": "Brightness level must be between 0 and 255"}), 400
        
        _LOGGER.info("Setting brightness to %d", level)
        if is_usb:
            await _run_sync(adb_client.shell, f"settings put system screen_brightness {level}")
        else:
            await adb_client.shell(f"settings put system screen_brightness {level}")
        
        return jsonify({"status": "brightness_set", "level": level})
    
    except Exception as e:
        _LOGGER.error("Error setting brightness: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/tap", methods=["POST"])
async def tap():
    """
    Tap at coordinates (x, y).
    
    Body (JSON):
        {
            "x": 500,
            "y": 300
        }
    """
    _LOGGER.info("Request received for /tap")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        x = data.get("x")
        y = data.get("y")
        if x is None or y is None:
            return jsonify({"error": "Missing 'x' or 'y'"}), 400
        
        _LOGGER.info("Tapping at coordinates (%d, %d)", x, y)
        if is_usb:
            await _run_sync(adb_client.shell, f"input tap {x} {y}")
        else:
            await adb_client.shell(f"input tap {x} {y}")
        
        return jsonify({"status": "tap_sent", "x": x, "y": y})
    
    except Exception as e:
        _LOGGER.error("Error sending tap: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/swipe", methods=["POST"])
async def swipe():
    """
    Swipe from (x1, y1) to (x2, y2) with optional duration.
    
    Body (JSON):
        {
            "x1": 100,
            "y1": 500,
            "x2": 900,
            "y2": 500,
            "duration": 300
        }
    """
    _LOGGER.info("Request received for /swipe")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        x1 = data.get("x1")
        y1 = data.get("y1")
        x2 = data.get("x2")
        y2 = data.get("y2")
        duration = data.get("duration", 300)
        
        if None in (x1, y1, x2, y2):
            return jsonify({"error": "Missing coordinates (x1, y1, x2, y2)"}), 400
        
        _LOGGER.info("Swiping from (%d, %d) to (%d, %d) over %dms", x1, y1, x2, y2, duration)
        if is_usb:
            await _run_sync(adb_client.shell, f"input swipe {x1} {y1} {x2} {y2} {duration}")
        else:
            await adb_client.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        
        return jsonify({"status": "swipe_sent", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "duration": duration})
    
    except Exception as e:
        _LOGGER.error("Error sending swipe: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/keyevent", methods=["POST"])
async def keyevent():
    """
    Send a key event (e.g., HOME, BACK, etc.).
    
    Body (JSON):
        {
            "key": "KEYCODE_HOME"
        }
    """
    _LOGGER.info("Request received for /keyevent")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        key = data.get("key")
        if not key:
            return jsonify({"error": "Missing 'key'"}), 400
        
        _LOGGER.info("Sending key event: %s", key)
        if is_usb:
            await _run_sync(adb_client.shell, f"input keyevent {key}")
        else:
            await adb_client.shell(f"input keyevent {key}")
        
        return jsonify({"status": "keyevent_sent", "key": key})
    
    except Exception as e:
        _LOGGER.error("Error sending key event: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/app", methods=["POST"])
async def app_control():
    """
    Control the Frameo app (open, restart, force-stop).
    
    Body (JSON):
        {
            "action": "open" | "restart" | "force-stop"
        }
    """
    _LOGGER.info("Request received for /app")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        action = data.get("action")
        package = "com.frameo.app"
        
        if action == "open":
            _LOGGER.info("Opening Frameo app")
            if is_usb:
                await _run_sync(adb_client.shell, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            else:
                await adb_client.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            return jsonify({"status": "app_opened", "package": package})
        
        elif action == "restart":
            _LOGGER.info("Restarting Frameo app")
            if is_usb:
                await _run_sync(adb_client.shell, f"am force-stop {package}")
                await asyncio.sleep(1)
                await _run_sync(adb_client.shell, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            else:
                await adb_client.shell(f"am force-stop {package}")
                await asyncio.sleep(1)
                await adb_client.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            return jsonify({"status": "app_restarted", "package": package})
        
        elif action == "force-stop":
            _LOGGER.info("Force stopping Frameo app")
            if is_usb:
                await _run_sync(adb_client.shell, f"am force-stop {package}")
            else:
                await adb_client.shell(f"am force-stop {package}")
            return jsonify({"status": "app_stopped", "package": package})
        
        else:
            return jsonify({"error": "Invalid action. Use 'open', 'restart', or 'force-stop'"}), 400
    
    except Exception as e:
        _LOGGER.error("Error controlling app: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/screenshot", methods=["GET"])
async def screenshot():
    """
    Take a screenshot and return it as PNG data.
    """
    _LOGGER.info("Request received for /screenshot")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        _LOGGER.info("Taking screenshot")
        if is_usb:
            result = await _run_sync(adb_client.shell, "screencap -p", decode=False)
        else:
            result = await adb_client.shell("screencap -p", decode=False)
        
        # The result should be raw PNG bytes
        return result, 200, {"Content-Type": "image/png"}
    
    except Exception as e:
        _LOGGER.error("Error taking screenshot: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
async def upload():
    """
    Upload a file to the device.
    
    Form data:
        - file: The file to upload
        - destination: Target directory on device (default: /sdcard/Frameo)
    """
    _LOGGER.info("Request received for /upload")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        files = await request.files
        file_data = files.get("file")
        if not file_data:
            return jsonify({"error": "No file provided"}), 400
        
        form = await request.form
        destination = form.get("destination", "/sdcard/Frameo")
        filename = file_data.filename
        
        _LOGGER.info("Uploading file '%s' to %s", filename, destination)
        
        # Read file content
        content = file_data.read()
        
        # Push to device
        remote_path = f"{destination}/{filename}"
        if is_usb:
            await _run_sync(adb_client.push, content, remote_path)
        else:
            await adb_client.push(content, remote_path)
        
        _LOGGER.info("File uploaded successfully: %s", remote_path)
        return jsonify({"status": "uploaded", "remote_path": remote_path})
    
    except Exception as e:
        _LOGGER.error("Error uploading file: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
async def download():
    """
    Download a file from the device.
    
    Body (JSON):
        {
            "remote_path": "/sdcard/Frameo/photo.jpg"
        }
    """
    _LOGGER.info("Request received for /download")
    if not adb_client:
        return jsonify({"error": "No device connected"}), 503
    
    try:
        data = await request.get_json()
        remote_path = data.get("remote_path")
        if not remote_path:
            return jsonify({"error": "Missing 'remote_path'"}), 400
        
        _LOGGER.info("Downloading file from: %s", remote_path)
        if is_usb:
            content = await _run_sync(adb_client.pull, remote_path)
        else:
            content = await adb_client.pull(remote_path)
        
        # Determine content type from file extension
        content_type = "application/octet-stream"
        if remote_path.lower().endswith(('.jpg', '.jpeg')):
            content_type = "image/jpeg"
        elif remote_path.lower().endswith('.png'):
            content_type = "image/png"
        
        return content, 200, {"Content-Type": content_type}
    
    except Exception as e:
        _LOGGER.error("Error downloading file: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

def main():
    """Main entry point for running the API server."""
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    _LOGGER.info("Starting Frameo Control API on %s:%d", host, port)
    app.run(host=host, port=port)

if __name__ == "__main__":
    main()
