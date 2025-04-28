"""Pequeñas utilidades de interfaz basadas en Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox


def clear_frame(frame: tk.Misc) -> None:
    """Destruye todos los widgets hijos de *frame*."""
    for widget in frame.winfo_children():
        widget.destroy()


def popup_error(msg: str, title: str = "Error") -> None:
    """Muestra un diálogo de error estándar."""
    messagebox.showerror(title, msg)


def popup_success(msg: str, title: str = "Éxito") -> None:
    """Muestra un diálogo de información con estilo “éxito”."""
    messagebox.showinfo(title, msg)
