from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path


class VideoFile(BaseModel):
    """Model representing a video file."""
    path: str
    name: str
    extension: str
    size: int
    
    class Config:
        json_encoders = {
            Path: lambda v: str(v)
        }


class SourceFolder(BaseModel):
    """Model representing a source folder for videos."""
    path: str


class DestinationFolder(BaseModel):
    """Model representing a destination folder for videos."""
    shorthand: str
    path: str


class DestinationFolders(BaseModel):
    """Model representing a dictionary of destination folders."""
    folders: Dict[str, str]


class FileOperation(BaseModel):
    """Model representing a file operation."""
    source_path: str
    destination_path: Optional[str] = None
    operation_type: str  # "move", "skip", "rename"


class FileOperationResult(BaseModel):
    """Model representing the result of a file operation."""
    success: bool
    message: str
    operation: FileOperation


class VideoScreenshots(BaseModel):
    """Model representing screenshots of a video."""
    video_path: str
    screenshot_paths: List[str]


class ProgressStatus(BaseModel):
    """Model representing the progress of a file operation."""
    operation_id: str
    progress: float  # 0.0 to 1.0
    status: str  # "in_progress", "completed", "failed"
    message: Optional[str] = None