# Package Structure Migration

## What Changed

The project has been restructured as a proper Python package that can be installed via pip.

## Old vs New Structure

### Old Structure (Standalone Scripts)
```
├── app.py                    # API server script
├── frameo-cli.py            # CLI script
├── requirements.txt         # API dependencies
└── cli-requirements.txt     # CLI dependencies
```

### New Structure (Python Package)
```
├── src/
│   └── frameo_control/
│       ├── __init__.py      # Package initialization
│       ├── api.py           # API server (was app.py)
│       └── cli.py           # CLI tool (was frameo-cli.py)
├── pyproject.toml           # Package metadata & dependencies
├── MANIFEST.in              # Files to include in distribution
└── PUBLISHING.md            # Build & publish guide
```

## Installation Methods

### Option 1: Install from PyPI (Future)
```bash
pip install frameo-control
```

### Option 2: Install from Source
```bash
git clone https://github.com/maju6406/frameo-control-api.git
cd frameo-control-api
pip install -e .
```

### Option 3: Docker (Unchanged workflow)
```bash
docker-compose up -d
```

## Command Changes

### Old Way (Running Scripts)
```bash
# API server
python3 app.py

# CLI
python3 frameo-cli.py devices
./frameo-cli.py devices
```

### New Way (Installed Commands)
```bash
# API server
frameo-api

# CLI
frameo-cli devices
```

## For Developers

### Running in Development Mode

```bash
# Install in editable mode
pip install -e .

# Now you can edit source files and changes take effect immediately
# No need to reinstall after each change
```

### Building the Package

```bash
# Install build tools
pip install build

# Build distribution files
python -m build

# Creates: dist/frameo_control-1.0.0-py3-none-any.whl
#          dist/frameo-control-1.0.0.tar.gz
```

## Benefits of Package Structure

1. **Easy Installation**: `pip install frameo-control`
2. **Proper Dependencies**: Automatically installs required packages
3. **Entry Points**: Get `frameo-api` and `frameo-cli` commands
4. **Version Management**: Proper semantic versioning
5. **Distribution**: Can publish to PyPI for easy sharing
6. **Import as Library**: Other Python code can import frameo_control

## Backward Compatibility

The old `app.py` and `frameo-cli.py` files still exist in the repository root for reference, but the active code is now in `src/frameo_control/`.

Docker builds and docker-compose configurations have been updated to use the new package structure automatically.

## Migration Path

### For Users
1. Pull latest changes
2. Rebuild Docker images: `docker-compose build`
3. Or install locally: `pip install -e .`
4. Use new commands: `frameo-api` and `frameo-cli`

### For Contributors
1. Code is now in `src/frameo_control/`
2. Edit `api.py` and `cli.py` in that location
3. Dependencies go in `pyproject.toml`
4. Test with `pip install -e .` then run commands
