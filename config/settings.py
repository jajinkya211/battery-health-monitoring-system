"""Application configuration settings"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://batteryuser:batterypass@localhost:5432/battery_health_db"
)

# Data directory for uploaded files
DATA_DIR = os.path.join(BASE_DIR, "data")

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Dashboard configuration
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8050"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")