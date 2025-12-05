# Frameo CLI

Command-line interface for the Frameo ADB Control API.

## Installation

### Quick Install

```bash
./install-cli.sh
```

This will:
1. Install Python dependencies
2. Make the CLI executable
3. Create a symlink in `~/.local/bin/frameo-cli`

### Manual Install

```bash
# Install dependencies
pip3 install -r cli-requirements.txt

# Make executable
chmod +x frameo-cli.py

# Create symlink (optional)
ln -s $(pwd)/frameo-cli.py ~/.local/bin/frameo-cli
```

### Add to PATH

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

## Usage

### Basic Commands

```bash
# Show help
frameo-cli --help

# List USB devices
frameo-cli devices

# Connect to USB device
frameo-cli connect usb ABC123DEF456

# Connect to network device
frameo-cli connect network 192.168.1.100
frameo-cli connect network 192.168.1.100 --port 5555

# Get device state
frameo-cli state

# Get device information
frameo-cli info
```

### Power Control

```bash
# Wake the device
frameo-cli wake

# Put device to sleep
frameo-cli sleep

# Set brightness (0-255)
frameo-cli brightness 150
frameo-cli brightness 50   # Dim
frameo-cli brightness 255  # Maximum
```

### Navigation

```bash
# Next photo
frameo-cli next

# Previous photo
frameo-cli prev

# Home button
frameo-cli home

# Back button
frameo-cli back
```

### App Control

```bash
# Open Frameo app
frameo-cli open-app

# Restart Frameo app
frameo-cli restart-app
```

### Touch Input

```bash
# Tap at coordinates
frameo-cli tap 500 500

# Swipe gesture
frameo-cli swipe 100 500 900 500
frameo-cli swipe 100 500 900 500 --duration 500
```

### Shell Commands

```bash
# Execute any shell command
frameo-cli shell "input tap 500 500"
frameo-cli shell "input keyevent KEYCODE_HOME"
frameo-cli shell "wm size"
frameo-cli shell "dumpsys battery"
```

### Wireless ADB

```bash
# Enable wireless debugging (requires USB connection first)
frameo-cli tcpip

# Then disconnect USB and connect wirelessly
frameo-cli connect network 192.168.1.100
```

### Screenshots

```bash
# Take screenshot (saves on device)
frameo-cli screenshot
frameo-cli screenshot --output my-screenshot.png
```

### File Transfer

```bash
# Upload a photo to Frameo
frameo-cli upload photo.jpg

# Upload to custom directory
frameo-cli upload photo.jpg --destination /sdcard/Pictures

# Upload multiple photos
for photo in *.jpg; do
  frameo-cli upload "$photo"
done

# Download a file from device
frameo-cli download /sdcard/screenshot.png
frameo-cli download /sdcard/Frameo/photo.jpg --output backup.jpg
```

## Advanced Usage

### Custom API Server

```bash
# Connect to non-default API server
frameo-cli --host 192.168.1.50 --port 8000 devices
frameo-cli --host remote-server.com state
```

### Scripting

Use the CLI in bash scripts:

```bash
#!/bin/bash

# Morning routine
frameo-cli wake
sleep 2
frameo-cli brightness 200
frameo-cli open-app
```

```bash
#!/bin/bash

# Photo slideshow script
echo "Starting photo slideshow..."
for i in {1..10}; do
    frameo-cli next
    sleep 5
done
echo "Slideshow complete!"
```

### Automation with Cron

```bash
# Edit crontab
crontab -e

# Add scheduled tasks
0 7 * * * /home/user/.local/bin/frameo-cli wake          # Wake at 7am
0 23 * * * /home/user/.local/bin/frameo-cli sleep        # Sleep at 11pm
0 8 * * * /home/user/.local/bin/frameo-cli brightness 200  # Bright in morning
0 20 * * * /home/user/.local/bin/frameo-cli brightness 100 # Dim in evening
```

### Integration with Other Tools

```bash
# Use with watch for monitoring
watch -n 5 frameo-cli state

# Pipe shell command output
frameo-cli shell "ps | grep frameo"

# Use in loops
for album in family vacation holidays; do
    frameo-cli tap 500 $((300 + album_index * 200))
    sleep 10
done
```

## Common Use Cases

### Quick Photo Navigation

```bash
# Create aliases in ~/.bashrc
alias fn='frameo-cli next'
alias fp='frameo-cli prev'
alias fw='frameo-cli wake'
alias fs='frameo-cli sleep'

# Now you can just type:
fn  # Next photo
fp  # Previous photo
```

### Device Setup Workflow

```bash
# 1. Find your device
frameo-cli devices

# 2. Connect via USB
frameo-cli connect usb ABC123DEF456

# 3. Enable wireless
frameo-cli tcpip

# 4. Find device IP (check your router or device settings)

# 5. Connect wirelessly
frameo-cli connect network 192.168.1.100

# 6. Test it
frameo-cli state
```

### Daily Automation

```bash
#!/bin/bash
# save as ~/frameo-daily.sh

# Morning
frameo-cli wake
frameo-cli brightness 200
frameo-cli open-app

# Show family photos (tap album at position)
frameo-cli tap 500 300

# Afternoon - switch to vacation photos
sleep 21600  # 6 hours
frameo-cli tap 500 500

# Evening - dim
sleep 21600  # 6 hours  
frameo-cli brightness 100

# Night - sleep
sleep 10800  # 3 hours
frameo-cli sleep
```

### Batch Photo Upload

```bash
#!/bin/bash
# Upload all photos from a directory

PHOTO_DIR="/path/to/photos"
echo "Uploading photos from $PHOTO_DIR..."

for photo in "$PHOTO_DIR"/*.{jpg,jpeg,png,gif}; do
    if [ -f "$photo" ]; then
        echo "Uploading $(basename "$photo")..."
        frameo-cli upload "$photo"
        sleep 1  # Brief pause between uploads
    fi
done

echo "All photos uploaded!"

# Refresh the Frameo app
frameo-cli restart-app
```

### Photo Sync Script

```bash
#!/bin/bash
# Watch a folder and auto-upload new photos

WATCH_DIR="/path/to/sync"

inotifywait -m -e close_write --format '%w%f' "$WATCH_DIR" | while read photo
do
    if [[ "$photo" =~ \.(jpg|jpeg|png|gif)$ ]]; then
        echo "New photo detected: $photo"
        frameo-cli upload "$photo"
    fi
done
```

## Troubleshooting

### Connection Issues

```bash
# Check if API server is running
curl http://localhost:5000/devices/usb

# Try connecting with explicit host
frameo-cli --host localhost --port 5000 devices
```

### Device Not Found

```bash
# List USB devices
frameo-cli devices

# Check USB connection
lsusb | grep Android

# Try reconnecting
frameo-cli connect usb <serial>
```

### Command Not Found

```bash
# Check if CLI is in PATH
which frameo-cli

# If not found, add to PATH or use full path
~/.local/bin/frameo-cli devices

# Or reinstall
./install-cli.sh
```

## Examples

See [EXAMPLES.md](EXAMPLES.md) for more advanced use cases and integration examples.

## API Documentation

- [API.md](API.md) - Complete API reference
- [OpenAPI Spec](openapi.yaml) - Machine-readable API specification

## Requirements

- Python 3.6+
- `requests` library
- `docopt` library
- Running Frameo ADB Control API server

## License

See [LICENSE](LICENSE) file for details.
