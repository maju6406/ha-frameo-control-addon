#!/bin/bash
# Install Frameo CLI tool

set -e

echo "🔧 Installing Frameo CLI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r cli-requirements.txt

# Make CLI executable
chmod +x frameo-cli.py

# Create symlink in user's bin directory
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# Get absolute path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_PATH="$SCRIPT_DIR/frameo-cli.py"

# Create symlink
ln -sf "$CLI_PATH" "$BIN_DIR/frameo-cli"

echo "✓ Frameo CLI installed successfully!"
echo ""
echo "📝 Usage:"
echo "  frameo-cli --help         Show help"
echo "  frameo-cli devices        List USB devices"
echo "  frameo-cli connect usb <serial>"
echo "  frameo-cli wake           Wake device"
echo "  frameo-cli next           Next photo"
echo ""
echo "💡 Make sure $BIN_DIR is in your PATH"
echo "   Add this to your ~/.bashrc or ~/.zshrc:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
