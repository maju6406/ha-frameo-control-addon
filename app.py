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
    """Initialize the ADB signer before starting the server."""
    global signer
    signer = await _run_sync(_load_or_generate_keys)
    _LOGGER.info("Frameo ADB Server Initialized and ready for connection requests.")

# --- API Endpoints ---
@app.route("/devices/usb", methods=["GET"])
async def get_usb_devices():
    """Scan for and return connected USB ADB devices."""
    _LOGGER.info("Request received for /devices/usb")
    try:
        devices = await _run_sync(UsbTransport.find_all_adb_devices)
        serials = [dev.serial_number for dev in devices]
        _LOGGER.info(f"Discovered USB devices: {serials}")
        return jsonify(serials)
    except UsbDeviceNotFoundError:
        _LOGGER.warning("No USB devices found during scan.")
        return jsonify([])
    except Exception as e:
        _LOGGER.error(f"Error finding USB devices: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/connect", methods=["POST"])
async def connect_device():
    """Establishes and holds a connection to the device."""
    global adb_client, is_usb
    conn_details = await request.get_json()
    if not conn_details:
        return jsonify({"error": "Connection details not provided"}), 400

    conn_type = conn_details.get("connection_type", "USB").upper()
    _LOGGER.info(f"Attempting to connect via {conn_type} with details: {conn_details}")

    try:
        if adb_client:
            await (_run_sync(adb_client.close) if is_usb else adb_client.close())
            adb_client = None
            _LOGGER.info("Closed existing connection before reconnecting.")
        
        if conn_type == "USB":
            is_usb = True
            serial = conn_details.get("serial")
            if not serial:
                return jsonify({"error": "USB connection requires a serial number."}), 400
            
            # USB connection is synchronous, so we instantiate the sync class
            adb_client = AdbDeviceUsb(serial=serial, default_transport_timeout_s=9.0)
            await _run_sync(adb_client.connect, rsa_keys=[signer], auth_timeout_s=120.0, auth_callback=_auth_callback_sync)
        
        else: # NETWORK
            is_usb = False
            host = conn_details.get("host")
            port = int(conn_details.get("port", 5555))
            if not host:
                return jsonify({"error": "Network connection requires a host."}), 400
            
            # TCP connection is asynchronous, so we can instantiate and use it directly
            adb_client = AdbDeviceTcpAsync(host=host, port=port, default_transport_timeout_s=9.0)
            await adb_client.connect(rsa_keys=[signer], auth_timeout_s=20.0)

        _LOGGER.info(f"Successfully connected to device: {conn_details.get('serial') or conn_details.get('host')}")
        return jsonify({"status": "connected"}), 200

    except (AdbConnectionError, AdbTimeoutError, UsbDeviceNotFoundError, usb1.USBError, ConnectionResetError) as e:
        _LOGGER.error(f"Failed to connect to device: {e}")
        adb_client = None
        return jsonify({"error": f"Connection failed: {e}"}), 500
    except Exception as e:
        _LOGGER.error(f"An unexpected error occurred during connection: {e}", exc_info=True)
        adb_client = None
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

async def _shell_command(command):
    """Executes a shell command on the existing connection."""
    global adb_client

    if not adb_client or not adb_client.available:
        return {"error": "Device is not connected or available."}, 503
    _LOGGER.info(f"Executing shell command: '{command}'")
    try:
        if is_usb:
            return await _run_sync(adb_client.shell, command), 200
        return await adb_client.shell(command), 200
    except (AdbConnectionError, AdbTimeoutError, ConnectionResetError, usb1.USBError) as e:
        _LOGGER.error(f"Shell command failed: {e}. Connection may be lost.")
        adb_client = None
        return {"error": str(e)}, 500

@app.route("/state", methods=["POST"])
async def get_state():
    _LOGGER.info("Request received for /state")
    response, status_code = await _shell_command("dumpsys power")
    if status_code >= 400: return jsonify(response), status_code
    
    is_on = "mWakefulness=Awake" in response
    brightness = 0
    for line in response.splitlines():
        if "mScreenBrightnessSetting=" in line:
            try: brightness = int(line.split("=")[1]); break
            except (ValueError, IndexError): pass
    return jsonify({"is_on": is_on, "brightness": brightness})

@app.route("/shell", methods=["POST"])
async def run_shell_command():
    data = await request.get_json(); command = data.get("command")
    if not command: return jsonify({"error": "Command not provided"}), 400
    response, status_code = await _shell_command(command)
    return jsonify({"result": response}), status_code

@app.route("/tcpip", methods=["POST"])
async def enable_tcpip():
    """Enables wireless debugging."""
    if not is_usb or not adb_client or not adb_client.available:
        return jsonify({"error": "A USB connection is required for this action."}), 400
    
    _LOGGER.info("Request received for /tcpip")
    try:
        port = 5555
        await _run_sync(
            adb_client._open, 
            destination=f'tcpip:{port}'.encode('utf-8'),
            transport_timeout_s=None,
            read_timeout_s=10.0,
            timeout_s=None
        )
        
        return jsonify({"result": f"TCP/IP enabled on port {port}"}), 200
    except Exception as e:
        _LOGGER.error(f"ADB Error on tcpip command: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
async def upload_file():
    """Upload a file to the device."""
    if not adb_client or not adb_client.available:
        return jsonify({"error": "Device is not connected or available."}), 503
    
    _LOGGER.info("Request received for /upload")
    
    # Get file from request
    files = await request.files
    if 'file' not in files:
        return jsonify({"error": "No file provided"}), 400
    
    file = files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Get destination path (default to Frameo's photo directory)
    form = await request.form
    destination = form.get('destination', '/sdcard/Frameo')
    
    try:
        # Read file content
        file_content = file.read()
        file_name = file.filename
        remote_path = f"{destination}/{file_name}"
        
        _LOGGER.info(f"Uploading {file_name} to {remote_path}")
        
        # Push file to device
        if is_usb:
            await _run_sync(adb_client.push, file_content, remote_path)
        else:
            await adb_client.push(file_content, remote_path)
        
        _LOGGER.info(f"File uploaded successfully: {remote_path}")
        
        # Trigger media scan so photo appears in gallery
        scan_cmd = f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_path}"
        if is_usb:
            await _run_sync(adb_client.shell, scan_cmd)
        else:
            await adb_client.shell(scan_cmd)
        
        return jsonify({
            "status": "success",
            "message": f"File uploaded to {remote_path}",
            "path": remote_path
        }), 200
    
    except Exception as e:
        _LOGGER.error(f"File upload failed: {e}", exc_info=True)
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route("/download", methods=["POST"])
async def download_file():
    """Download a file from the device."""
    if not adb_client or not adb_client.available:
        return jsonify({"error": "Device is not connected or available."}), 503
    
    _LOGGER.info("Request received for /download")
    
    data = await request.get_json()
    if not data or 'path' not in data:
        return jsonify({"error": "No path provided"}), 400
    
    remote_path = data['path']
    
    try:
        _LOGGER.info(f"Downloading file from {remote_path}")
        
        # Pull file from device
        if is_usb:
            file_content = await _run_sync(adb_client.pull, remote_path)
        else:
            file_content = await adb_client.pull(remote_path)
        
        # Return file as response
        from quart import Response
        import os
        filename = os.path.basename(remote_path)
        
        return Response(
            file_content,
            mimetype='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        ), 200
    
    except Exception as e:
        _LOGGER.error(f"File download failed: {e}", exc_info=True)
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
