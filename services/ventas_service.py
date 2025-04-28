"""Reglas de negocio de ventas: creación, eliminación y consultas."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Sequence

from repository import producto_repo, ventas_repo


class StockError(Exception):
    """Se lanza si la cantidad solicitada supera el stock disponible."""


class VentasService:
    """Orquesta las operaciones de venta y delega en los repositorios."""

    def __init__(self) -> None:
        self.producto_repo = producto_repo

    # ---------------------------------------------------------------- utils
    def preparar_items_venta(self, cantidades: Dict) -> list[Dict]:
        """Convierte los datos del formulario en ítems listos para persistir.

        Args:
            cantidades: Dict cuyas claves son `id_producto` y cuyo valor es otro
                dict con keys: ``var`` (StringVar), ``nombre`` y ``stock``.

        Returns:
            Lista de diccionarios con id_producto, nombre, cantidad y
            monto_producto (IVA incluido).

        Raises:
            StockError: Si se intenta vender más unidades de las disponibles.
        """
        items: list[Dict] = []
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
            monto = int(Decimal(precio_neto * 1.19 * cantidad).quantize(0, ROUND_HALF_UP))

            items.append(
                {
                    "id_producto": id_prod,
                    "nombre": datos["nombre"],
                    "cantidad": cantidad,
                    "monto_producto": monto,
                }
            )
        return items

    # ---------------------------------------------------------------- API
    def crear_venta(self, *, fecha: str, forma_pago: str, items: Sequence[Dict]) -> int:
        """Persiste la venta y descuenta stock.

        Args:
            fecha: `YYYY-MM-DD`.
            forma_pago: cadena libre ("efectivo", "tarjeta", etc.).
            items: Secuencia de dicts devueltos por `preparar_items_venta`.

        Returns:
            id_venta generado.
        """
        total_prod = sum(i["cantidad"] for i in items)
        total_monto = sum(i["monto_producto"] for i in items)

        id_venta = ventas_repo.insertar_venta(
            {
                "fecha": fecha,
                "forma_pago": forma_pago,
                "monto_total": total_monto,
                "total_productos": total_prod,
            },
            items,
        )

        for it in items:
            self.producto_repo.descontar_stock(it["id_producto"], it["cantidad"])

        return id_venta

    def eliminar_venta(self, id_venta: int) -> None:
        """Elimina una venta y restaura el stock asociado."""
        ventas_repo.eliminar_venta(id_venta)

    def obtener_ventas(self, rango: tuple[str, str] | None = None):
        """Lista ventas (opcionalmente acotadas por fechas)."""
        return ventas_repo.listar(rango)

    def ver_detalle_venta(self, id_venta: int):
        """Devuelve el detalle de productos vendidos en una venta."""
        return ventas_repo.detalle(id_venta)

    def exportar_ventas_excel(self) -> str:
        """Exporta las ventas a Excel y devuelve la ruta del archivo."""
        return ventas_repo.exportar_excel()
