"""
Helper utility functions for AutoDub Pro.
"""

import os
import re
import sys
import shutil
import tempfile
import platform
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


def get_temp_dir() -> str:
    """
    Get a temporary directory for AutoDub Pro.
    
    Returns:
        Path to the temporary directory
    """
    temp_dir = os.path.join(tempfile.gettempdir(), "autodub_pro")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def get_user_data_dir() -> str:
    """
    Get the user data directory for AutoDub Pro based on the platform.
    
    Returns:
        Path to the user data directory
    """
    if platform.system() == "Windows":
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:  # Linux and other Unix-like systems
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        
    data_dir = os.path.join(base_dir, "AutoDubPro")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def find_ffmpeg() -> Optional[str]:
    """
    Find the FFmpeg executable on the system.
    
    Returns:
        Path to FFmpeg executable or None if not found
    """
    # First check if it's in PATH
    ffmpeg_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    
    # Check if ffmpeg is in PATH
    for path in os.environ["PATH"].split(os.pathsep):
        ffmpeg_path = os.path.join(path, ffmpeg_name)
        if os.path.isfile(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
            return ffmpeg_path
    
    # If not in PATH, check common locations
    common_locations = []
    
    if platform.system() == "Windows":
        common_locations = [
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            os.path.join(os.path.expanduser("~"), "ffmpeg", "bin", "ffmpeg.exe")
        ]
    elif platform.system() == "Darwin":  # macOS
        common_locations = [
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "/opt/local/bin/ffmpeg"
        ]
    else:  # Linux and other Unix-like systems
        common_locations = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/bin/ffmpeg"
        ]
    
    for location in common_locations:
        if os.path.isfile(location) and os.access(location, os.X_OK):
            return location
    
    return None


def clean_temp_files(directory: Optional[str] = None, file_patterns: Optional[List[str]] = None) -> int:
    """
    Clean temporary files from a directory.
    
    Args:
        directory: Directory to clean (defaults to AutoDub Pro temp directory)
        file_patterns: List of file patterns to match for deletion
        
    Returns:
        Number of files deleted
    """
    if directory is None:
        directory = get_temp_dir()
        
    if file_patterns is None:
        file_patterns = ["*.tmp", "*.temp", "temp_*"]
        
    count = 0
    
    try:
        for pattern in file_patterns:
            for file_path in Path(directory).glob(pattern):
                try:
                    file_path.unlink()
                    count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
                    
        return count
        
    except Exception as e:
        print(f"Error cleaning temp files: {e}")
        return count


def detect_ffmpeg_version() -> Optional[str]:
    """
    Detect the FFmpeg version.
    
    Returns:
        FFmpeg version string or None if not found
    """
    ffmpeg_path = find_ffmpeg()
    
    if ffmpeg_path is None:
        return None
        
    try:
        import subprocess
        result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True)
        
        # Extract version from output
        match = re.search(r"ffmpeg version (\S+)", result.stdout)
        
        if match:
            return match.group(1)
            
        return result.stdout.split('\n')[0]
        
    except Exception as e:
        print(f"Error detecting FFmpeg version: {e}")
        return None


def format_time(seconds: float) -> str:
    """
    Format a time in seconds to HH:MM:SS.mmm format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def parse_time(time_str: str) -> Optional[float]:
    """
    Parse a time string in various formats to seconds.
    
    Args:
        time_str: Time string in format HH:MM:SS.mmm, MM:SS.mmm, or SS.mmm
        
    Returns:
        Time in seconds or None if parsing fails
    """
    try:
        # Try HH:MM:SS.mmm format
        if time_str.count(':') == 2:
            hours, minutes, seconds = time_str.split(':')
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            
        # Try MM:SS.mmm format
        elif time_str.count(':') == 1:
            minutes, seconds = time_str.split(':')
            return int(minutes) * 60 + float(seconds)
            
        # Try SS.mmm format
        else:
            return float(time_str)
            
    except Exception as e:
        print(f"Error parsing time: {e}")
        return None


def is_ffmpeg_available() -> bool:
    """
    Check if FFmpeg is available on the system.
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    return find_ffmpeg() is not None


def create_unique_filename(base_dir: str, base_name: str, extension: str) -> str:
    """
    Create a unique filename by appending a number if needed.
    
    Args:
        base_dir: Directory for the file
        base_name: Base filename
        extension: File extension
        
    Returns:
        Unique filename
    """
    # Make sure extension starts with a dot
    if not extension.startswith('.'):
        extension = '.' + extension
        
    # First try the original name
    file_path = os.path.join(base_dir, f"{base_name}{extension}")
    
    # If it exists, add numbers
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(base_dir, f"{base_name}_{counter}{extension}")
        counter += 1
        
    return file_path


def copy_with_metadata(src_path: str, dest_path: str) -> bool:
    """
    Copy a file while preserving metadata.
    
    Args:
        src_path: Source file path
        dest_path: Destination file path
        
    Returns:
        True if copying was successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        
        # Copy the file with metadata
        shutil.copy2(src_path, dest_path)
        
        return True
        
    except Exception as e:
        print(f"Error copying file: {e}")
        return False 