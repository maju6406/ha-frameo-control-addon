# Building and Publishing Frameo Control API

This guide explains how to build and publish the Frameo Control API package.

## Prerequisites

```bash
pip install build twine
```

## Building the Package

### 1. Update Version

Edit `src/frameo_control/__init__.py` and `pyproject.toml` to update the version number following semantic versioning.

### 2. Build Distribution Files

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Build wheel and source distribution
python -m build
```

This creates:
- `dist/frameo_control-X.Y.Z-py3-none-any.whl` (wheel package)
- `dist/frameo-control-X.Y.Z.tar.gz` (source distribution)

### 3. Verify the Build

```bash
# Check package contents
tar -tzf dist/frameo-control-*.tar.gz

# Install locally to test
pip install dist/frameo_control-*.whl

# Test commands
frameo-api --help
frameo-cli --help
```

## Publishing to PyPI

### Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ frameo-control
```

### Publish to PyPI

```bash
# Upload to PyPI (requires PyPI account and API token)
twine upload dist/*
```

### Configure PyPI Credentials

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-API-TOKEN
```

## Post-Publication

After publishing:

1. **Tag the release in git:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create GitHub Release:**
   - Go to GitHub releases
   - Create new release from tag
   - Add release notes

3. **Update documentation:**
   - Verify install instructions work
   - Update any version references

4. **Test installation:**
   ```bash
   pip install frameo-control
   frameo-cli --version
   ```

## Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backward compatible)
- **PATCH** version: Bug fixes (backward compatible)

## Build Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `src/frameo_control/__init__.py`
- [ ] Update version in `src/frameo_control/cli.py` (VERSION constant)
- [ ] Update CHANGELOG (if exists)
- [ ] Run tests
- [ ] Clean previous builds
- [ ] Build package
- [ ] Test installation locally
- [ ] Upload to TestPyPI
- [ ] Test from TestPyPI
- [ ] Upload to PyPI
- [ ] Create git tag
- [ ] Create GitHub release
- [ ] Verify installation from PyPI

## Troubleshooting

### "File already exists" error
- You're trying to upload a version that already exists
- Increment the version number

### Import errors after installation
- Check `pyproject.toml` [tool.setuptools.packages.find] configuration
- Verify package structure with `python -m build --sdist` and inspect contents

### Missing dependencies
- Ensure all dependencies are listed in `pyproject.toml` dependencies
- Test in a clean virtual environment
