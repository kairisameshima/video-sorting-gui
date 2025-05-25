import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import asyncio
import ffmpeg
import logging

from ..core.config import TEMP_DIR, VIDEO_EXTENSIONS, LOG_FILE
from ..models.video import VideoFile, FileOperation, FileOperationResult, SourceFolder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add file handler for logging file operations
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# In-memory storage for operation history and skipped files
operation_history: List[FileOperation] = []
skipped_files: List[str] = []


def is_video_file(file_path: Path) -> bool:
    """Check if a file is a video file based on its extension."""
    return file_path.suffix.lower() in VIDEO_EXTENSIONS


def get_video_files(folder_path: str) -> List[VideoFile]:
    """Get all video files in a folder and sort them by modification time (newest first)."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Invalid folder path: {folder_path}")

    video_files = []
    for file_path in folder.iterdir():
        # Skip files that start with "._"
        if file_path.name.startswith("._"):
            logger.info(f"Skipping file that starts with '._': {file_path.name}")
            continue

        if file_path.is_file() and is_video_file(file_path):
            # Get file modification time
            mtime = file_path.stat().st_mtime

            video_files.append(VideoFile(
                path=str(file_path),
                name=file_path.stem,
                extension=file_path.suffix,
                size=file_path.stat().st_size,
                timestamp=mtime
            ))

    # Sort videos by timestamp (newest first)
    video_files.sort(key=lambda x: x.timestamp if x.timestamp is not None else 0, reverse=True)

    return video_files


async def move_file(source_path: str, destination_path: str, prepend_hyphen_first: bool = False) -> FileOperationResult:
    """Move a file from source to destination. Optionally prepend a hyphen before moving."""
    operation_id = str(uuid.uuid4())
    source = Path(source_path)
    destination = Path(destination_path)

    # Create destination directory if it doesn't exist
    destination.parent.mkdir(parents=True, exist_ok=True)

    # If prepend_hyphen_first is True, modify the destination filename
    if prepend_hyphen_first:
        destination = destination.parent / f"-{destination.name}"
        logger.info(f"Will prepend hyphen before moving: {destination.name}")

    operation = FileOperation(
        source_path=source_path,
        destination_path=str(destination),
        operation_type="move"
    )

    try:
        # Log the file movement operation
        logger.info(f"Moving file: {source} -> {destination}")

        # For large files, we'll copy and then delete the original
        shutil.copy2(source, destination)

        # Delete the original file
        os.remove(source)

        # Update operation history
        operation_history.append(operation)

        # Log successful completion
        logger.info(f"File moved successfully: {source} -> {destination}")

        return FileOperationResult(
            success=True,
            message=f"File moved successfully from {source} to {destination}",
            operation=operation
        )

    except Exception as e:
        logger.error(f"Error moving file: {source} -> {destination}: {str(e)}")

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
            # Log the skip operation
            logger.info(f"Skipping file: {file_path}")

        # Update operation history
        operation_history.append(operation)

        return FileOperationResult(
            success=True,
            message=f"File {file_path} added to skip list",
            operation=operation
        )

    except Exception as e:
        logger.error(f"Error skipping file: {file_path}: {str(e)}")
        return FileOperationResult(
            success=False,
            message=f"Error skipping file: {str(e)}",
            operation=operation
        )


def prepend_hyphen(file_path: str) -> FileOperationResult:
    """Prepend a hyphen to a filename."""
    source = Path(file_path)

    if not source.exists():
        logger.error(f"File does not exist: {file_path}")
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
        # Log the rename operation
        logger.info(f"Renaming file: {source.name} -> {new_name}")

        # Rename the file
        source.rename(destination)

        # Update operation history
        operation_history.append(operation)

        # Log successful completion
        logger.info(f"File renamed successfully: {source.name} -> {new_name}")

        return FileOperationResult(
            success=True,
            message=f"File renamed from {source.name} to {new_name}",
            operation=operation
        )

    except Exception as e:
        logger.error(f"Error renaming file: {source.name} -> {new_name}: {str(e)}")
        return FileOperationResult(
            success=False,
            message=f"Error renaming file: {str(e)}",
            operation=operation
        )


def undo_last_operation() -> Optional[FileOperationResult]:
    """Undo the last file operation."""
    if not operation_history:
        logger.info("No operations to undo")
        return None

    last_operation = operation_history.pop()
    logger.info(f"Undoing last operation: {last_operation.operation_type} on {last_operation.source_path}")

    try:
        if last_operation.operation_type == "move":
            # Move the file back to its original location
            source = Path(last_operation.destination_path)
            destination = Path(last_operation.source_path)

            # Create parent directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Log the undo move operation
            logger.info(f"Undoing move: {source} -> {destination}")

            # Move the file
            shutil.move(source, destination)

            # Log successful completion
            logger.info(f"File moved back successfully: {source} -> {destination}")

            return FileOperationResult(
                success=True,
                message=f"Moved file back from {source} to {destination}",
                operation=last_operation
            )

        elif last_operation.operation_type == "skip":
            # Remove from skipped files
            if last_operation.source_path in skipped_files:
                skipped_files.remove(last_operation.source_path)
                # Log the undo skip operation
                logger.info(f"Undoing skip: Removed {last_operation.source_path} from skip list")

            return FileOperationResult(
                success=True,
                message=f"Removed {last_operation.source_path} from skip list",
                operation=last_operation
            )

        elif last_operation.operation_type == "rename":
            # Rename the file back
            source = Path(last_operation.destination_path)
            destination = Path(last_operation.source_path)

            # Log the undo rename operation
            logger.info(f"Undoing rename: {source.name} -> {destination.name}")

            # Rename the file
            source.rename(destination)

            # Log successful completion
            logger.info(f"File renamed back successfully: {source.name} -> {destination.name}")

            return FileOperationResult(
                success=True,
                message=f"Renamed file back from {source.name} to {destination.name}",
                operation=last_operation
            )

        else:
            logger.error(f"Unknown operation type: {last_operation.operation_type}")
            return FileOperationResult(
                success=False,
                message=f"Unknown operation type: {last_operation.operation_type}",
                operation=last_operation
            )

    except Exception as e:
        logger.error(f"Error undoing operation: {last_operation.operation_type} on {last_operation.source_path}: {str(e)}")
        # Put the operation back in history since it wasn't undone
        operation_history.append(last_operation)

        return FileOperationResult(
            success=False,
            message=f"Error undoing operation: {str(e)}",
            operation=last_operation
        )




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
