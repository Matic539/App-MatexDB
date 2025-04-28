"""Ventana principal de la aplicación Matex (capa UI)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Type

from app import __version__
from ui.ventas.eliminar_tab import EliminarTab
from ui.ventas.historial_tab import HistorialTab
from ui.ventas.ingreso_tab import IngresoTab
from ui.ventas.inventario_tab import InventarioTab


class MainWindow(tk.Tk):
    """Contenedor raíz con todas las pestañas."""

    #: Mapa *Etiqueta → Clase de pestaña*
    TABS = {
        "Ingreso de Ventas": IngresoTab,
        "Historial de Ventas": HistorialTab,
        "Control de Inventario": InventarioTab,
        "Eliminar Ventas": EliminarTab,
    }

    def __init__(self) -> None:
        """Inicializa la ventana y construye los widgets."""
        super().__init__()
        self.title(f"Matex v{__version__} — Administrador de Ventas")
        self.geometry("900x600")
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        """Crea el Notebook y añade cada pestaña declarada en ``TABS``."""
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Barra de estado con la versión
        status = ttk.Label(
            self,
            text=f"Matex — v{__version__}",
            anchor="e",
            relief="sunken",
            padding=(5, 2),
        )
        status.pack(fill="x", side="bottom")

        # Cargar dinámicamente las pestañas
        for label, TabClass in self.TABS.items():
            frame = TabClass(notebook)  # Cada Tab hereda de ttk.Frame
            notebook.add(frame, text=label)
