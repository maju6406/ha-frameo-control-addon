#!/bin/bash
# Build and test the Frameo Control API package

set -e

echo "🔨 Building Frameo Control API Package"
echo "======================================"
echo

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info
echo "✓ Clean complete"
echo

# Install build tools if needed
echo "📦 Ensuring build tools are installed..."
pip install -q build twine
echo "✓ Build tools ready"
echo

# Build the package
echo "🏗️  Building package..."
python -m build
echo "✓ Build complete"
echo

# Show what was created
echo "📋 Generated files:"
ls -lh dist/
echo

# Validate the package
echo "🔍 Validating package..."
twine check dist/*
echo "✓ Validation complete"
echo

# Show package contents
echo "📦 Package contents:"
tar -tzf dist/frameo-control-*.tar.gz | head -20
echo "... (showing first 20 files)"
echo

echo "✅ Build successful!"
echo
echo "Next steps:"
echo "  • Test locally: pip install dist/frameo_control-*.whl"
echo "  • Test PyPI: twine upload --repository testpypi dist/*"
echo "  • Publish: twine upload dist/*"
