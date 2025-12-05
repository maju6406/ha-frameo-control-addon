# WiFi Connection Guide

Yes! The Frameo ADB Control API and CLI work perfectly over WiFi. This guide explains how to set up and use wireless ADB.

## Quick Answer

**Yes, everything works over WiFi!** Once you enable wireless ADB, you can:
- ✅ Control the frame remotely (no USB cable needed)
- ✅ Upload photos wirelessly
- ✅ Execute commands from anywhere on your network
- ✅ Integrate with home automation systems
- ✅ Use the CLI from any computer on your network

## Setup Process

### Initial Setup (Requires USB Once)

You need USB connection **only once** to enable wireless debugging:

```bash
# 1. Connect device via USB
frameo-cli devices
# Output: ABC123DEF456

# 2. Connect to device
frameo-cli connect usb ABC123DEF456

# 3. Enable wireless debugging
frameo-cli tcpip
# Output: ✓ TCP/IP enabled on port 5555

# 4. Find your Frameo's IP address
# Check your router's DHCP clients list, or use:
frameo-cli shell "ip addr show wlan0 | grep 'inet '"
```

### Wireless Connection

After enabling wireless ADB, disconnect USB and connect via network:

```bash
# Connect wirelessly (replace with your Frameo's IP)
frameo-cli connect network 192.168.1.100

# Now everything works over WiFi!
frameo-cli state
frameo-cli upload photo.jpg
frameo-cli next
```

## How It Works

### Architecture

```
┌──────────────┐         WiFi         ┌──────────────┐
│   Computer   │ ◄─────────────────► │    Frameo    │
│              │                       │    Device    │
│  CLI or API  │   Port 5555 (ADB)    │              │
│              │                       │              │
└──────────────┘                       └──────────────┘
```

### Connection Methods

1. **USB Connection**
   - Direct USB cable to device
   - Required for initial wireless setup
   - Faster for large file transfers
   - No network issues

2. **Network Connection** (WiFi)
   - Works over local network
   - No cable required
   - Access from any device on network
   - Persistent across reboots (usually)

## Using WiFi Connection

### API Usage

```bash
# API server connects to device over WiFi
curl -X POST http://localhost:5000/connect \
  -H "Content-Type: application/json" \
  -d '{
    "connection_type": "NETWORK",
    "host": "192.168.1.100",
    "port": 5555
  }'

# Now all API calls work wirelessly
curl -X POST http://localhost:5000/upload -F "file=@photo.jpg"
curl -X POST http://localhost:5000/shell -d '{"command": "input tap 500 500"}'
```

### CLI Usage

```bash
# Connect once
frameo-cli connect network 192.168.1.100

# All commands now work over WiFi
frameo-cli wake
frameo-cli upload vacation/*.jpg
frameo-cli next
frameo-cli brightness 200
```

### Python Client

```python
import requests

# Connect to Frameo over WiFi
response = requests.post('http://localhost:5000/connect', json={
    'connection_type': 'NETWORK',
    'host': '192.168.1.100',
    'port': 5555
})

# Upload photos wirelessly
with open('photo.jpg', 'rb') as f:
    requests.post('http://localhost:5000/upload', files={'file': f})

# Control remotely
requests.post('http://localhost:5000/shell', json={
    'command': 'input swipe 900 500 100 500 300'
})
```

## Finding Your Frameo's IP Address

### Method 1: Router Admin Page
1. Log into your router (usually 192.168.1.1 or 192.168.0.1)
2. Look for "Connected Devices" or "DHCP Clients"
3. Find device named "Frameo" or similar

### Method 2: Using Connected Device
If you're still USB-connected:
```bash
frameo-cli shell "ip addr show wlan0"
# Look for: inet 192.168.1.100/24
```

### Method 3: Network Scanner
```bash
# Using nmap (if installed)
nmap -p 5555 192.168.1.0/24

# Using arp-scan
sudo arp-scan --localnet | grep -i frameo
```

### Method 4: Frameo Settings
Check the device's WiFi settings:
1. Tap Settings on Frameo
2. Look for Network or WiFi settings
3. IP address should be displayed

## Persistent Wireless Connection

### Keep Wireless ADB Enabled

Wireless ADB usually persists across reboots, but you can ensure it stays enabled:

```bash
# Check if wireless ADB is active
frameo-cli connect network 192.168.1.100

# If it fails, reconnect via USB and re-enable
frameo-cli connect usb ABC123DEF456
frameo-cli tcpip
```

### Auto-Reconnect Script

```bash
#!/bin/bash
# auto-reconnect.sh - Try WiFi first, fall back to USB

FRAMEO_IP="192.168.1.100"
FRAMEO_SERIAL="ABC123DEF456"

echo "Trying WiFi connection..."
if frameo-cli --host localhost --port 5000 connect network "$FRAMEO_IP" 2>/dev/null; then
    echo "✓ Connected via WiFi"
    exit 0
fi

echo "WiFi failed, trying USB..."
if frameo-cli connect usb "$FRAMEO_SERIAL"; then
    echo "✓ Connected via USB"
    echo "Re-enabling wireless ADB..."
    frameo-cli tcpip
    sleep 2
    frameo-cli connect network "$FRAMEO_IP"
    echo "✓ Switched to WiFi"
    exit 0
fi

echo "✗ Connection failed"
exit 1
```

## Remote Access (Beyond Local Network)

### Access from Anywhere

To access your Frameo from outside your home network, you need to:

#### Option 1: VPN
Set up a VPN to your home network (recommended for security):
```bash
# Connect to home VPN first
# Then use local IP as normal
frameo-cli connect network 192.168.1.100
```

#### Option 2: Port Forwarding
Forward port 5555 on your router (less secure):
```bash
# Connect using public IP
frameo-cli connect network YOUR_PUBLIC_IP --port 5555
```

**⚠️ Security Warning**: Port forwarding ADB to the internet is not recommended without additional security measures.

#### Option 3: SSH Tunnel
Create an SSH tunnel through a machine on your network:
```bash
# From remote location
ssh -L 5555:192.168.1.100:5555 user@home-server.com

# Then connect via localhost
frameo-cli connect network localhost --port 5555
```

## Performance Considerations

### WiFi vs USB

| Feature | WiFi | USB |
|---------|------|-----|
| **Speed** | Good (depends on network) | Excellent |
| **Convenience** | Excellent (wireless) | Requires cable |
| **Range** | Anywhere on network | Cable length |
| **Reliability** | Good (can drop on network issues) | Excellent |
| **Setup** | One-time USB setup needed | Plug and play |
| **File Uploads** | Fast enough for photos | Faster for large files |

### Recommendations

- **WiFi** for: Daily control, automation, scheduled uploads
- **USB** for: Initial setup, troubleshooting, bulk photo uploads

### Upload Speed Comparison

Typical WiFi speeds for photo uploads:
- Small photo (2MB): < 1 second
- Medium photo (5MB): 1-2 seconds
- Large photo (10MB): 2-4 seconds
- 100 photos batch: 2-5 minutes

This is more than fast enough for normal use!

## Troubleshooting WiFi Connection

### Connection Refused

```bash
# Problem: Cannot connect over WiFi
frameo-cli connect network 192.168.1.100
# Error: Connection refused

# Solution 1: Check if wireless ADB is enabled
# Reconnect via USB and run:
frameo-cli tcpip

# Solution 2: Verify IP address hasn't changed
# Check router DHCP leases

# Solution 3: Restart device
frameo-cli shell "reboot"  # If USB connected
```

### Wireless ADB Disabled After Reboot

```bash
# Some devices disable wireless ADB on reboot
# Quick fix: USB reconnect and enable again
frameo-cli connect usb ABC123DEF456
frameo-cli tcpip
frameo-cli connect network 192.168.1.100
```

### Firewall Issues

```bash
# If API server is on different machine than Frameo
# Ensure port 5555 is not blocked by firewall

# Test connectivity
nc -zv 192.168.1.100 5555
telnet 192.168.1.100 5555
```

### Static IP Recommendation

Set a static IP or DHCP reservation for your Frameo:
1. Log into router
2. Find Frameo's MAC address
3. Create DHCP reservation
4. Now IP address won't change

## Complete WiFi Setup Example

```bash
# === FIRST TIME SETUP ===

# 1. Connect via USB
frameo-cli devices
# Output: ABC123DEF456

frameo-cli connect usb ABC123DEF456
# Output: ✓ Connected to USB device: ABC123DEF456

# 2. Get IP address
frameo-cli shell "ip addr show wlan0 | grep 'inet '"
# Output: inet 192.168.1.100/24

# 3. Enable wireless ADB
frameo-cli tcpip
# Output: ✓ TCP/IP enabled on port 5555

# 4. Disconnect USB cable physically

# 5. Connect wirelessly
frameo-cli connect network 192.168.1.100
# Output: ✓ Connected to network device: 192.168.1.100:5555

# === DAILY USE (NO USB) ===

# Control from anywhere on network
frameo-cli wake
frameo-cli upload family-photos/*.jpg
frameo-cli next
frameo-cli brightness 150
frameo-cli state

# Upload from Python script
import requests
with open('photo.jpg', 'rb') as f:
    requests.post('http://localhost:5000/upload', files={'file': f})

# Scheduled automation works over WiFi
crontab -e
# 0 8 * * * frameo-cli wake
# 0 23 * * * frameo-cli sleep
```

## Summary

✅ **Everything works over WiFi** - All API and CLI features  
✅ **One-time USB setup** - Enable wireless ADB once  
✅ **Remote control** - From anywhere on your network  
✅ **Automation friendly** - Perfect for home automation  
✅ **Fast enough** - Photo uploads work great wirelessly  
✅ **Persistent** - Usually stays enabled across reboots  

**Bottom line**: After the initial USB setup, you can put the USB cable away and control your Frameo entirely over WiFi! 🎉
