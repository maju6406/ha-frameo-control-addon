#!/usr/bin/env python3
"""
Frameo CLI - Command-line interface for Frameo ADB Control API

Usage:
    frameo-cli connect usb <serial>
    frameo-cli connect network <host> [--port <port>]
    frameo-cli devices
    frameo-cli state
    frameo-cli shell <command>
    frameo-cli tcpip
    frameo-cli wake
    frameo-cli sleep
    frameo-cli brightness <level>
    frameo-cli tap <x> <y>
    frameo-cli swipe <x1> <y1> <x2> <y2> [--duration <ms>]
    frameo-cli next
    frameo-cli prev
    frameo-cli home
    frameo-cli back
    frameo-cli open-app
    frameo-cli restart-app
    frameo-cli screenshot [--output <file>]
    frameo-cli upload <file> [--destination <path>]
    frameo-cli download <remote-path> [--output <file>]
    frameo-cli info
    frameo-cli --help
    frameo-cli --version

Options:
    --host <host>           API server host [default: localhost]
    --port <port>           API server port [default: 5000]
    --duration <ms>         Swipe duration in milliseconds [default: 300]
    --output <file>         Output file path [default: screenshot.png]
    --destination <path>    Destination directory on device [default: /sdcard/Frameo]
    -h --help               Show this help message
    --version               Show version
"""

import sys
import json
import os
import requests
from docopt import docopt
from typing import Optional, Dict, Any

VERSION = "1.0.0"
DEFAULT_API_HOST = "localhost"
DEFAULT_API_PORT = 5000


class FrameoCLI:
    """Frameo CLI client"""
    
    def __init__(self, host: str = DEFAULT_API_HOST, port: int = DEFAULT_API_PORT):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[Any, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            self._error(f"Cannot connect to API at {self.base_url}")
            self._error("Make sure the Frameo API server is running")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                self._error(f"API Error: {error_data.get('error', str(e))}")
            except:
                self._error(f"HTTP Error: {e}")
            sys.exit(1)
        except Exception as e:
            self._error(f"Unexpected error: {e}")
            sys.exit(1)
    
    def _success(self, message: str):
        """Print success message"""
        print(f"✓ {message}")
    
    def _error(self, message: str):
        """Print error message"""
        print(f"✗ {message}", file=sys.stderr)
    
    def _info(self, message: str):
        """Print info message"""
        print(f"ℹ {message}")
    
    def _print_json(self, data: Dict):
        """Pretty print JSON data"""
        print(json.dumps(data, indent=2))
    
    def get_usb_devices(self):
        """Get list of USB devices"""
        result = self._request("GET", "/devices/usb")
        if not result:
            self._info("No USB devices found")
            return
        
        print("Available USB devices:")
        for i, serial in enumerate(result, 1):
            print(f"  {i}. {serial}")
    
    def connect_usb(self, serial: str):
        """Connect to USB device"""
        data = {
            "connection_type": "USB",
            "serial": serial
        }
        result = self._request("POST", "/connect", data)
        self._success(f"Connected to USB device: {serial}")
    
    def connect_network(self, host: str, port: int = 5555):
        """Connect to network device"""
        data = {
            "connection_type": "NETWORK",
            "host": host,
            "port": port
        }
        result = self._request("POST", "/connect", data)
        self._success(f"Connected to network device: {host}:{port}")
    
    def get_state(self):
        """Get device state"""
        result = self._request("POST", "/state")
        status = "ON" if result.get("is_on") else "OFF"
        brightness = result.get("brightness", 0)
        
        print(f"Device Status: {status}")
        print(f"Brightness: {brightness}/255 ({int(brightness/255*100)}%)")
    
    def shell(self, command: str):
        """Execute shell command"""
        data = {"command": command}
        result = self._request("POST", "/shell", data)
        output = result.get("result", "")
        if output.strip():
            print(output)
        else:
            self._success("Command executed")
    
    def enable_tcpip(self):
        """Enable wireless debugging"""
        result = self._request("POST", "/tcpip")
        self._success(result.get("result", "Wireless debugging enabled"))
        self._info("You can now connect wirelessly using the device's IP address")
    
    def wake(self):
        """Wake the device"""
        self.shell("input keyevent KEYCODE_WAKEUP")
        self._success("Device woken up")
    
    def sleep(self):
        """Put device to sleep"""
        self.shell("input keyevent KEYCODE_SLEEP")
        self._success("Device sleeping")
    
    def set_brightness(self, level: int):
        """Set screen brightness"""
        if not 0 <= level <= 255:
            self._error("Brightness must be between 0 and 255")
            sys.exit(1)
        
        self.shell(f"settings put system screen_brightness {level}")
        self._success(f"Brightness set to {level}/255 ({int(level/255*100)}%)")
    
    def tap(self, x: int, y: int):
        """Tap at coordinates"""
        self.shell(f"input tap {x} {y}")
        self._success(f"Tapped at ({x}, {y})")
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """Swipe gesture"""
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        self._success(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
    
    def next_photo(self):
        """Swipe to next photo"""
        self.shell("input swipe 900 500 100 500 300")
        self._success("Next photo")
    
    def prev_photo(self):
        """Swipe to previous photo"""
        self.shell("input swipe 100 500 900 500 300")
        self._success("Previous photo")
    
    def home(self):
        """Press home button"""
        self.shell("input keyevent KEYCODE_HOME")
        self._success("Home button pressed")
    
    def back(self):
        """Press back button"""
        self.shell("input keyevent KEYCODE_BACK")
        self._success("Back button pressed")
    
    def open_app(self):
        """Open Frameo app"""
        self.shell("am start -n com.frameo.app/.MainActivity")
        self._success("Frameo app opened")
    
    def restart_app(self):
        """Restart Frameo app"""
        self.shell("am force-stop com.frameo.app")
        self._info("Stopping app...")
        import time
        time.sleep(2)
        self.shell("am start -n com.frameo.app/.MainActivity")
        self._success("Frameo app restarted")
    
    def screenshot(self, output: str = "screenshot.png"):
        """Take screenshot"""
        # Take screenshot on device
        self.shell("screencap -p /sdcard/screenshot.png")
        self._info("Screenshot saved on device at /sdcard/screenshot.png")
        
        # Note: Pulling the file requires additional ADB functionality
        # For now, just inform the user
        self._info("To retrieve the screenshot, use ADB:")
        self._info(f"  adb pull /sdcard/screenshot.png {output}")
    
    def info(self):
        """Display device information"""
        print("Getting device information...\n")
        
        # Device model
        result = self._request("POST", "/shell", {"command": "getprop ro.product.model"})
        print(f"Model: {result.get('result', 'Unknown').strip()}")
        
        # Android version
        result = self._request("POST", "/shell", {"command": "getprop ro.build.version.release"})
        print(f"Android Version: {result.get('result', 'Unknown').strip()}")
        
        # Screen resolution
        result = self._request("POST", "/shell", {"command": "wm size"})
        print(f"Resolution: {result.get('result', 'Unknown').strip()}")
        
        # Battery level
        result = self._request("POST", "/shell", {"command": "dumpsys battery | grep level"})
        battery = result.get('result', '').strip()
        if battery:
            print(f"Battery: {battery}")
        
        # Current state
        print()
        self.get_state()
    
    def upload(self, file_path: str, destination: str = "/sdcard/Frameo"):
        """Upload a file to the device"""
        if not os.path.exists(file_path):
            self._error(f"File not found: {file_path}")
            sys.exit(1)
        
        if not os.path.isfile(file_path):
            self._error(f"Not a file: {file_path}")
            sys.exit(1)
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        self._info(f"Uploading {file_name} ({file_size_mb:.2f} MB)...")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                data = {'destination': destination}
                
                url = f"{self.base_url}/upload"
                response = self.session.post(url, files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                self._success(f"File uploaded: {result.get('path')}")
                self._info("Photo should appear in Frameo shortly")
        
        except requests.exceptions.ConnectionError:
            self._error(f"Cannot connect to API at {self.base_url}")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                self._error(f"Upload failed: {error_data.get('error', str(e))}")
            except:
                self._error(f"HTTP Error: {e}")
            sys.exit(1)
        except Exception as e:
            self._error(f"Upload failed: {e}")
            sys.exit(1)
    
    def download(self, remote_path: str, output: str = None):
        """Download a file from the device"""
        if output is None:
            output = os.path.basename(remote_path)
        
        self._info(f"Downloading {remote_path}...")
        
        try:
            data = {"path": remote_path}
            url = f"{self.base_url}/download"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            with open(output, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            file_size_mb = file_size / (1024 * 1024)
            self._success(f"Downloaded to {output} ({file_size_mb:.2f} MB)")
        
        except requests.exceptions.ConnectionError:
            self._error(f"Cannot connect to API at {self.base_url}")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                self._error(f"Download failed: {error_data.get('error', str(e))}")
            except:
                self._error(f"HTTP Error: {e}")
            sys.exit(1)
        except Exception as e:
            self._error(f"Download failed: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point"""
    args = docopt(__doc__, version=f"Frameo CLI v{VERSION}")
    
    # Parse global options
    host = args.get("--host", DEFAULT_API_HOST)
    port = int(args.get("--port", DEFAULT_API_PORT))
    
    # Initialize CLI
    cli = FrameoCLI(host=host, port=port)
    
    try:
        # Device discovery
        if args["devices"]:
            cli.get_usb_devices()
        
        # Connection
        elif args["connect"]:
            if args["usb"]:
                cli.connect_usb(args["<serial>"])
            elif args["network"]:
                port = int(args.get("--port") or 5555)
                cli.connect_network(args["<host>"], port)
        
        # State
        elif args["state"]:
            cli.get_state()
        
        # Shell command
        elif args["shell"]:
            cli.shell(args["<command>"])
        
        # TCP/IP
        elif args["tcpip"]:
            cli.enable_tcpip()
        
        # Power control
        elif args["wake"]:
            cli.wake()
        elif args["sleep"]:
            cli.sleep()
        
        # Brightness
        elif args["brightness"]:
            cli.set_brightness(int(args["<level>"]))
        
        # Touch input
        elif args["tap"]:
            cli.tap(int(args["<x>"]), int(args["<y>"]))
        elif args["swipe"]:
            duration = int(args.get("--duration") or 300)
            cli.swipe(
                int(args["<x1>"]),
                int(args["<y1>"]),
                int(args["<x2>"]),
                int(args["<y2>"]),
                duration
            )
        
        # Navigation shortcuts
        elif args["next"]:
            cli.next_photo()
        elif args["prev"]:
            cli.prev_photo()
        elif args["home"]:
            cli.home()
        elif args["back"]:
            cli.back()
        
        # App control
        elif args["open-app"]:
            cli.open_app()
        elif args["restart-app"]:
            cli.restart_app()
        
        # Screenshot
        elif args["screenshot"]:
            output = args.get("--output") or "screenshot.png"
            cli.screenshot(output)
        
        # File transfer
        elif args["upload"]:
            destination = args.get("--destination") or "/sdcard/Frameo"
            cli.upload(args["<file>"], destination)
        elif args["download"]:
            output = args.get("--output")
            cli.download(args["<remote-path>"], output)
        
        # Device info
        elif args["info"]:
            cli.info()
    
    except KeyboardInterrupt:
        print("\nAborted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
