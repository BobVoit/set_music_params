"""
Utility functions for clipboard handling, validation, etc.
"""

import os
import tkinter as tk
from typing import Union


def paste_to_widget(widget, root: tk.Tk) -> bool:
    """
    Paste clipboard content into a widget.
    
    Args:
        widget: Tkinter widget (Entry, Text, etc.)
        root: Root window for clipboard access.
        
    Returns:
        True if paste succeeded, False otherwise.
    """
    try:
        clip = root.clipboard_get()
    except tk.TclError:
        return False
    
    try:
        if hasattr(widget, 'insert') and callable(getattr(widget, 'insert')):
            widget.insert(tk.INSERT, clip)
            return True
    except Exception:
        pass
    
    return False


def copy_from_widget(widget, root: tk.Tk) -> bool:
    """
    Copy selected text from widget to clipboard.
    
    Args:
        widget: Tkinter widget.
        root: Root window.
        
    Returns:
        True if copy succeeded, False otherwise.
    """
    try:
        # Try to get selected text
        try:
            txt = widget.selection_get()
        except Exception:
            # If no selection, get all text
            txt = widget.get()
        
        root.clipboard_clear()
        root.clipboard_append(txt)
        return True
    except Exception:
        return False


def cut_from_widget(widget, root: tk.Tk) -> bool:
    """
    Cut selected text from widget to clipboard.
    
    Args:
        widget: Tkinter widget.
        root: Root window.
        
    Returns:
        True if cut succeeded, False otherwise.
    """
    try:
        # Try to get selected text
        try:
            txt = widget.selection_get()
            start = widget.index(tk.SEL_FIRST)
            end = widget.index(tk.SEL_LAST)
            widget.delete(start, end)
        except Exception:
            # If no selection, cut all text
            txt = widget.get()
            widget.delete(0, tk.END)
        
        root.clipboard_clear()
        root.clipboard_append(txt)
        return True
    except Exception:
        return False


def validate_year(year_str: str) -> bool:
    """
    Validate year string (should be numeric and reasonable).
    
    Args:
        year_str: Year as string.
        
    Returns:
        True if valid, False otherwise.
    """
    if not year_str:
        return True
    
    if not year_str.isdigit():
        return False
    
    year = int(year_str)
    return 1900 <= year <= 2100


def validate_non_empty(text: str) -> bool:
    """
    Check if text is not empty after stripping whitespace.
    """
    return bool(text.strip())


def validate_image_size(image_path: str, max_size_mb: float = 5.0) -> tuple[bool, str]:
    """
    Check if image file size is within limit.
    
    Args:
        image_path: Path to image file.
        max_size_mb: Maximum size in megabytes.
        
    Returns:
        (is_valid, error_message)
    """
    if not os.path.exists(image_path):
        return False, "Файл не существует"
    
    size_bytes = os.path.getsize(image_path)
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > max_size_mb:
        return False, f"Размер изображения {size_mb:.2f} МБ превышает лимит {max_size_mb} МБ"
    
    return True, ""