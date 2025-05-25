#!/usr/bin/env python3
"""
Video Sorting GUI - Main entry point

This script provides a convenient way to start both the backend and frontend servers.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
api_host = os.getenv("API_HOST", "localhost")
api_port = int(os.getenv("API_PORT", "8000"))
frontend_host = os.getenv("FRONTEND_HOST", "localhost")
frontend_port = int(os.getenv("FRONTEND_PORT", "3000"))

# Project paths
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"


def check_requirements():
    """Check if all requirements are met."""
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        return False

    # Check if ffmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: ffmpeg is not installed or not in PATH.")
        print("Please install ffmpeg and make sure it's available in your PATH.")
        return False

    # Check if Node.js is installed (for frontend)
    try:
        subprocess.run(["node", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: Node.js is not installed. Frontend will not work.")
        print("Please install Node.js to run the frontend.")

    # Check if frontend dependencies are installed
    node_modules_path = FRONTEND_DIR / "node_modules"
    if not node_modules_path.exists():
        print("Warning: Frontend dependencies are not installed.")
        print("Please run 'npm install' in the frontend directory before starting the application.")
        print(f"Command: cd {FRONTEND_DIR} && npm install")

    return True


def start_backend():
    """Start the backend server."""
    print(f"Starting backend server at http://{api_host}:{api_port}...")
    os.chdir(BACKEND_DIR)
    return subprocess.Popen(["python", "run.py"])


def start_frontend():
    """Start the frontend development server."""
    # Check if node_modules exists
    node_modules_path = FRONTEND_DIR / "node_modules"
    if not node_modules_path.exists():
        print(f"Error: Frontend dependencies not installed. Cannot start frontend server.")
        print(f"Please run 'npm install' in the frontend directory first.")
        print(f"Command: cd {FRONTEND_DIR} && npm install")
        return None

    print(f"Starting frontend server at http://{frontend_host}:{frontend_port}...")
    os.chdir(FRONTEND_DIR)
    return subprocess.Popen(["npm", "start"])


def main():
    """Main entry point."""
    if not check_requirements():
        sys.exit(1)

    print("Starting Video Sorting GUI...")

    # Start backend
    backend_process = start_backend()

    # Wait for backend to start
    time.sleep(2)

    # Start frontend
    frontend_process = None
    try:
        frontend_process = start_frontend()

        if frontend_process:
            print("\nVideo Sorting GUI is running!")
            print(f"Backend API: http://{api_host}:{api_port}")
            print(f"Frontend: http://{frontend_host}:{frontend_port}")
            print("\nPress Ctrl+C to stop the servers.")
        else:
            print("\nOnly the backend server is running!")
            print(f"Backend API: http://{api_host}:{api_port}")
            print("\nPlease install frontend dependencies and restart the application to use the frontend.")
            print("\nPress Ctrl+C to stop the server.")

        # Keep the script running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        # Clean up processes
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.terminate()

        print("Servers stopped.")


if __name__ == "__main__":
    main()
