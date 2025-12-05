# Frameo ADB Control API - Use Cases & Examples

This document provides practical examples and use cases for leveraging the Frameo ADB Control API to automate and enhance your Frameo digital photo frame experience.

## Table of Contents

- [Home Automation Integration](#home-automation-integration)
- [Scheduled Actions](#scheduled-actions)
- [Photo Management Automation](#photo-management-automation)
- [Interactive Kiosk Mode](#interactive-kiosk-mode)
- [Remote Control Interface](#remote-control-interface)
- [Advanced Automation](#advanced-automation)

---

## Home Automation Integration

### 1. Turn Frame On/Off with Presence Detection

Automatically wake your Frameo when you arrive home and sleep it when you leave.

```python
import requests
from datetime import datetime

class FrameoHomeAutomation:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def wake_frame(self):
        """Wake the screen"""
        response = requests.post(
            f"{self.api_url}/shell",
            json={"command": "input keyevent KEYCODE_WAKEUP"}
        )
        print("Frame woken up")
        return response.json()
    
    def sleep_frame(self):
        """Put screen to sleep"""
        response = requests.post(
            f"{self.api_url}/shell",
            json={"command": "input keyevent KEYCODE_SLEEP"}
        )
        print("Frame put to sleep")
        return response.json()
    
    def set_brightness(self, level):
        """Set brightness (0-255)"""
        response = requests.post(
            f"{self.api_url}/shell",
            json={"command": f"settings put system screen_brightness {level}"}
        )
        print(f"Brightness set to {level}")
        return response.json()
    
    def bedtime_mode(self):
        """Dim and sleep the frame for bedtime"""
        self.set_brightness(50)  # Dim first
        time.sleep(2)
        self.sleep_frame()
    
    def morning_mode(self):
        """Wake frame and set bright for daytime"""
        self.wake_frame()
        time.sleep(1)
        self.set_brightness(200)

# Usage with Home Automation Systems
automation = FrameoHomeAutomation()

# When someone arrives home
automation.morning_mode()

# When everyone leaves
automation.sleep_frame()

# Bedtime routine
automation.bedtime_mode()
```

### 2. Smart Scene Integration

Integrate with smart home scenes (Philips Hue, Google Home, etc.)

```python
# Movie Night Scene
def movie_night_scene():
    frameo = FrameoHomeAutomation()
    frameo.set_brightness(30)  # Dim the frame
    # Integrate with your other smart home devices
    # hue.set_lights(dim=True)
    # tv.turn_on()

# Dinner Party Scene
def dinner_party_scene():
    frameo = FrameoHomeAutomation()
    frameo.wake_frame()
    frameo.set_brightness(150)
    # Show photo slideshow
    frameo.shell("am start -n com.frameo.app/.MainActivity")

# Good Night Scene
def good_night_scene():
    frameo = FrameoHomeAutomation()
    frameo.sleep_frame()
    # Lock doors, turn off lights, etc.
```

---

## Scheduled Actions

### 3. Daily Photo Rotation Schedule

Automatically navigate through photo albums at specific times.

```python
import schedule
import time

class FrameoScheduler:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def shell(self, command):
        response = requests.post(
            f"{self.api_url}/shell",
            json={"command": command}
        )
        return response.json()
    
    def tap(self, x, y):
        self.shell(f"input tap {x} {y}")
    
    def swipe_left(self):
        """Swipe to next photo"""
        self.shell("input swipe 900 500 100 500 300")
    
    def swipe_right(self):
        """Swipe to previous photo"""
        self.shell("input swipe 100 500 900 500 300")
    
    def open_frameo_app(self):
        """Launch Frameo app"""
        self.shell("am start -n com.frameo.app/.MainActivity")
    
    def go_home(self):
        """Go to home screen"""
        self.shell("input keyevent KEYCODE_HOME")

# Setup scheduler
scheduler = FrameoScheduler()

# Morning: Show family photos
schedule.every().day.at("07:00").do(scheduler.open_frameo_app)
schedule.every().day.at("07:00").do(scheduler.tap, 500, 300)  # Open family album

# Afternoon: Show travel photos
schedule.every().day.at("14:00").do(scheduler.tap, 500, 500)  # Open travel album

# Evening: Show recent photos
schedule.every().day.at("18:00").do(scheduler.tap, 500, 700)  # Open recent photos

# Night: Sleep the frame
schedule.every().day.at("23:00").do(scheduler.go_home)
schedule.every().day.at("23:00").do(lambda: scheduler.shell("input keyevent KEYCODE_SLEEP"))

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### 4. Weather-Based Slideshow

Show different photo collections based on weather conditions.

```python
import requests
from datetime import datetime

def get_weather():
    # Use your preferred weather API
    weather_api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "YourCity",
        "appid": "YOUR_API_KEY"
    }
    response = requests.get(weather_api_url, params=params)
    data = response.json()
    return data['weather'][0]['main']  # e.g., "Clear", "Rain", "Snow"

def show_weather_appropriate_photos():
    frameo = FrameoScheduler()
    weather = get_weather()
    
    if weather == "Snow":
        print("Showing winter photos")
        frameo.tap(500, 400)  # Winter album coordinates
    elif weather == "Rain":
        print("Showing cozy indoor photos")
        frameo.tap(500, 600)  # Indoor album
    elif weather == "Clear":
        print("Showing sunny outdoor photos")
        frameo.tap(500, 200)  # Outdoor adventures album
    else:
        print("Showing recent photos")
        frameo.tap(500, 800)  # Recent album

# Run every morning
schedule.every().day.at("08:00").do(show_weather_appropriate_photos)
```

---

## Photo Management Automation

### 5. Automatic Photo Upload

Monitor a folder and automatically upload new photos to your Frameo.

```python
import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FrameoPhotoUploader(FileSystemEventHandler):
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.uploading = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Check if it's an image file
        if event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            # Wait a moment for file to be fully written
            time.sleep(2)
            self.upload_photo(event.src_path)
    
    def upload_photo(self, file_path):
        """Upload photo to Frameo"""
        if file_path in self.uploading:
            return
        
        self.uploading.add(file_path)
        
        try:
            file_name = os.path.basename(file_path)
            print(f"📤 Uploading {file_name}...")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                response = requests.post(f"{self.api_url}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✓ Uploaded: {result['path']}")
                else:
                    print(f"✗ Upload failed: {response.text}")
        
        except Exception as e:
            print(f"✗ Error uploading {file_name}: {e}")
        
        finally:
            self.uploading.remove(file_path)

# Watch your photo sync folder
observer = Observer()
event_handler = FrameoPhotoUploader("http://localhost:5000")
observer.schedule(event_handler, path="/path/to/photo/folder", recursive=True)
observer.start()

print("👀 Watching for new photos...")
print("Drop photos into the watched folder to auto-upload!")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print("\nStopped watching")
observer.join()
```

### 6. Batch Photo Upload with Progress

Upload multiple photos with progress tracking and error handling.

```python
import os
import requests
from pathlib import Path

class BatchPhotoUploader:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def upload_photo(self, file_path):
        """Upload a single photo"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(f"{self.api_url}/upload", files=files, timeout=30)
                response.raise_for_status()
                return True, response.json()
        except Exception as e:
            return False, str(e)
    
    def upload_directory(self, directory, extensions=None):
        """Upload all photos from a directory"""
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        # Find all image files
        photo_files = []
        for ext in extensions:
            photo_files.extend(Path(directory).rglob(f"*{ext}"))
            photo_files.extend(Path(directory).rglob(f"*{ext.upper()}"))
        
        if not photo_files:
            print(f"No photos found in {directory}")
            return
        
        print(f"Found {len(photo_files)} photos to upload\n")
        
        success_count = 0
        failed_uploads = []
        
        for idx, photo_path in enumerate(photo_files, 1):
            file_name = photo_path.name
            file_size = photo_path.stat().st_size / (1024 * 1024)  # MB
            
            print(f"[{idx}/{len(photo_files)}] Uploading {file_name} ({file_size:.2f} MB)...", end=" ")
            
            success, result = self.upload_photo(str(photo_path))
            
            if success:
                print("✓")
                success_count += 1
            else:
                print(f"✗ {result}")
                failed_uploads.append((file_name, result))
            
            # Brief pause to avoid overwhelming the device
            time.sleep(0.5)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Upload Complete!")
        print(f"Successful: {success_count}/{len(photo_files)}")
        
        if failed_uploads:
            print(f"\nFailed uploads:")
            for file_name, error in failed_uploads:
                print(f"  ✗ {file_name}: {error}")

# Usage
uploader = BatchPhotoUploader()

# Upload all photos from a directory
uploader.upload_directory("/path/to/vacation/photos")

# Upload specific file types only
uploader.upload_directory("/path/to/photos", extensions=['.jpg', '.png'])
```

### 7. Automatic Photo Refresh

Monitor a folder and auto-refresh the frame when new photos are added.

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PhotoFolderWatcher(FileSystemEventHandler):
    def __init__(self, frameo_api_url):
        self.api_url = frameo_api_url
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            print(f"New photo detected: {event.src_path}")
            # Refresh the Frameo app
            self.refresh_frameo()
    
    def refresh_frameo(self):
        """Force refresh the photo feed"""
        response = requests.post(
            f"{self.api_url}/shell",
            json={"command": "am force-stop com.frameo.app"}
        )
        time.sleep(2)
        response = requests.post(
            f"{self.api_url}/shell",
            json={"command": "am start -n com.frameo.app/.MainActivity"}
        )
        print("Frameo app refreshed")

# Watch your photo sync folder
observer = Observer()
event_handler = PhotoFolderWatcher("http://localhost:5000")
observer.schedule(event_handler, path="/path/to/frameo/photos", recursive=True)
observer.start()

print("Watching for new photos...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### 7. Cloud Photo Sync

Automatically download and upload photos from cloud services.

```python
import requests
import tempfile
import os
from dropbox import Dropbox  # pip install dropbox

class CloudToFrameoSync:
    def __init__(self, frameo_api="http://localhost:5000", dropbox_token=None):
        self.frameo_api = frameo_api
        self.dbx = Dropbox(dropbox_token) if dropbox_token else None
    
    def sync_from_dropbox(self, dropbox_folder="/Photos"):
        """Download photos from Dropbox and upload to Frameo"""
        if not self.dbx:
            print("Dropbox not configured")
            return
        
        print(f"Syncing from Dropbox folder: {dropbox_folder}")
        
        # List files in Dropbox folder
        try:
            result = self.dbx.files_list_folder(dropbox_folder)
            
            for entry in result.entries:
                if entry.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    print(f"📥 Downloading {entry.name}...")
                    
                    # Download to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(entry.name)[1]) as tmp:
                        metadata, response = self.dbx.files_download(entry.path_lower)
                        tmp.write(response.content)
                        tmp_path = tmp.name
                    
                    # Upload to Frameo
                    print(f"📤 Uploading to Frameo...")
                    with open(tmp_path, 'rb') as f:
                        files = {'file': (entry.name, f)}
                        upload_response = requests.post(f"{self.frameo_api}/upload", files=files)
                        
                        if upload_response.status_code == 200:
                            print(f"✓ Synced: {entry.name}")
                        else:
                            print(f"✗ Upload failed: {entry.name}")
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
        
        except Exception as e:
            print(f"Error syncing from Dropbox: {e}")

# Usage
sync = CloudToFrameoSync(
    frameo_api="http://localhost:5000",
    dropbox_token="YOUR_DROPBOX_TOKEN"
)

# Sync photos from Dropbox
sync.sync_from_dropbox("/Camera Uploads")

# Schedule to run daily
import schedule
schedule.every().day.at("02:00").do(sync.sync_from_dropbox, "/Camera Uploads")

while True:
    schedule.run_pending()
    time.sleep(3600)
```

### 8. Bulk Photo Navigation

Create a photo tour that automatically shows specific photos.

```python
class PhotoTour:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def shell(self, command):
        response = requests.post(f"{self.api_url}/shell", json={"command": command})
        return response.json()
    
    def show_photo_sequence(self, photo_coordinates, display_time=5):
        """
        Show a sequence of photos by tapping their coordinates
        photo_coordinates: list of (x, y) tuples
        display_time: seconds to display each photo
        """
        for x, y in photo_coordinates:
            self.shell(f"input tap {x} {y}")
            print(f"Showing photo at ({x}, {y})")
            time.sleep(display_time)
    
    def create_story(self):
        """Create a photo story - vacation highlights"""
        story_photos = [
            (500, 300),  # Arrival at destination
            (500, 400),  # First day
            (500, 500),  # Adventure day
            (500, 600),  # Food photo
            (500, 700),  # Sunset
            (500, 800),  # Goodbye
        ]
        
        self.show_photo_sequence(story_photos, display_time=8)

# Run the photo tour
tour = PhotoTour()
tour.create_story()
```

---

## Interactive Kiosk Mode

### 7. Guest Book Interface

Let guests interact with the frame to leave messages or select photo albums.

```python
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
FRAMEO_API = "http://localhost:5000"

@app.route('/')
def home():
    return render_template('guest_control.html')

@app.route('/album/<album_name>')
def show_album(album_name):
    """Show different albums based on guest selection"""
    album_coords = {
        'family': (500, 300),
        'vacation': (500, 500),
        'holidays': (500, 700),
        'recent': (500, 900)
    }
    
    if album_name in album_coords:
        x, y = album_coords[album_name]
        requests.post(
            f"{FRAMEO_API}/shell",
            json={"command": f"input tap {x} {y}"}
        )
        return f"Now showing: {album_name.title()} Album"
    
    return "Album not found", 404

@app.route('/control/<action>')
def control_frame(action):
    """Control frame actions"""
    commands = {
        'next': "input swipe 900 500 100 500 300",
        'prev': "input swipe 100 500 900 500 300",
        'home': "input keyevent KEYCODE_HOME",
        'sleep': "input keyevent KEYCODE_SLEEP",
        'wake': "input keyevent KEYCODE_WAKEUP"
    }
    
    if action in commands:
        requests.post(
            f"{FRAMEO_API}/shell",
            json={"command": commands[action]}
        )
        return f"Action executed: {action}"
    
    return "Action not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

HTML template (`templates/guest_control.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Frameo Guest Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .button-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            max-width: 600px;
            margin: 2rem auto;
        }
        button {
            padding: 2rem;
            font-size: 1.2rem;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            background: white;
            color: #333;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <h1>📷 Choose Your Photo Album</h1>
    
    <div class="button-grid">
        <button onclick="showAlbum('family')">👨‍👩‍👧‍👦 Family</button>
        <button onclick="showAlbum('vacation')">🏖️ Vacation</button>
        <button onclick="showAlbum('holidays')">🎄 Holidays</button>
        <button onclick="showAlbum('recent')">📸 Recent</button>
    </div>
    
    <h2>⏯️ Controls</h2>
    <div class="button-grid">
        <button onclick="control('prev')">⬅️ Previous</button>
        <button onclick="control('next')">➡️ Next</button>
        <button onclick="control('wake')">💡 Wake</button>
        <button onclick="control('sleep')">💤 Sleep</button>
    </div>
    
    <script>
        function showAlbum(album) {
            fetch(`/album/${album}`)
                .then(response => response.text())
                .then(message => alert(message));
        }
        
        function control(action) {
            fetch(`/control/${action}`)
                .then(response => response.text())
                .then(message => console.log(message));
        }
    </script>
</body>
</html>
```

---

## Remote Control Interface

### 8. Mobile App/Web Interface

Create a custom remote control web app.

```javascript
// React component for Frameo remote control
import React, { useState } from 'react';
import axios from 'axios';

function FrameoRemote() {
  const [status, setStatus] = useState('');
  const API_URL = 'http://localhost:5000';
  
  const sendCommand = async (command) => {
    try {
      const response = await axios.post(`${API_URL}/shell`, {
        command: command
      });
      setStatus(`✓ ${command}`);
    } catch (error) {
      setStatus(`✗ Error: ${error.message}`);
    }
  };
  
  const getState = async () => {
    try {
      const response = await axios.post(`${API_URL}/state`);
      const { is_on, brightness } = response.data;
      setStatus(`Frame is ${is_on ? 'ON' : 'OFF'}, Brightness: ${brightness}`);
    } catch (error) {
      setStatus(`✗ Error: ${error.message}`);
    }
  };
  
  return (
    <div className="frameo-remote">
      <h1>Frameo Remote Control</h1>
      
      <div className="status-bar">
        <button onClick={getState}>Refresh Status</button>
        <p>{status}</p>
      </div>
      
      <div className="control-grid">
        <h2>Power</h2>
        <button onClick={() => sendCommand('input keyevent KEYCODE_WAKEUP')}>
          💡 Wake
        </button>
        <button onClick={() => sendCommand('input keyevent KEYCODE_SLEEP')}>
          💤 Sleep
        </button>
        
        <h2>Navigation</h2>
        <button onClick={() => sendCommand('input keyevent KEYCODE_HOME')}>
          🏠 Home
        </button>
        <button onClick={() => sendCommand('input keyevent KEYCODE_BACK')}>
          ⬅️ Back
        </button>
        
        <h2>Photo Control</h2>
        <button onClick={() => sendCommand('input swipe 900 500 100 500 300')}>
          ➡️ Next Photo
        </button>
        <button onClick={() => sendCommand('input swipe 100 500 900 500 300')}>
          ⬅️ Previous Photo
        </button>
        <button onClick={() => sendCommand('input tap 960 540')}>
          ▶️ Play/Pause
        </button>
        
        <h2>Brightness</h2>
        <button onClick={() => sendCommand('settings put system screen_brightness 50')}>
          🔅 Low
        </button>
        <button onClick={() => sendCommand('settings put system screen_brightness 150')}>
          💡 Medium
        </button>
        <button onClick={() => sendCommand('settings put system screen_brightness 255')}>
          ☀️ Bright
        </button>
        
        <h2>Quick Actions</h2>
        <button onClick={() => sendCommand('am start -n com.frameo.app/.MainActivity')}>
          📷 Open Frameo
        </button>
        <button onClick={() => sendCommand('am force-stop com.frameo.app')}>
          🔄 Restart App
        </button>
      </div>
    </div>
  );
}

export default FrameoRemote;
```

---

## Advanced Automation

### 9. Context-Aware Display

Show different content based on time, weather, calendar events, etc.

```python
import requests
from datetime import datetime
import calendar

class SmartFrameoController:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def shell(self, command):
        response = requests.post(f"{self.api_url}/shell", json={"command": command})
        return response.json()
    
    def get_context(self):
        """Get current context"""
        now = datetime.now()
        return {
            'hour': now.hour,
            'day_of_week': calendar.day_name[now.weekday()],
            'month': now.month,
            'is_weekend': now.weekday() >= 5,
            'is_holiday_season': now.month in [11, 12],
        }
    
    def smart_display(self):
        """Display appropriate content based on context"""
        context = self.get_context()
        
        # Holiday season: Show holiday photos
        if context['is_holiday_season']:
            print("🎄 Showing holiday photos")
            self.shell("input tap 500 700")  # Holiday album
        
        # Weekend morning: Show family photos
        elif context['is_weekend'] and 8 <= context['hour'] < 12:
            print("☀️ Weekend morning - family photos")
            self.shell("input tap 500 300")  # Family album
        
        # Weekday morning: Show motivational quotes/sunrise photos
        elif not context['is_weekend'] and 6 <= context['hour'] < 9:
            print("💪 Weekday motivation")
            self.shell("input tap 500, 400")  # Motivation album
        
        # Evening: Show calming photos
        elif 19 <= context['hour'] < 23:
            print("🌙 Evening relaxation")
            self.shell("input tap 500 600")  # Calming scenes
        
        # Default: Recent photos
        else:
            print("📸 Recent photos")
            self.shell("input tap 500 900")

# Run smart display logic periodically
controller = SmartFrameoController()
schedule.every().hour.do(controller.smart_display)
```

### 10. Voice Control Integration

Integrate with voice assistants.

```python
# Google Assistant / Alexa integration example
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
FRAMEO_API = "http://localhost:5000"

@app.route('/voice-command', methods=['POST'])
def voice_command():
    """Handle voice assistant webhook"""
    data = request.json
    intent = data.get('intent')
    
    commands = {
        'FrameoWake': 'input keyevent KEYCODE_WAKEUP',
        'FrameoSleep': 'input keyevent KEYCODE_SLEEP',
        'FrameoNext': 'input swipe 900 500 100 500 300',
        'FrameoPrevious': 'input swipe 100 500 900 500 300',
        'FrameoShowFamily': 'input tap 500 300',
        'FrameoShowVacation': 'input tap 500 500',
        'FrameoBrighter': 'settings put system screen_brightness 255',
        'FrameoDimmer': 'settings put system screen_brightness 50',
    }
    
    if intent in commands:
        response = requests.post(
            f"{FRAMEO_API}/shell",
            json={"command": commands[intent]}
        )
        return jsonify({
            "speech": f"Okay, {intent.replace('Frameo', '')} executed",
            "success": True
        })
    
    return jsonify({
        "speech": "Sorry, I don't understand that command",
        "success": False
    })

if __name__ == '__main__':
    app.run(port=5001)

# Voice commands:
# "Hey Google, turn on my photo frame"
# "Alexa, show family photos on frame"
# "Hey Google, next photo"
```

### 11. Smart Notifications

Display notifications on the frame.

```python
def send_notification_to_frame(title, message):
    """Display a notification on the Frameo"""
    # Take screenshot first
    requests.post(
        "http://localhost:5000/shell",
        json={"command": "screencap -p /sdcard/backup.png"}
    )
    
    # Show notification using Android's notification system
    notification_cmd = f'am broadcast -a android.intent.action.VIEW -d "notification://{title}/{message}"'
    requests.post(
        "http://localhost:5000/shell",
        json={"command": notification_cmd}
    )
    
    # Auto-dismiss after 10 seconds
    time.sleep(10)
    requests.post(
        "http://localhost:5000/shell",
        json={"command": "input keyevent KEYCODE_BACK"}
    )

# Examples:
send_notification_to_frame("Doorbell", "Someone is at the door!")
send_notification_to_frame("Weather Alert", "Rain expected in 30 minutes")
send_notification_to_frame("Reminder", "Take out the trash")
```

### 12. Integration with IFTTT/Zapier

Create webhooks for automation platforms.

```python
# Webhook endpoint for IFTTT/Zapier
@app.route('/webhook/frameo', methods=['POST'])
def webhook_handler():
    """
    Handle webhooks from IFTTT, Zapier, etc.
    
    POST body:
    {
        "action": "show_album",
        "album": "family"
    }
    """
    data = request.json
    action = data.get('action')
    
    if action == 'show_album':
        album = data.get('album')
        album_positions = {
            'family': (500, 300),
            'vacation': (500, 500),
            'recent': (500, 900)
        }
        if album in album_positions:
            x, y = album_positions[album]
            requests.post(
                f"{FRAMEO_API}/shell",
                json={"command": f"input tap {x} {y}"}
            )
            return jsonify({"success": True})
    
    elif action == 'wake':
        requests.post(
            f"{FRAMEO_API}/shell",
            json={"command": "input keyevent KEYCODE_WAKEUP"}
        )
        return jsonify({"success": True})
    
    return jsonify({"error": "Unknown action"}), 400

# IFTTT Applet examples:
# "When I arrive home, wake my Frameo"
# "Every morning at 8am, show family photos"
# "When it's raining, show umbrella reminder"
```

---

## Summary

The Frameo Control API enables you to:

✅ **Automate** frame behavior based on time, presence, or events  
✅ **Integrate** with smart home systems (Home Assistant, Node-RED, OpenHAB, etc.)  
✅ **Create** custom interfaces (web apps, mobile apps, voice control)  
✅ **Schedule** content rotation and power management  
✅ **Monitor** and respond to photo uploads  
✅ **Build** interactive experiences for guests  
✅ **Connect** with IFTTT, Zapier, and other automation platforms  

The possibilities are endless! Start with simple automations and expand to create a truly smart photo frame experience.
