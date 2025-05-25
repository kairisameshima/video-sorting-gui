# Video Sorting GUI

A video sorting application with a React frontend and FastAPI backend. This application helps you sort and organize video files by allowing you to:

- Select a source folder containing videos
- Define destination folders with shorthand keys
- View video previews with screenshots generated using ffmpeg
- Move videos to destination folders with a single click
- Skip videos you don't want to sort
- Prepend hyphens to filenames
- Undo file operations

## Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- ffmpeg (must be installed and available in your PATH)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/video-sorting-gui.git
cd video-sorting-gui
```

### 2. Set up the backend

The backend uses Poetry for dependency management. If you don't have Poetry installed, you can install it following the instructions at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).

```bash
# Install dependencies
poetry install

# Create a virtual environment in the project folder
poetry config virtualenvs.in-project true
poetry shell
```

### 3. Set up the frontend

```bash
cd frontend
npm install
```

> **Important**: This step is crucial. If you skip it, you'll encounter a "react-scripts: command not found" error when trying to start the frontend.

## Configuration

The application uses a `.env` file for configuration. You can modify the following variables:

```
API_HOST=localhost
API_PORT=8000
FRONTEND_HOST=localhost
FRONTEND_PORT=3000
# Path to ffmpeg binary (if not in PATH)
# FFMPEG_PATH=/path/to/ffmpeg
```

## Running the Application

### 1. Start the backend server

From the project root directory:

```bash
cd backend
python run.py
```

The API will be available at http://localhost:8000.

### 2. Start the frontend development server

In a new terminal, from the project root directory:

```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000.

## Usage

1. **Select Source Folder**: Enter the full path to the folder containing the videos you want to sort.

2. **Define Destination Folders**: Create a mapping of shorthand keys to destination folders. For example:
   - A -> /path/to/action/movies
   - C -> /path/to/comedy/movies
   - D -> /path/to/drama/movies

3. **Sort Videos**: Once you've set up the source and destination folders, you'll see the videos one by one with screenshots. You can:
   - Click on a destination folder button to move the video
   - Click "Skip" to skip the current video
   - Click "Prepend Hyphen" to add a hyphen to the beginning of the filename
   - Click "Undo" to undo the last operation

## Development

### Backend Structure

- `backend/app/`: Main application package
  - `api/`: API endpoints
  - `core/`: Core configuration
  - `models/`: Pydantic models
  - `services/`: Business logic services

### Frontend Structure

- `frontend/src/`: Source code
  - `api/`: API client
  - `components/`: React components
  - `App.js`: Main application component

## License

MIT
