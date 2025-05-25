import os
import uuid
import subprocess
from pathlib import Path
from typing import List, Optional
import logging
import asyncio

from ..core.config import TEMP_DIR, FFMPEG_PATH
from ..models.video import VideoScreenshots

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_screenshots(video_path: str, num_screenshots: int = 3) -> Optional[VideoScreenshots]:
    """Generate screenshots from a video file."""
    video_path = Path(video_path)
    
    if not video_path.exists() or not video_path.is_file():
        logger.error(f"Video file not found: {video_path}")
        return None
    
    try:
        # Create a unique directory for this video's screenshots
        screenshot_dir = TEMP_DIR / f"screenshots_{uuid.uuid4()}"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Get video duration using ffprobe
        duration_cmd = [
            FFMPEG_PATH.replace("ffmpeg", "ffprobe"),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        
        duration_process = await asyncio.create_subprocess_exec(
            *duration_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await duration_process.communicate()
        
        if duration_process.returncode != 0:
            logger.error(f"Error getting video duration: {stderr.decode()}")
            return None
        
        duration = float(stdout.decode().strip())
        
        # Calculate timestamps for screenshots
        timestamps = []
        if duration > 0:
            interval = duration / (num_screenshots + 1)
            for i in range(1, num_screenshots + 1):
                timestamps.append(interval * i)
        else:
            # Fallback if duration couldn't be determined
            timestamps = [10, 30, 60]
        
        # Generate screenshots
        screenshot_paths = []
        for i, timestamp in enumerate(timestamps):
            if i >= num_screenshots:
                break
                
            output_path = screenshot_dir / f"screenshot_{i+1}.jpg"
            screenshot_paths.append(str(output_path))
            
            # Use ffmpeg to extract frame at timestamp
            cmd = [
                FFMPEG_PATH,
                "-ss", str(timestamp),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            _, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Error generating screenshot: {stderr.decode()}")
        
        # Return the screenshots if any were generated
        if screenshot_paths:
            return VideoScreenshots(
                video_path=str(video_path),
                screenshot_paths=screenshot_paths
            )
        else:
            logger.error(f"No screenshots were generated for {video_path}")
            return None
    
    except Exception as e:
        logger.error(f"Error generating screenshots: {str(e)}")
        return None


def cleanup_screenshots(screenshot_paths: List[str]) -> None:
    """Clean up screenshot files and directories."""
    for path in screenshot_paths:
        try:
            screenshot_path = Path(path)
            if screenshot_path.exists():
                screenshot_path.unlink()
                
            # Try to remove the parent directory if it's empty
            parent_dir = screenshot_path.parent
            if parent_dir.exists() and parent_dir.is_dir() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
        
        except Exception as e:
            logger.error(f"Error cleaning up screenshot: {str(e)}")