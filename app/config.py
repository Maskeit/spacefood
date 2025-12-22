"""
Configuration file for OCR processing system.
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "app" / "data"
RESULT_DIR = PROJECT_ROOT / "app" / "data_result"

# Supported file types
SUPPORTED_FORMATS = [".pdf"]

# Logging
LOG_LEVEL = "INFO"
