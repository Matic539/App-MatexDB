import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd
import os

from services.ventas_service import VentasService
from ui import popup_error, popup_success, clear_frame
from utils.format_utils import format_money

class HistorialTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.service = VentasService()
        self._build_widgets()
        self._update_table()

    def _build_widgets(self):
        clear_frame(self)
        ttk.Label(self, text="Historial de Ventas", font=("Arial", 14, "bold")).pack(pady=10)

        # Filtros
        filtros = ttk.Frame(self)
        filtros.pack(pady=5)
        ttk.Label(filtros, text="Desde:").pack(side="left")
        self.f_desde = DateEntry(filtros, date_pattern="yyyy-mm-dd", width=12)
        self.f_desde.pack(side="left", padx=5)
        ttk.Label(filtros, text="Hasta:").pack(side="left")
        self.f_hasta = DateEntry(filtros, date_pattern="yyyy-mm-dd", width=12)
        self.f_hasta.pack(side="left", padx=5)
        ttk.Button(filtros, text="Buscar", command=self._buscar).pack(side="left", padx=5)
        ttk.Button(filtros, text="🔄", width=3, command=self._update_table).pack(side="left", padx=5)
        ttk.Button(filtros, text="Exportar a Excel", command=self._exportar).pack(side="left", padx=5)

        # Tabla
        frame_tabla = ttk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(
            frame_tabla,
            columns=("ID", "Fecha", "Forma", "Productos", "Monto"),
            show="headings",
        )
        for col, w in zip(("ID", "Fecha", "Forma", "Productos", "Monto"), (50, 100, 120, 120, 120)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._detalle)
        ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview).pack(side="right", fill="y")

    # -------- Acciones -----------
    def _update_table(self, rango=None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        ventas = self.service.obtener_ventas(rango)
        for v in ventas:
            self.tree.insert(
                "", "end", values=(v["id"], v["fecha"], v["forma"], v["total_prod"], format_money(v["monto"]))
            )

    def _buscar(self):
        rango = (
            self.f_desde.get_date().strftime("%Y-%m-%d"),
            self.f_hasta.get_date().strftime("%Y-%m-%d"),
        )
        self._update_table(rango)

    def _detalle(self, _evt):
        item = self.tree.focus()
        if not item:
            return
        id_venta = int(self.tree.item(item, "values")[0])
        productos = self.service.ver_detalle_venta(id_venta)

        win = tk.Toplevel(self)
        win.title(f"Detalle venta #{id_venta}")
        tree = ttk.Treeview(win, columns=("Producto", "Cant.", "Monto"), show="headings")
        for col in ("Producto", "Cant.", "Monto"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        for p in productos:
            tree.insert("", "end", values=(p["nombre"], p["cantidad"], format_money(p["monto"])))

    def _exportar(self):
        path = self.service.exportar_ventas_excel()
        popup_success(f"Archivo guardado en:\n{path}")