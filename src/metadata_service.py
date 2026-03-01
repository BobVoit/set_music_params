"""
Service for reading and writing MP3 metadata using mutagen.
"""

import os
from pathlib import Path
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from .models import Metadata


class MetadataService:
    """Service for MP3 metadata operations."""
    
    _cover_cache = {}  # path -> image_data cache


class MetadataService:
    """Service for MP3 metadata operations."""
    
    @staticmethod
    def load_metadata(file_path: str) -> Metadata:
        """
        Load metadata from an MP3 file.
        
        Args:
            file_path: Path to MP3 file.
            
        Returns:
            Metadata object with loaded fields.
            
        Raises:
            Exception: If file cannot be read or metadata invalid.
        """
        try:
            audio = EasyID3(file_path)
            artist = audio.get('artist', [''])[0]
            album = audio.get('album', [''])[0]
            year = audio.get('date', [''])[0]
            genre = audio.get('genre', [''])[0]
            return Metadata(artist=artist, album=album, year=year, genre=genre)
        except Exception as e:
            raise Exception(f"Failed to load metadata from {file_path}: {str(e)}")
    
    @staticmethod
    def save_metadata(file_path: str, metadata: Metadata, cover_path: Optional[str] = None) -> None:
        """
        Save metadata to an MP3 file.
        
        Args:
            file_path: Path to MP3 file.
            metadata: Metadata object with fields to save.
            cover_path: Optional path to cover image.
            
        Raises:
            Exception: If saving fails.
        """
        try:
            # Load or create EasyID3 tags
            try:
                audio = EasyID3(file_path)
            except:
                audio = EasyID3()
            
            # Update fields if they are not empty
            if metadata.artist:
                audio['artist'] = metadata.artist
            if metadata.album:
                audio['album'] = metadata.album
            if metadata.year:
                audio['date'] = metadata.year
            if metadata.genre:
                audio['genre'] = metadata.genre
            
            audio.save(file_path)
            
            # Handle cover image
            if cover_path:
                MetadataService._save_cover(file_path, cover_path)
                
        except Exception as e:
            raise Exception(f"Failed to save metadata to {file_path}: {str(e)}")
    
    @classmethod
    def _save_cover(cls, file_path: str, cover_path: str) -> None:
        """
        Save cover image to MP3 file.
        
        Args:
            file_path: Path to MP3 file.
            cover_path: Path to cover image.
        """
        # Load image data from cache or file
        if cover_path in cls._cover_cache:
            image_data = cls._cover_cache[cover_path]
        else:
            with open(cover_path, 'rb') as f:
                image_data = f.read()
            cls._cover_cache[cover_path] = image_data
        
        try:
            audio_id3 = ID3(file_path)
        except:
            audio_id3 = ID3()
        
        # Determine MIME type from extension
        ext = Path(cover_path).suffix.lower()
        mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
        
        audio_id3.add(APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=image_data))
        audio_id3.save(file_path, v2_version=3)
    
    @classmethod
    def clear_cover_cache(cls):
        """Clear cached cover images."""
        cls._cover_cache.clear()