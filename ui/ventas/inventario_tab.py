import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

from services.producto_service import ProductoService
from ui import popup_error, popup_success, clear_frame
from utils.format_utils import format_money

class InventarioTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.service = ProductoService()
        self._build_widgets()
        self._update_table()

    def _build_widgets(self):
        clear_frame(self)
        ttk.Label(self, text="Inventario de Productos", font=("Arial", 14, "bold")).pack(pady=10)

        # Botones de filtro
        btns = ttk.Frame(self)
        btns.pack(pady=5)
        ttk.Button(btns, text="Ver todos", command=self._update_table).pack(side="left", padx=5)
        ttk.Button(btns, text="Stock bajo", command=lambda: self._update_table(stock_bajo=True)).pack(side="left", padx=5)
        ttk.Button(btns, text="Sin precio", command=lambda: self._update_table(sin_precio=True)).pack(side="left", padx=5)
        ttk.Button(btns, text="Exportar a Excel", command=self._exportar).pack(side="left", padx=5)
        ttk.Button(btns, text="Agregar Producto", command=self._nuevo).pack(side="left", padx=5)
        ttk.Button(btns, text="Eliminar Producto", command=self._eliminar).pack(side="left", padx=5)

        # Tabla
        frame_tabla = ttk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(
            frame_tabla, columns=("ID", "Producto", "Precio", "Stock"), show="headings"
        )
        for col, w in zip(("ID", "Producto", "Precio", "Stock"), (50, 250, 100, 100)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._editar)
        ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview).pack(side="right", fill="y")

    # -------- Acciones -----------
    def _update_table(self, stock_bajo=False, sin_precio=False):
        for r in self.tree.get_children():
            self.tree.delete(r)
        prods = self.service.listar(stock_bajo=stock_bajo, sin_precio=sin_precio)
        for p in prods:
            self.tree.insert("", "end", values=(p["id"], p["nombre"], format_money(p["precio"]), p["stock"]))

    def _exportar(self):
        ruta = self.service.exportar_excel()
        popup_success(f"Inventario exportado a:\n{ruta}")

    def _nuevo(self):
        # Ventana simple de alta
        win = tk.Toplevel(self)
        win.title("Nuevo producto")
        ttk.Label(win, text="Nombre:").pack(pady=5)
        nombre = tk.StringVar()
        ttk.Entry(win, textvariable=nombre).pack()
        ttk.Label(win, text="Precio neto:").pack(pady=5)
        precio = tk.StringVar()
        ttk.Entry(win, textvariable=precio).pack()
        ttk.Label(win, text="Stock:").pack(pady=5)
        stock = tk.StringVar()
        ttk.Entry(win, textvariable=stock).pack()

        def guardar():
            try:
                self.service.alta(nombre.get(), int(precio.get()), int(stock.get()))
            except Exception as exc:
                popup_error(str(exc))
                return
            popup_success("Producto agregado")
            win.destroy()
            self._update_table()

        ttk.Button(win, text="Guardar", command=guardar).pack(pady=10)

    def _eliminar(self):
        item = self.tree.focus()
        if not item:
            popup_error("Selecciona un producto.")
            return
        id_prod = int(self.tree.item(item, "values")[0])
        self.service.baja(id_prod)
        popup_success("Producto eliminado")
        self._update_table()

    def _editar(self, _evt):
        item = self.tree.focus()
        if not item:
            return
        id_prod, nombre, precio, stock = self.tree.item(item, "values")
        win = tk.Toplevel(self)
        win.title(f"Editar: {nombre}")
        ttk.Label(win, text=f"Producto: {nombre}", font=("Arial", 12, "bold")).pack(pady=5)

        ttk.Label(win, text="Precio neto:").pack()
        precio_var = tk.StringVar(value=str(precio).replace("$", "").replace(".", ""))
        ttk.Entry(win, textvariable=precio_var).pack()
        ttk.Label(win, text="Stock:").pack()
        stock_var = tk.StringVar(value=str(stock))
        ttk.Entry(win, textvariable=stock_var).pack()

        def confirmar():
            try:
                self.service.modificar(int(id_prod), int(precio_var.get()), int(stock_var.get()))
            except Exception as exc:
                popup_error(str(exc))
                return
            popup_success("Producto actualizado")
            win.destroy()
            self._update_table()

        ttk.Button(win, text="Confirmar", command=confirmar).pack(pady=15)