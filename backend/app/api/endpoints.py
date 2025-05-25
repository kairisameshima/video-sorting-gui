from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import os
from pathlib import Path

from ..models.video import (
    VideoFile, SourceFolder, DestinationFolders, 
    FileOperation, FileOperationResult, VideoScreenshots, ProgressStatus
)
from ..services.file_service import (
    get_video_files, move_file, skip_file, 
    prepend_hyphen, undo_last_operation, get_operation_progress,
    get_common_directories
)
from ..services.video_service import generate_screenshots, cleanup_screenshots

router = APIRouter()


@router.post("/source-folder", response_model=List[VideoFile])
async def set_source_folder(source_folder: SourceFolder):
    """Set the source folder and return a list of video files."""
    try:
        video_files = get_video_files(source_folder.path)
        return video_files
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting source folder: {str(e)}")


@router.post("/destination-folders", response_model=Dict[str, str])
async def set_destination_folders(folders: DestinationFolders):
    """Set the destination folders mapping."""
    return folders.folders


@router.post("/move-file", response_model=FileOperationResult)
async def move_video_file(operation: FileOperation):
    """Move a video file to a destination folder."""
    if operation.operation_type != "move" or not operation.destination_path:
        raise HTTPException(status_code=400, detail="Invalid operation for move-file")

    try:
        result = await move_file(operation.source_path, operation.destination_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moving file: {str(e)}")


@router.post("/skip-file", response_model=FileOperationResult)
async def skip_video_file(operation: FileOperation):
    """Add a video file to the skip list."""
    if operation.operation_type != "skip":
        raise HTTPException(status_code=400, detail="Invalid operation for skip-file")

    try:
        result = skip_file(operation.source_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error skipping file: {str(e)}")


@router.post("/prepend-hyphen", response_model=FileOperationResult)
async def prepend_hyphen_to_file(operation: FileOperation):
    """Prepend a hyphen to a filename."""
    if operation.operation_type != "rename":
        raise HTTPException(status_code=400, detail="Invalid operation for prepend-hyphen")

    try:
        result = prepend_hyphen(operation.source_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renaming file: {str(e)}")


@router.post("/undo", response_model=Optional[FileOperationResult])
async def undo_operation():
    """Undo the last file operation."""
    try:
        result = undo_last_operation()
        if result is None:
            return JSONResponse(content={"message": "No operations to undo"}, status_code=200)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error undoing operation: {str(e)}")


@router.get("/progress/{operation_id}", response_model=Optional[ProgressStatus])
async def get_progress(operation_id: str):
    """Get the progress of a file operation."""
    progress = get_operation_progress(operation_id)
    if progress is None:
        raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")
    return progress


@router.post("/screenshots", response_model=Optional[VideoScreenshots])
async def get_video_screenshots(
    video_path: str, 
    num_screenshots: int = 3
):
    """Generate screenshots from a video file."""
    try:
        screenshots = await generate_screenshots(video_path, num_screenshots)
        if screenshots is None:
            raise HTTPException(status_code=404, detail=f"Could not generate screenshots for {video_path}")

        return screenshots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating screenshots: {str(e)}")


@router.get("/common-directories", response_model=List[SourceFolder])
async def get_directories():
    """Get a list of common directories on macOS that might contain video files."""
    try:
        return get_common_directories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting common directories: {str(e)}")
