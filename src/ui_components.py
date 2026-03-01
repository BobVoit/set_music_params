"""
Custom UI components for the MP3 Metadata Editor.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ProgressDialog:
    """A simple progress dialog for long operations."""
    
    def __init__(self, parent, title="Processing", width=400, height=100):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.update_idletasks()
        p_x = parent.winfo_x()
        p_y = parent.winfo_y()
        p_width = parent.winfo_width()
        p_height = parent.winfo_height()
        d_width = self.dialog.winfo_width()
        d_height = self.dialog.winfo_height()
        x = p_x + (p_width - d_width) // 2
        y = p_y + (p_height - d_height) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Label
        self.label = ttk.Label(self.dialog, text="Processing...")
        self.label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.dialog, mode='determinate')
        self.progress.pack(pady=10, padx=20, fill=tk.X)
        
        # Cancel button
        self.cancel_button = ttk.Button(self.dialog, text="Cancel", command=self.cancel)
        self.cancel_button.pack(pady=5)
        self.cancelled = False
        
    def update(self, value: int, maximum: int = 100, text: str = None):
        """Update progress bar and label."""
        self.progress['maximum'] = maximum
        self.progress['value'] = value
        if text:
            self.label.config(text=text)
        self.dialog.update()
    
    def cancel(self):
        """Set cancelled flag and close."""
        self.cancelled = True
        self.dialog.destroy()
    
    def close(self):
        """Close the dialog."""
        self.dialog.destroy()


class ValidatedEntry(ttk.Entry):
    """Entry with validation for year field."""
    
    def __init__(self, parent, validate_type='year', **kwargs):
        super().__init__(parent, **kwargs)
        self.validate_type = validate_type
        
        if validate_type == 'year':
            vcmd = (self.register(self._validate_year), '%P')
            self.config(validate='key', validatecommand=vcmd)
    
    def _validate_year(self, new_value):
        if not new_value:
            return True
        if new_value.isdigit():
            year = int(new_value)
            return 1900 <= year <= 2100
        return False


class CoverPreview(ttk.Frame):
    """Widget for displaying a cover image preview."""
    
    def __init__(self, parent, max_size=(150, 150), **kwargs):
        super().__init__(parent, **kwargs)
        self.max_size = max_size
        self.image = None
        self.photo = None
        
        self.label = ttk.Label(self, text="Обложка не выбрана", foreground="gray")
        self.label.pack()
        
        self.image_label = ttk.Label(self)
        self.image_label.pack()
    
    def set_image(self, image_path):
        """Load and display image from path."""
        try:
            img = Image.open(image_path)
            img.thumbnail(self.max_size, Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo)
            self.label.config(text="")
        except Exception as e:
            self.label.config(text=f"Ошибка загрузки: {e}", foreground="red")
            self.image_label.config(image='')
    
    def clear(self):
        """Clear preview."""
        self.label.config(text="Обложка не выбрана", foreground="gray")
        self.image_label.config(image='')