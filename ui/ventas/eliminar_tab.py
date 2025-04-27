import tkinter as tk
from ui import popup_error, popup_success, clear_frame
from services.ventas_service import VentasService

class EliminarTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.service = VentasService()
        self._build_widgets()

    def _build_widgets(self):
        clear_frame(self)
        tk.Label(self, text="Ingrese el ID de la venta a eliminar:").pack(pady=10)
        self.id_var = tk.StringVar()
        tk.Entry(self, textvariable=self.id_var, width=10).pack()
        tk.Button(self, text="Eliminar", command=self._eliminar, bg="red", fg="white").pack(pady=20)

    def _eliminar(self):
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