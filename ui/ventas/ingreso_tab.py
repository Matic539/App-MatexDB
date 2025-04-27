from datetime import date
from tkinter import ttk
import tkinter as tk
from tkcalendar import DateEntry

from services.ventas_service import VentasService, StockError
from ui import popup_error, popup_success, clear_frame
from utils.format_utils import format_money

class IngresoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.service = VentasService()
        self._build_widgets()

    # ---------- GUI ----------
    def _build_widgets(self):
        clear_frame(self)

        # Fecha
        ttk.Label(self, text="Fecha de venta:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.fecha_entry = DateEntry(self, date_pattern="yyyy-mm-dd", width=18)
        self.fecha_entry.set_date(date.today())
        self.fecha_entry.grid(row=0, column=1)

        # ▶ Botón de refresco
        ttk.Button(self, text="🔄", width=3, command=self._refresh).grid(row=0, column=2, sticky="e", padx=5)

        # Forma de pago
        ttk.Label(self, text="Forma de pago:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.forma_pago_var = tk.StringVar(value="efectivo")
        ttk.Combobox(
            self,
            textvariable=self.forma_pago_var,
            values=["tarjeta", "efectivo", "transferencia", "mixto", "link de pago"],
            state="readonly",
            width=20,
        ).grid(row=1, column=1)

        # Canvas de productos
        self.canvas = tk.Canvas(self, height=350, width=400)
        self.canvas.grid(row=3, column=0, columnspan=2, padx=10, sticky="nsew")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.products_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        self.products_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # ▶ soporte cross-platform para el scroll del mouse
        def _on_mousewheel(event):
            # Windows / macOS
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")

        # Windows / macOS
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux (rueda arriba/abajo)
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)

        # Detalles
        self._build_detalles()

        # Botones
        ttk.Button(self, text="Confirmar venta", command=self._confirmar, style="Accent.TButton").grid(
            row=4, column=0, columnspan=2, pady=10
        )
        ttk.Button(self, text="Guardar venta", command=self._guardar).grid(row=5, column=0, columnspan=2, pady=5)

        self._cargar_productos()
    
    
    def _refresh(self):
        """Recarga la lista de productos y limpia el resumen."""
        self._cargar_productos()
        self.resumen_lbl.config(text="Aquí aparecerán los detalles…")
        # Borra posible venta confirmada
        if hasattr(self, "items_confirmados"):
            del self.items_confirmados

    def _build_detalles(self):
        frame = ttk.Frame(self)
        frame.grid(row=0, column=3, rowspan=3, padx=20, sticky="n")
        ttk.Label(frame, text="🧾 Detalles de la Compra", font=("Arial", 12, "bold")).pack(anchor="w")
        self.resumen_lbl = ttk.Label(frame, text="Aquí aparecerán los detalles...", justify="left")
        self.resumen_lbl.pack(anchor="w")

    # ---------- Lógica ----------
    def _cargar_productos(self):
        self.cantidades = {}
        for w in self.products_frame.winfo_children():
            w.destroy()

        for i, prod in enumerate(self.service.producto_repo.obtener_productos()):
            id_prod, nombre, stock = prod
            ttk.Label(self.products_frame, text=f"{nombre} (Stock: {stock})").grid(row=i, column=0, sticky="w")
            var = tk.StringVar(value="0")
            ttk.Entry(self.products_frame, textvariable=var, width=5).grid(row=i, column=1)
            self.cantidades[id_prod] = dict(var=var, nombre=nombre, stock=stock)

    def _confirmar(self):
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

    def _guardar(self):
        if not hasattr(self, "items_confirmados"):
            popup_error("Confirma la venta antes de guardarla.")
            return
        try:
            id_venta = self.service.crear_venta(
                fecha=self.fecha_entry.get_date().strftime("%Y-%m-%d"),
                forma_pago=self.forma_pago_var.get(),
                items=self.items_confirmados,
            )
        except Exception as exc:
            popup_error(f"Ocurrió un error: {exc}")
            return

        popup_success(f"Venta #{id_venta} registrada correctamente")
        self.resumen_lbl.config(text="Aquí aparecerán los detalles...")
        self._cargar_productos()
        del self.items_confirmados