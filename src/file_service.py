"""
Service for file operations: scanning directories, renaming files.
"""

import os
import re
from typing import List
from pathlib import Path


class FileService:
    """Service for file system operations."""
    
    @staticmethod
    def find_mp3_files(directory: str) -> List[str]:
        """
        Find all MP3 files in a directory.
        
        Args:
            directory: Path to directory.
            
        Returns:
            List of MP3 filenames (sorted).
        """
        if not os.path.isdir(directory):
            return []
        
        files = [f for f in os.listdir(directory) if f.lower().endswith('.mp3')]
        files.sort()
        return files
    
    @staticmethod
    def rename_file_without_track_number(file_path: str) -> str:
        """
        Remove leading track number from filename (e.g., "01. Song.mp3" -> "Song.mp3").
        
        Args:
            file_path: Full path to file.
            
        Returns:
            New file path after renaming (or original if no change).
        """
        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        # Pattern: optional whitespace, digits, dot, optional whitespace
        newname = re.sub(r'^\s*\d+\.\s*', '', basename)
        
        if newname and newname != basename:
            newpath = os.path.join(dirname, newname)
            try:
                os.rename(file_path, newpath)
                return newpath
            except Exception:
                # If rename fails, return original path
                return file_path
        
        return file_path
    
    @staticmethod
    def get_file_info(directory: str, filename: str) -> dict:
        """
        Get basic file information.
        
        Args:
            directory: Parent directory.
            filename: Filename.
            
        Returns:
            Dictionary with file info.
        """
        path = os.path.join(directory, filename)
        return {
            'filename': filename,
            'path': path,
            'size': os.path.getsize(path) if os.path.exists(path) else 0,
            'modified': os.path.getmtime(path) if os.path.exists(path) else 0
        }