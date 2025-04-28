"""Pestaña para eliminar ventas y restaurar stock."""

from __future__ import annotations

import tkinter as tk

from services.ventas_service import VentasService
from ui import clear_frame, popup_error, popup_success


class EliminarTab(tk.Frame):
    """Frame Tkinter que permite eliminar una venta por ID."""

    def __init__(self, parent: tk.Misc):
        super().__init__(parent)
        self.service = VentasService()
        self._build_widgets()

    # ------------------------------------------------------------------ UI
    def _build_widgets(self) -> None:
        """Crea los widgets dentro de la pestaña."""
        clear_frame(self)
        tk.Label(self, text="Ingrese el ID de la venta a eliminar:").pack(pady=10)

        self.id_var = tk.StringVar()
        tk.Entry(self, textvariable=self.id_var, width=10).pack()

        tk.Button(
            self,
            text="Eliminar",
            command=self._eliminar,
            bg="red",
            fg="white",
        ).pack(pady=20)

    # ---------------------------------------------------------------- Acciones
    def _eliminar(self) -> None:
        """Valida el ID y solicita a VentasService que elimine la venta."""
        try:
            id_venta = int(self.id_var.get())
        except ValueError:
            popup_error("ID no válido")
            return

        try:
            self.service.eliminar_venta(id_venta)
        except ValueError as exc:
            popup_error(str(exc))
            return

        popup_success(f"Venta #{id_venta} eliminada")
        self.id_var.set("")
