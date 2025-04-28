"""Operaciones CRUD y reportes de *ventas*."""

from __future__ import annotations

import os
from typing import Any, Dict, Sequence

import pandas as pd

from repository.db import get_conn


# -------------------------------------------------------------------------
# CRUD
# -------------------------------------------------------------------------
def insertar_venta(venta: Dict[str, Any], items: Sequence[Dict[str, Any]]) -> int:
    """Inserta cabecera y detalle de una venta.

    Args:
        venta: Dict con fecha, forma_pago, monto_total, total_productos.
        items: Secuencia de dicts con id_producto, cantidad, monto_producto.

    Returns:
        id_venta generado.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO ventas (fecha, forma_pago, monto_total, total_productos)
            VALUES (%(fecha)s, %(forma_pago)s, %(monto_total)s, %(total_productos)s)
            RETURNING id_venta
            """,
            venta,
        )
        id_venta: int = cur.fetchone()[0]
        detalle = [(id_venta, it["id_producto"], it["cantidad"], it["monto_producto"]) for it in items]
        cur.executemany(
            """
            INSERT INTO ventas_producto
            (id_venta, id_producto, cantidad, monto_producto)
            VALUES (%s, %s, %s, %s)
            """,
            detalle,
        )
        return id_venta


def eliminar_venta(id_venta: int) -> None:
    """Elimina una venta y restaura el stock de sus productos."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id_producto, cantidad FROM ventas_producto WHERE id_venta = %s",
            (id_venta,),
        )
        for id_prod, cant in cur.fetchall():
            cur.execute(
                "UPDATE productos SET stock = stock + %s WHERE id_producto = %s",
                (cant, id_prod),
            )
        cur.execute("DELETE FROM ventas_producto WHERE id_venta = %s", (id_venta,))
        cur.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))


# -------------------------------------------------------------------------
# Lecturas y exportación
# -------------------------------------------------------------------------
def listar(rango: tuple[str, str] | None = None) -> list[dict[str, Any]]:
    """Lista ventas opcionalmente filtradas por rango de fechas.

    Args:
        rango: Tupla ``(desde, hasta)`` en formato *YYYY-MM-DD*.

    Returns:
        Lista de dicts con id, fecha, forma, total_prod, monto.
    """
    sql = """
        SELECT id_venta, fecha, forma_pago, total_productos, monto_total
        FROM ventas
    """
    params: tuple[Any, ...] = ()
    if rango:
        sql += " WHERE fecha BETWEEN %s AND %s"
        params = rango
    sql += " ORDER BY fecha DESC"

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return [
            {
                "id": r[0],
                "fecha": r[1],
                "forma": r[2],
                "total_prod": r[3],
                "monto": r[4],
            }
            for r in cur.fetchall()
        ]


def detalle(id_venta: int) -> list[dict[str, Any]]:
    """Devuelve el detalle de productos vendidos en una venta."""
    sql = """
        SELECT p.nombre, vp.cantidad, vp.monto_producto
        FROM ventas_producto vp
        JOIN productos p ON vp.id_producto = p.id_producto
        WHERE vp.id_venta = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (id_venta,))
        return [{"nombre": r[0], "cantidad": r[1], "monto": r[2]} for r in cur.fetchall()]


def exportar_excel() -> str:
    """Exporta la tabla de ventas a *data/ventas_exportadas.xlsx*.

    Returns:
        Ruta absoluta del archivo generado.
    """
    df = pd.DataFrame(listar())
    os.makedirs("data", exist_ok=True)
    path = os.path.abspath("data/ventas_exportadas.xlsx")
    df.to_excel(path, index=False)
    return path
