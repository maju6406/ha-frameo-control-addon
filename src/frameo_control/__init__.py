"""
Frameo Control API - Control Frameo digital photo frames via ADB

This package provides both a REST API server and a command-line interface
for controlling Frameo digital photo frames over USB or network connections.
"""

__version__ = "0.1.0"
__author__ = "Frameo Control Contributors"
__license__ = "MIT"

from frameo_control.api import app
from frameo_control.cli import main as cli_main

__all__ = ["app", "cli_main", "__version__"]
