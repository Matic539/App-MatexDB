from typing import Sequence, Dict, List
from decimal import Decimal, ROUND_HALF_UP

from repository import ventas_repo, producto_repo

class StockError(Exception):
    """Se lanza cuando no hay stock suficiente."""

class VentasService:
    def __init__(self):
        self.producto_repo = producto_repo

    # ----- Utilidades internas -----
    def preparar_items_venta(self, cantidades: Dict) -> List[Dict]:
        """Convierte los datos del formulario en items listos para persistir."""
        items: List[Dict] = []
        for id_prod, datos in cantidades.items():
            try:
                cantidad = int(datos["var"].get())
            except ValueError:
                cantidad = 0
            if cantidad <= 0:
                continue
            stock_disponible = datos["stock"]
            if cantidad > stock_disponible:
                raise StockError(f"No hay suficiente stock de {datos['nombre']}")
            precio_neto = self.producto_repo.obtener_precio(id_prod)
            monto = int(
                Decimal(precio_neto * 1.19 * cantidad).quantize(0, ROUND_HALF_UP)
            )
            items.append(
                dict(
                    id_producto=id_prod,
                    nombre=datos["nombre"],
                    cantidad=cantidad,
                    monto_producto=monto,
                )
            )
        return items

    # ----- API púbica -----
    def crear_venta(self, fecha: str, forma_pago: str, items: Sequence[Dict]) -> int:
        total_prod = sum(i["cantidad"] for i in items)
        total_monto = sum(i["monto_producto"] for i in items)
        id_venta = ventas_repo.insertar_venta(
            dict(
                fecha=fecha,
                forma_pago=forma_pago,
                monto_total=total_monto,
                total_productos=total_prod,
            ),
            items,
        )
        for it in items:
            self.producto_repo.descontar_stock(it["id_producto"], it["cantidad"])
        return id_venta

    def eliminar_venta(self, id_venta: int) -> None:
        ventas_repo.eliminar_venta(id_venta)

    def obtener_ventas(self, rango=None):
        return ventas_repo.listar(rango)

    def ver_detalle_venta(self, id_venta: int):
        return ventas_repo.detalle(id_venta)

    def exportar_ventas_excel(self) -> str:
        return ventas_repo.exportar_excel()