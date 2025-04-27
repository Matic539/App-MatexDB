import tkinter as tk
from tkinter import messagebox
from typing import Any

def clear_frame(frame: tk.Misc) -> None:
    for widget in frame.winfo_children():
        widget.destroy()

def popup_error(msg: str, title: str = "Error") -> None:
    messagebox.showerror(title, msg)

def popup_success(msg: str, title: str = "Éxito") -> None:
    messagebox.showinfo(title, msg)