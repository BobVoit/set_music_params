"""
Service for archive operations: extracting archives, handling different archive formats.
"""

import os
import zipfile
import shutil
from pathlib import Path
from typing import Optional, List


class ArchiveService:
    """Service for archive operations."""
    
    @staticmethod
    def is_archive_file(file_path: str) -> bool:
        """
        Check if file is a supported archive format.
        
        Args:
            file_path: Path to file.
            
        Returns:
            True if file is a supported archive, False otherwise.
        """
        supported_extensions = {'.zip', '.rar', '.7z'}
        return Path(file_path).suffix.lower() in supported_extensions
    
    @staticmethod
    def extract_archive(archive_path: str, extract_to: str, create_subdir: bool = True) -> str:
        """
        Extract archive to specified directory.
        
        Args:
            archive_path: Path to archive file.
            extract_to: Base directory to extract to.
            create_subdir: If True, create subdirectory with archive name, 
                          if False, extract directly to extract_to.
            
        Returns:
            Path to the directory where files were extracted.
        """
        archive_path = Path(archive_path)
        extract_to = Path(extract_to)
        
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive file not found: {archive_path}")
        
        # Create extraction directory
        if create_subdir:
            archive_name = archive_path.stem
            extract_dir = extract_to / archive_name
        else:
            extract_dir = extract_to
        
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract based on file extension
        if archive_path.suffix.lower() == '.zip':
            ArchiveService._extract_zip(archive_path, extract_dir)
        else:
            # For other formats, we'll need additional libraries
            # For now, we'll just copy the file as-is if it's not zip
            # In a real implementation, we would use rarfile or py7zr libraries
            shutil.copy2(archive_path, extract_dir)
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
        
        return str(extract_dir)
    
    @staticmethod
    def _extract_zip(zip_path: Path, extract_to: Path):
        """
        Extract ZIP archive.
        
        Args:
            zip_path: Path to ZIP file.
            extract_to: Directory to extract to.
        """
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check for potential path traversal attacks
            for member in zip_ref.namelist():
                member_path = extract_to / member
                if not str(member_path.resolve()).startswith(str(extract_to.resolve())):
                    raise ValueError(f"Archive contains unsafe path: {member}")
            
            zip_ref.extractall(extract_to)
    
    @staticmethod
    def get_default_extract_name(archive_path: str) -> str:
        """
        Get default extraction directory name from archive path.
        
        Args:
            archive_path: Path to archive file.
            
        Returns:
            Suggested directory name for extraction.
        """
        return Path(archive_path).stem