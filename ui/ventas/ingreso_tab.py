"""Pestaña para registrar una nueva venta."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk
from typing import Dict

from tkcalendar import DateEntry

from services.ventas_service import StockError, VentasService
from ui import clear_frame, popup_error, popup_success
from utils.format_utils import format_money


class IngresoTab(ttk.Frame):
    """Formulario de venta con listado de productos y cálculo de totales."""

    def __init__(self, parent: ttk.Notebook):
        super().__init__(parent)
        self.service = VentasService()
        self._build_widgets()

    # ------------------------------------------------------------------ GUI
    def _build_widgets(self) -> None:
        clear_frame(self)

        # Fecha
        ttk.Label(self, text="Fecha de venta:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.fecha_entry = DateEntry(self, date_pattern="yyyy-mm-dd", width=18)
        self.fecha_entry.set_date(date.today())
        self.fecha_entry.grid(row=0, column=1)

        # Botón de refresco
        ttk.Button(self, text="🔄", width=3, command=self._refresh).grid(
            row=0, column=2, sticky="e", padx=5
        )

        # Forma de pago
        ttk.Label(self, text="Forma de pago:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.forma_pago_var = tk.StringVar(value="efectivo")
        ttk.Combobox(
            self,
            textvariable=self.forma_pago_var,
            values=["tarjeta", "efectivo", "transferencia", "mixto", "link de pago"],
            state="readonly",
            width=20,
        ).grid(row=1, column=1)

        # Canvas de productos con scroll
        self._build_canvas()

        # Detalles de la venta confirmada
        self._build_detalles()

        # Botones principales
        ttk.Button(
            self,
            text="Confirmar venta",
            command=self._confirmar,
            style="Accent.TButton",
        ).grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(self, text="Guardar venta", command=self._guardar).grid(
            row=5, column=0, columnspan=2, pady=5
        )

        self._cargar_productos()

    def _build_canvas(self) -> None:
        """Crea el canvas que aloja la lista de productos con scroll."""
        self.canvas = tk.Canvas(self, height=350, width=400)
        self.canvas.grid(row=3, column=0, columnspan=2, padx=10, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.products_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        self.products_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Scroll con rueda del mouse
        def _on_mousewheel(event):
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", _on_mousewheel)

    def _build_detalles(self) -> None:
        frame = ttk.Frame(self)
        frame.grid(row=0, column=3, rowspan=3, padx=20, sticky="n")

        ttk.Label(
            frame, text="🧾 Detalles de la Compra", font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.resumen_lbl = ttk.Label(
            frame, text="Aquí aparecerán los detalles...", justify="left"
        )
        self.resumen_lbl.pack(anchor="w")

    # ---------------------------------------------------------------- Lógica
    def _refresh(self) -> None:
        """Recarga productos y limpia el formulario."""
        self._cargar_productos()
        self.resumen_lbl.config(text="Aquí aparecerán los detalles…")
        if hasattr(self, "items_confirmados"):
            del self.items_confirmados

    def _cargar_productos(self) -> None:
        """Llena el canvas con productos obtenidos del servicio."""
        self.cantidades: Dict[int, Dict] = {}
        for w in self.products_frame.winfo_children():
            w.destroy()

        for i, (id_prod, nombre, stock) in enumerate(
            self.service.producto_repo.obtener_productos()
        ):
            ttk.Label(self.products_frame, text=f"{nombre} (Stock: {stock})").grid(
                row=i, column=0, sticky="w"
            )
            var = tk.StringVar(value="0")
            ttk.Entry(self.products_frame, textvariable=var, width=5).grid(
                row=i, column=1
            )
            self.cantidades[id_prod] = {"var": var, "nombre": nombre, "stock": stock}

    def _confirmar(self) -> None:
        """Valida stock y muestra resumen antes de guardar."""
        try:
            items = self.service.preparar_items_venta(self.cantidades)
        except StockError as exc:
            popup_error(str(exc))
            return

        if not items:
            popup_error("Debes seleccionar al menos un producto")
            return

        total_prod = sum(i["cantidad"] for i in items)
        total_monto = sum(i["monto_producto"] for i in items)
        self.items_confirmados = items

        resumen = (
            f"📅 Fecha: {self.fecha_entry.get_date():%Y-%m-%d}\n"
            f"💳 Forma de pago: {self.forma_pago_var.get()}\n"
            f"🛍 Productos: {total_prod}\n"
            f"💰 Monto total (IVA incluido): {format_money(total_monto)}"
        )
        self.resumen_lbl.config(text=resumen)
        popup_success("Venta confirmada. Pulsa *Guardar venta* para persistir.")

    def _guardar(self) -> None:
        """Envía la venta al servicio y actualiza la UI."""
        if not hasattr(self, "items_confirmados"):
            popup_error("Confirma la venta antes de guardarla.")
            return

        try:
            id_venta = self.service.crear_venta(
                fecha=self.fecha_entry.get_date().strftime("%Y-%m-%d"),
                forma_pago=self.forma_pago_var.get(),
                items=self.items_confirmados,
            )
        except Exception as exc:  # noqa: BLE001
            popup_error(f"Ocurrió un error: {exc}")
            return

        popup_success(f"Venta #{id_venta} registrada correctamente")
        self.resumen_lbl.config(text="Aquí aparecerán los detalles...")
        self._cargar_productos()
        del self.items_confirmados
