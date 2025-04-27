import tkinter as tk
from tkinter import ttk

from ui.ventas.ingreso_tab import IngresoTab
from ui.ventas.historial_tab import HistorialTab
from ui.ventas.inventario_tab import InventarioTab
from ui.ventas.eliminar_tab import EliminarTab
from app import __version__  

class MainWindow(tk.Tk):
    TABS = {
        "Ingreso de Ventas": IngresoTab,
        "Historial de Ventas": HistorialTab,
        "Control de Inventario": InventarioTab,
        "Eliminar Ventas": EliminarTab,
    }

    def __init__(self) -> None:
        super().__init__()
        self.title(f"Matex v{__version__} — Administrador de Ventas")
        self.geometry("900x600")
        self._build_ui()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        
        # ▶ Barra de estado/version:
        status = ttk.Label(
            self,
            text=f"Matex — v{__version__}",
            anchor="e",
            relief="sunken",
            padding=(5, 2),
        )
        status.pack(fill="x", side="bottom")
        for label, Tab in self.TABS.items():
            frame = Tab(notebook)      # Cada Tab hereda de ttk.Frame
            notebook.add(frame, text=label)