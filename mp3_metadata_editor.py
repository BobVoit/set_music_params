"""
MP3 Metadata Editor - точка входа приложения.
Использует рефакторизованные модули из папки src.
"""

import tkinter as tk
from src.main_window import MainWindow


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
