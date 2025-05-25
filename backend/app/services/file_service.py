import os
import shutil
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import asyncio
import ffmpeg
import logging

from ..core.config import TEMP_DIR, VIDEO_EXTENSIONS
from ..models.video import VideoFile, FileOperation, FileOperationResult, ProgressStatus, SourceFolder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for operation history and skipped files
operation_history: List[FileOperation] = []
skipped_files: List[str] = []
operation_progress: Dict[str, ProgressStatus] = {}


def is_video_file(file_path: Path) -> bool:
    """Check if a file is a video file based on its extension."""
    return file_path.suffix.lower() in VIDEO_EXTENSIONS


def get_video_files(folder_path: str) -> List[VideoFile]:
    """Get all video files in a folder."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path}")

    video_files = []
    for file_path in folder.iterdir():
        if file_path.is_file() and is_video_file(file_path):
            video_files.append(VideoFile(
                path=str(file_path),
                name=file_path.stem,
                extension=file_path.suffix,
                size=file_path.stat().st_size
            ))

    return video_files


async def move_file(source_path: str, destination_path: str) -> FileOperationResult:
    """Move a file from source to destination with progress tracking."""
    operation_id = str(uuid.uuid4())
    source = Path(source_path)
    destination = Path(destination_path)

    # Create destination directory if it doesn't exist
    destination.parent.mkdir(parents=True, exist_ok=True)

    operation = FileOperation(
        source_path=source_path,
        destination_path=destination_path,
        operation_type="move"
    )

    try:
        # Start progress tracking
        operation_progress[operation_id] = ProgressStatus(
            operation_id=operation_id,
            progress=0.0,
            status="in_progress",
            message=f"Moving {source.name} to {destination.parent}"
        )

        # For large files, we'll copy with progress tracking and then delete the original
        total_size = source.stat().st_size
        copied_size = 0

        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            while True:
                # Read in chunks of 1MB
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break

                dst.write(chunk)
                copied_size += len(chunk)

                # Update progress
                progress = min(copied_size / total_size, 1.0)
                operation_progress[operation_id].progress = progress

                # Allow other tasks to run
                await asyncio.sleep(0.01)

        # Delete the original file
        os.remove(source)

        # Update operation history
        operation_history.append(operation)

        # Update progress status
        operation_progress[operation_id].progress = 1.0
        operation_progress[operation_id].status = "completed"
        operation_progress[operation_id].message = f"Moved {source.name} to {destination.parent}"

        return FileOperationResult(
            success=True,
            message=f"File moved successfully from {source} to {destination}",
            operation=operation
        )

    except Exception as e:
        logger.error(f"Error moving file: {str(e)}")

        # Update progress status
        operation_progress[operation_id].status = "failed"
        operation_progress[operation_id].message = f"Failed to move {source.name}: {str(e)}"

        return FileOperationResult(
            success=False,
            message=f"Error moving file: {str(e)}",
            operation=operation
        )


def skip_file(file_path: str) -> FileOperationResult:
    """Add a file to the skip list."""
    operation = FileOperation(
        source_path=file_path,
        operation_type="skip"
    )

    try:
        # Add to skipped files if not already there
        if file_path not in skipped_files:
            skipped_files.append(file_path)

        # Update operation history
        operation_history.append(operation)

        return FileOperationResult(
            success=True,
            message=f"File {file_path} added to skip list",
            operation=operation
        )

    except Exception as e:
        logger.error(f"Error skipping file: {str(e)}")
        return FileOperationResult(
            success=False,
            message=f"Error skipping file: {str(e)}",
            operation=operation
        )


def prepend_hyphen(file_path: str) -> FileOperationResult:
    """Prepend a hyphen to a filename."""
    source = Path(file_path)

    if not source.exists():
        return FileOperationResult(
            success=False,
            message=f"File {file_path} does not exist",
            operation=FileOperation(
                source_path=file_path,
                operation_type="rename"
            )
        )

    new_name = f"-{source.name}"
    destination = source.parent / new_name

    operation = FileOperation(
        source_path=str(source),
        destination_path=str(destination),
        operation_type="rename"
    )

    try:
        # Rename the file
        source.rename(destination)

        # Update operation history
        operation_history.append(operation)

        return FileOperationResult(
            success=True,
            message=f"File renamed from {source.name} to {new_name}",
            operation=operation
        )

    except Exception as e:
        logger.error(f"Error renaming file: {str(e)}")
        return FileOperationResult(
            success=False,
            message=f"Error renaming file: {str(e)}",
            operation=operation
        )


def undo_last_operation() -> Optional[FileOperationResult]:
    """Undo the last file operation."""
    if not operation_history:
        return None

    last_operation = operation_history.pop()

    try:
        if last_operation.operation_type == "move":
            # Move the file back to its original location
            source = Path(last_operation.destination_path)
            destination = Path(last_operation.source_path)

            # Create parent directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(source, destination)

            return FileOperationResult(
                success=True,
                message=f"Moved file back from {source} to {destination}",
                operation=last_operation
            )

        elif last_operation.operation_type == "skip":
            # Remove from skipped files
            if last_operation.source_path in skipped_files:
                skipped_files.remove(last_operation.source_path)

            return FileOperationResult(
                success=True,
                message=f"Removed {last_operation.source_path} from skip list",
                operation=last_operation
            )

        elif last_operation.operation_type == "rename":
            # Rename the file back
            source = Path(last_operation.destination_path)
            destination = Path(last_operation.source_path)

            # Rename the file
            source.rename(destination)

            return FileOperationResult(
                success=True,
                message=f"Renamed file back from {source.name} to {destination.name}",
                operation=last_operation
            )

        else:
            return FileOperationResult(
                success=False,
                message=f"Unknown operation type: {last_operation.operation_type}",
                operation=last_operation
            )

    except Exception as e:
        logger.error(f"Error undoing operation: {str(e)}")
        # Put the operation back in history since it wasn't undone
        operation_history.append(last_operation)

        return FileOperationResult(
            success=False,
            message=f"Error undoing operation: {str(e)}",
            operation=last_operation
        )


def get_operation_progress(operation_id: str) -> Optional[ProgressStatus]:
    """Get the progress of a file operation."""
    return operation_progress.get(operation_id)


def get_common_directories() -> List[SourceFolder]:
    """Get a list of common directories on macOS that might contain video files."""
    home_dir = os.path.expanduser("~")
    common_dirs = [
        SourceFolder(path=home_dir),
        SourceFolder(path=os.path.join(home_dir, "Desktop")),
        SourceFolder(path=os.path.join(home_dir, "Documents")),
        SourceFolder(path=os.path.join(home_dir, "Downloads")),
        SourceFolder(path=os.path.join(home_dir, "Movies")),
        SourceFolder(path=os.path.join(home_dir, "Pictures")),
        SourceFolder(path=os.path.join(home_dir, "Videos")),
    ]

    # Add mounted volumes (external drives, etc.)
    volumes_dir = "/Volumes"
    if os.path.exists(volumes_dir) and os.path.isdir(volumes_dir):
        for volume in os.listdir(volumes_dir):
            volume_path = os.path.join(volumes_dir, volume)
            if os.path.isdir(volume_path) and volume != "Macintosh HD":
                common_dirs.append(SourceFolder(path=volume_path))

    return common_dirs
