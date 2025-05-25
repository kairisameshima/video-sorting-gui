import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))

# FFMPEG configuration
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

# Application directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Logs directory
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "file_operations.log"

# CORS configuration
CORS_ORIGINS = [
    f"http://{os.getenv('FRONTEND_HOST', 'localhost')}:{os.getenv('FRONTEND_PORT', '3000')}",
    "http://localhost:3000",
]

# Video file extensions
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]
