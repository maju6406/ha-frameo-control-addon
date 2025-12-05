#!/bin/bash
# Quick start script for Frameo Control API package

set -e

echo "🚀 Frameo Control API - Quick Start"
echo "===================================="
echo

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $(python3 --version)"
echo

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not in a virtual environment"
    echo "   Consider creating one: python3 -m venv venv && source venv/bin/activate"
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Install the package
echo "📦 Installing frameo-control package..."
pip install -e . -q
echo "✓ Package installed"
echo

# Test the installation
echo "🧪 Testing installation..."
if command -v frameo-api &> /dev/null; then
    echo "✓ frameo-api command available"
else
    echo "❌ frameo-api command not found"
    exit 1
fi

if command -v frameo-cli &> /dev/null; then
    echo "✓ frameo-cli command available"
    FRAMEO_VERSION=$(frameo-cli --version 2>&1 | head -1)
    echo "  $FRAMEO_VERSION"
else
    echo "❌ frameo-cli command not found"
    exit 1
fi
echo

# Show next steps
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo
echo "1. Start the API server:"
echo "   frameo-api"
echo "   (runs on http://localhost:5000)"
echo
echo "2. Or use the CLI tool:"
echo "   frameo-cli devices              # List USB devices"
echo "   frameo-cli connect usb ABC123   # Connect to device"
echo "   frameo-cli state                # Check device state"
echo "   frameo-cli --help               # See all commands"
echo
echo "3. View documentation:"
echo "   cat README.md"
echo "   cat CLI.md"
echo "   cat API.md"
echo
echo "4. For Docker deployment:"
echo "   docker-compose up -d"
echo

# Check for USB devices if libusb is available
if python3 -c "import usb1" 2>/dev/null; then
    echo "💡 Quick device check:"
    echo "   frameo-cli devices"
    echo
fi
