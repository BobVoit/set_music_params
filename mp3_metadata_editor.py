import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageTk
import io

class MP3MetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Metadata Editor")
        self.root.geometry("900x700")
        
        self.current_dir = None
        self.mp3_files = []
        self.current_file_index = 0
        self.current_metadata = {}
        self.cover_image_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Главное меню
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Выбор директории
        dir_frame = ttk.LabelFrame(main_frame, text="Выбор директории")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_label = ttk.Label(dir_frame, text="Директория не выбрана", foreground="gray")
        self.dir_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(dir_frame, text="Выбрать директорию", command=self.select_directory).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Содержание директории
        files_frame = ttk.LabelFrame(main_frame, text="MP3 файлы")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Список файлов
        scrollbar = ttk.Scrollbar(files_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(files_frame, yscrollcommand=scrollbar.set, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_listbox.yview)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Метаданные
        metadata_frame = ttk.LabelFrame(main_frame, text="Метаданные")
        metadata_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Исполнитель
        ttk.Label(metadata_frame, text="Исполнитель:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.artist_entry = ttk.Entry(metadata_frame, width=50)
        self.artist_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Альбом
        ttk.Label(metadata_frame, text="Альбом:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.album_entry = ttk.Entry(metadata_frame, width=50)
        self.album_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Год
        ttk.Label(metadata_frame, text="Год выпуска:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.year_entry = ttk.Entry(metadata_frame, width=50)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Жанр
        ttk.Label(metadata_frame, text="Жанр:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.genre_entry = ttk.Entry(metadata_frame, width=50)
        self.genre_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Обложка
        ttk.Label(metadata_frame, text="Обложка:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        cover_button_frame = ttk.Frame(metadata_frame)
        cover_button_frame.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        self.cover_label = ttk.Label(cover_button_frame, text="Не выбрана", foreground="gray")
        self.cover_label.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cover_button_frame, text="Выбрать обложку", command=self.select_cover).pack(side=tk.LEFT)
        
        # Опция удаления порядкового номера из имени файла
        self.remove_number_var = tk.BooleanVar()
        ttk.Checkbutton(metadata_frame, text="Удалять номер в названии файла", variable=self.remove_number_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        metadata_frame.columnconfigure(1, weight=1)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="◀ Предыдущий", command=self.prev_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Сохранить текущий", command=self.save_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Следующий ▶", command=self.next_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Применить ко всем", command=self.apply_to_all).pack(side=tk.RIGHT, padx=5)
        
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.pack(fill=tk.X)
        
    def select_directory(self):
        directory = filedialog.askdirectory(title="Выберите директорию с MP3 файлами")
        if directory:
            self.current_dir = directory
            self.dir_label.config(text=directory, foreground="black")
            self.load_mp3_files()
            
    def load_mp3_files(self):
        self.mp3_files = [f for f in os.listdir(self.current_dir) if f.lower().endswith('.mp3')]
        self.mp3_files.sort()
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
        selection = self.file_listbox.curselection()
        if selection:
            self.current_file_index = selection[0]
            self.load_metadata(self.current_file_index)
            
    def load_metadata(self, index):
        if index < 0 or index >= len(self.mp3_files):
            return
            
        file_path = os.path.join(self.current_dir, self.mp3_files[index])
        
        try:
            audio = EasyID3(file_path)
            self.artist_entry.delete(0, tk.END)
            self.artist_entry.insert(0, audio.get('artist', [''])[0])
            
            self.album_entry.delete(0, tk.END)
            self.album_entry.insert(0, audio.get('album', [''])[0])
            
            self.year_entry.delete(0, tk.END)
            self.year_entry.insert(0, audio.get('date', [''])[0])
            
            self.genre_entry.delete(0, tk.END)
            self.genre_entry.insert(0, audio.get('genre', [''])[0])
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить метаданные: {str(e)}")
        
        self.cover_image_path = None
        self.cover_label.config(text="Не выбрана", foreground="gray")
        self.status_label.config(text=f"Файл: {self.mp3_files[index]}")
        
    def select_cover(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение обложки",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if file_path:
            self.cover_image_path = file_path
            self.cover_label.config(text=Path(file_path).name, foreground="black")

    def rename_file(self, file_path: str) -> str:
        """If checkbox is active, remove leading track number (e.g. "11. ") from filename."""
        if not self.remove_number_var.get():
            return file_path
        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        # strip pattern of starting digits, dot and spaces
        import re
        newname = re.sub(r'^\s*\d+\.\s*', '', basename)
        if newname and newname != basename:
            newpath = os.path.join(dirname, newname)
            try:
                os.rename(file_path, newpath)
            except Exception:
                # ignore rename errors
                return file_path
            return newpath
        return file_path
            
    def prev_file(self):
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_file_index)
            self.file_listbox.see(self.current_file_index)
            self.load_metadata(self.current_file_index)
            
    def next_file(self):
        if self.current_file_index < len(self.mp3_files) - 1:
            self.current_file_index += 1
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self.current_file_index)
            self.file_listbox.see(self.current_file_index)
            self.load_metadata(self.current_file_index)
            
    def save_current(self):
        if not self.mp3_files:
            messagebox.showwarning("Предупреждение", "Нет загруженных файлов")
            return
            
        file_path = os.path.join(self.current_dir, self.mp3_files[self.current_file_index])
        new_path = self.rename_file(file_path)
        self.save_metadata(new_path)
        messagebox.showinfo("Успех", f"Метаданные сохранены для {os.path.basename(new_path)}")
        # обновляем список на случай изменения имени
        self.load_mp3_files()
        
    def apply_to_all(self):
        if not self.mp3_files:
            messagebox.showwarning("Предупреждение", "Нет загруженных файлов")
            return
            
        confirm = messagebox.askyesno("Подтверждение", 
                                      f"Применить метаданные ко всем {len(self.mp3_files)} файлам?")
        if confirm:
            for i, mp3_file in enumerate(self.mp3_files):
                file_path = os.path.join(self.current_dir, mp3_file)
                new_path = self.rename_file(file_path)
                self.save_metadata(new_path)
                self.status_label.config(text=f"Обработано {i+1}/{len(self.mp3_files)}")
                self.root.update()
                
            # после обработки обновим список в GUI в случае переименований
            self.load_mp3_files()
            messagebox.showinfo("Успех", f"Метаданные применены ко всем файлам")
            self.status_label.config(text="Метаданные успешно применены", foreground="green")
        
    def save_metadata(self, file_path):
        try:
            # Загружаем или создаем метаданные
            try:
                audio = EasyID3(file_path)
            except:
                audio = EasyID3()
                
            # Сохраняем метаданные
            artist = self.artist_entry.get()
            if artist:
                audio['artist'] = artist
                
            album = self.album_entry.get()
            if album:
                audio['album'] = album
                
            year = self.year_entry.get()
            if year:
                audio['date'] = year
                
            genre = self.genre_entry.get()
            if genre:
                audio['genre'] = genre
                
            audio.save(file_path)
            
            # Обработка обложки
            if self.cover_image_path:
                try:
                    audio_id3 = ID3(file_path)
                except:
                    audio_id3 = ID3()
                    
                with open(self.cover_image_path, 'rb') as f:
                    image_data = f.read()
                    
                # Определяем MIME тип по расширению
                ext = Path(self.cover_image_path).suffix.lower()
                mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                
                audio_id3.add(APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=image_data))
                audio_id3.save(file_path, v2_version=3)
                
        except Exception as e:
            raise Exception(f"Ошибка сохранения: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MP3MetadataEditor(root)
    root.mainloop()
