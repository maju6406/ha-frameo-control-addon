# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-05

### Added
- Initial release as pip-installable Python package
- REST API server for controlling Frameo digital photo frames via ADB
- Command-line interface (CLI) tool with comprehensive commands
- Support for USB and network (WiFi) connections
- Device discovery and connection management
- Screen control (wake, sleep, brightness)
- Touch input simulation (tap, swipe)
- Key event injection (home, back, navigation)
- Frameo app control (open, restart, force-stop)
- Screenshot capture
- File upload and download
- Shell command execution
- Device state monitoring
- Wireless ADB (tcpip) support
- Docker container support with USB device access
- Comprehensive API documentation (OpenAPI/Swagger)
- CLI documentation and examples
- WiFi setup guide

### Changed
- Rebranded from `ha-frameo-control-addon` to `frameo-control-api`
- Restructured as proper Python package under `src/frameo_control/`
- Updated all documentation to reflect standalone nature
- Removed Home Assistant-specific branding
- Enhanced multi-platform automation support

### Package Structure
- Entry points: `frameo-api` and `frameo-cli` commands
- Proper dependency management via `pyproject.toml`
- Pip-installable: `pip install frameo-control`
- Development mode support: `pip install -e .`

[0.1.0]: https://github.com/maju6406/frameo-control-api/releases/tag/v0.1.0
