"""
Data models for MP3 metadata editor.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Metadata:
    """Represents MP3 metadata."""
    artist: str = ""
    album: str = ""
    year: str = ""
    genre: str = ""
    cover_path: Optional[str] = None


@dataclass
class FileInfo:
    """Represents an MP3 file information."""
    filename: str
    path: str
    metadata: Optional[Metadata] = None