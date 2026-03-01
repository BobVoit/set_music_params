"""
Main window of MP3 Metadata Editor.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path

from .models import Metadata
from .metadata_service import MetadataService
from .file_service import FileService
from .utils import paste_to_widget, copy_from_widget, cut_from_widget, validate_year, validate_image_size
from .ui_components import ProgressDialog, CoverPreview


class MainWindow:
    """Main application window."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Metadata Editor")
        self.root.geometry("900x700")
        
        self.current_dir = None
        self.mp3_files = []
        self.current_file_index = 0
        self.current_metadata = Metadata()
        self.cover_image_path = None
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        """Create and layout UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Выбор директории")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_label = ttk.Label(dir_frame, text="Директория не выбрана", foreground="gray")
        self.dir_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(dir_frame, text="Выбрать директорию", command=self.select_directory).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # MP3 files list
        files_frame = ttk.LabelFrame(main_frame, text="MP3 файлы")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(files_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(files_frame, yscrollcommand=scrollbar.set, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_listbox.yview)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Metadata frame
        metadata_frame = ttk.LabelFrame(main_frame, text="Метаданные")
        metadata_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Artist
        ttk.Label(metadata_frame, text="Исполнитель:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.artist_entry = ttk.Entry(metadata_frame, width=50)
        self.artist_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Album
        ttk.Label(metadata_frame, text="Альбом:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.album_entry = ttk.Entry(metadata_frame, width=50)
        self.album_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Year
        ttk.Label(metadata_frame, text="Год выпуска:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.year_entry = ttk.Entry(metadata_frame, width=50)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Genre
        ttk.Label(metadata_frame, text="Жанр:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.genre_entry = ttk.Entry(metadata_frame, width=50)
        self.genre_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Cover
        ttk.Label(metadata_frame, text="Обложка:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        
        cover_container = ttk.Frame(metadata_frame)
        cover_container.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Left side: button and label
        left_frame = ttk.Frame(cover_container)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.cover_label = ttk.Label(left_frame, text="Не выбрана", foreground="gray")
        self.cover_label.pack(pady=(0, 5))
        ttk.Button(left_frame, text="Выбрать обложку", command=self.select_cover).pack()
        
        # Right side: preview
        right_frame = ttk.Frame(cover_container)
        right_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        self.cover_preview = CoverPreview(right_frame, max_size=(120, 120))
        self.cover_preview.pack()
        
        # Remove track number checkbox
        self.remove_number_var = tk.BooleanVar()
        ttk.Checkbutton(metadata_frame, text="Удалять номер в названии файла", 
                        variable=self.remove_number_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        metadata_frame.columnconfigure(1, weight=1)
        
        # Control buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="◀ Предыдущий", command=self.prev_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Сохранить текущий", command=self.save_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Следующий ▶", command=self.next_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Применить ко всем", command=self.apply_to_all).pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.pack(fill=tk.X)
        
    def setup_bindings(self):
        """Set up keyboard and context menu bindings."""
        # Global paste bindings
        self.root.bind_all('<Control-v>', self.on_paste)
        self.root.bind_all('<Control-V>', self.on_paste)
        
        # Context menu
        self._menu_widget = None
        self._context_menu = tk.Menu(self.root, tearoff=0)
        self._context_menu.add_command(label='Вырезать', command=self.cut_from_menu)
        self._context_menu.add_command(label='Копировать', command=self.copy_from_menu)
        self._context_menu.add_command(label='Вставить', command=self.paste_from_menu)
        
        # Bind right-click to entries
        for w in (self.artist_entry, self.album_entry, self.year_entry, self.genre_entry):
            w.bind('<Button-3>', self.show_context_menu)
    
    def select_directory(self):
        """Open directory dialog and load MP3 files."""
        directory = filedialog.askdirectory(title="Выберите директорию с MP3 файлами")
        if directory:
            self.current_dir = directory
            self.dir_label.config(text=directory, foreground="black")
            self.load_mp3_files()
    
    def load_mp3_files(self):
        """Scan directory for MP3 files and populate listbox."""
        if not self.current_dir:
            return
        
        self.mp3_files = FileService.find_mp3_files(self.current_dir)
        self.file_listbox.delete(0, tk.END)
        for mp3_file in self.mp3_files:
            self.file_listbox.insert(tk.END, mp3_file)
        
        if self.mp3_files:
            self.current_file_index = 0
            self.file_listbox.selection_set(0)
            self.load_metadata(0)
            self.status_label.config(text=f"Загружено {len(self.mp3_files)} MP3 файлов")
        else:
            self.status_label.config(text="MP3 файлы не найдены", foreground="red")
    
    def on_file_select(self, event):
        """Handle file selection from listbox."""
        selection = self.file_listbox.curselection()
        if selection:
            self.current_file_index = selection[0]
            self.load_metadata(self.current_file_index)
    
    def load_metadata(self, index):
        """Load metadata for file at given index."""
        if index < 0 or index >= len(self.mp3_files):
            return
        
        file_path = os.path.join(self.current_dir, self.mp3_files[index])
        
        try:
            metadata = MetadataService.load_metadata(file_path)
            self.current_metadata = metadata
            
            self.artist_entry.delete(0, tk.END)
            self.artist_entry.insert(0, metadata.artist)
            
            self.album_entry.delete(0, tk.END)
            self.album_entry.insert(0, metadata.album)
            
            self.year_entry.delete(0, tk.END)
            self.year_entry.insert(0, metadata.year)
            
            self.genre_entry.delete(0, tk.END)
            self.genre_entry.insert(0, metadata.genre)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить метаданные: {str(e)}")
            # Clear fields
            self.artist_entry.delete(0, tk.END)
            self.album_entry.delete(0, tk.END)
            self.year_entry.delete(0, tk.END)
            self.genre_entry.delete(0, tk.END)
        
        self.cover_image_path = None
        self.cover_label.config(text="Не выбрана", foreground="gray")
        self.cover_preview.clear()
        self.status_label.config(text=f"Файл: {self.mp3_files[index]}")
    
    def select_cover(self):
        """Open file dialog to select cover image."""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение обложки",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file_path:
            # Validate image size
            is_valid, error = validate_image_size(file_path, max_size_mb=10.0)
            if not is_valid:
                messagebox.showwarning("Предупреждение", f"{error}\nВы можете продолжить, но это может замедлить работу.")
            
            self.cover_image_path = file_path
            self.cover_label.config(text=Path(file_path).name, foreground="black")
            self.cover_preview.set_image(file_path)
    
    def on_paste(self, event):
        """Global paste handler."""
        widget = self.root.focus_get()
        if widget and paste_to_widget(widget, self.root):
            return "break"
    
    def show_context_menu(self, event):
        """Show right-click context menu."""
        self._menu_widget = event.widget
        self._context_menu.tk_popup(event.x_root, event.y_root)
    
    def paste_from_menu(self):
        """Paste from context menu."""
        if self._menu_widget:
            paste_to_widget(self._menu_widget, self.root)
    
    def copy_from_menu(self):
        """Copy from context menu."""
        if self._menu_widget:
            copy_from_widget(self._menu_widget, self.root)
    
    def cut_from_menu(self):
        """Cut from context menu."""
        if self._menu_widget:
            cut_from_widget(self._menu_widget, self.root)
    
    def prev_file(self):
        """Navigate to previous file."""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_file_index)
            self.file_listbox.see(self.current_file_index)
            self.load_metadata(self.current_file_index)
    
    def next_file(self):
        """Navigate to next file."""
        if self.current_file_index < len(self.mp3_files) - 1:
            self.current_file_index += 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_file_index)
            self.file_listbox.see(self.current_file_index)
            self.load_metadata(self.current_file_index)
    
    def save_current(self):
        """Save metadata for current file."""
        if not self.mp3_files:
            messagebox.showwarning("Предупреждение", "Нет загруженных файлов")
            return
        
        # Validate year
        year = self.year_entry.get()
        if year and not validate_year(year):
            messagebox.showerror("Ошибка", "Некорректный год. Должен быть числом от 1900 до 2100.")
            return
        
        file_path = os.path.join(self.current_dir, self.mp3_files[self.current_file_index])
        
        # Rename if needed
        if self.remove_number_var.get():
            file_path = FileService.rename_file_without_track_number(file_path)
        
        # Create metadata object from UI
        metadata = Metadata(
            artist=self.artist_entry.get(),
            album=self.album_entry.get(),
            year=year,
            genre=self.genre_entry.get()
        )
        
        try:
            MetadataService.save_metadata(file_path, metadata, self.cover_image_path)
            messagebox.showinfo("Успех", f"Метаданные сохранены для {os.path.basename(file_path)}")
            self.load_mp3_files()  # Refresh list in case of rename
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить метаданные: {str(e)}")
    
    def apply_to_all(self):
        """Apply current metadata to all files."""
        if not self.mp3_files:
            messagebox.showwarning("Предупреждение", "Нет загруженных файлов")
            return
        
        # Validate year
        year = self.year_entry.get()
        if year and not validate_year(year):
            messagebox.showerror("Ошибка", "Некорректный год. Должен быть числом от 1900 до 2100.")
            return
        
        confirm = messagebox.askyesno(
            "Подтверждение", 
            f"Применить метаданные ко всем {len(self.mp3_files)} файлам?"
        )
        if not confirm:
            return
        
        # Create metadata object from UI
        metadata = Metadata(
            artist=self.artist_entry.get(),
            album=self.album_entry.get(),
            year=year,
            genre=self.genre_entry.get()
        )
        
        # Show progress dialog
        progress = ProgressDialog(self.root, title="Применение метаданных")
        
        try:
            for i, mp3_file in enumerate(self.mp3_files):
                if progress.cancelled:
                    break
                
                file_path = os.path.join(self.current_dir, mp3_file)
                
                # Rename if needed
                if self.remove_number_var.get():
                    file_path = FileService.rename_file_without_track_number(file_path)
                
                # Save metadata
                MetadataService.save_metadata(file_path, metadata, self.cover_image_path)
                
                # Update progress
                progress.update(i + 1, len(self.mp3_files), f"Обработано {i+1}/{len(self.mp3_files)}")
            
            progress.close()
            
            if progress.cancelled:
                self.status_label.config(text="Операция отменена", foreground="orange")
            else:
                self.load_mp3_files()  # Refresh list
                messagebox.showinfo("Успех", f"Метаданные применены ко всем файлам")
                self.status_label.config(text="Метаданные успешно применены", foreground="green")
                
        except Exception as e:
            progress.close()
            messagebox.showerror("Ошибка", f"Не удалось применить метаданные: {str(e)}")