"""Operaciones CRUD sobre *productos* y *precios*.

Esta capa NO contiene lógica de negocio; solo SQL y transformaciones
mínimas a tipos *dict* / *list*.
"""

from __future__ import annotations

import os
from typing import Any, Sequence

import pandas as pd

from repository.db import get_conn


# -------------------------------------------------------------------------
# Helpers internos
# -------------------------------------------------------------------------
def _fetch_all(sql: str, params: Sequence[Any] = ()) -> list[tuple]:
    """Ejecuta una consulta y devuelve todas las filas."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# -------------------------------------------------------------------------
# API pública
# -------------------------------------------------------------------------
def obtener_productos() -> list[tuple[int, str, int]]:
    """Lista id, nombre y stock de todos los productos."""
    return _fetch_all(
        "SELECT id_producto, nombre, stock FROM productos ORDER BY id_producto"
    )


def obtener_precio(id_prod: int) -> int:
    """Devuelve el precio neto de un producto (o 0 si no existe)."""
    query = "SELECT precio_neto " "FROM precios " "WHERE id_producto = %s"
    res = _fetch_all(query, (id_prod,))
    return int(res[0][0]) if res else 0


def obtener_stock(id_prod: int) -> int:
    """Devuelve el stock disponible de un producto."""
    query = "SELECT stock " "FROM productos " "WHERE id_producto = %s"
    res = _fetch_all(query, (id_prod,))
    return int(res[0][0]) if res else 0


def descontar_stock(id_prod: int, cantidad: int) -> None:
    """Resta *cantidad* al stock del producto indicado."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
            (cantidad, id_prod),
        )


# ----- CRUD --------------------------------------------------------------
def crear(nombre: str, precio: int, stock: int) -> None:
    """Crea un nuevo producto con su precio inicial."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO productos (nombre, stock) VALUES (%s, %s) RETURNING id_producto",
            (nombre, stock),
        )
        id_prod = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO precios (id_producto, precio_neto) VALUES (%s, %s)",
            (id_prod, precio),
        )


def eliminar(id_prod: int) -> None:
    """Elimina un producto (y su precio) de la BD."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM precios WHERE id_producto=%s", (id_prod,))
        cur.execute("DELETE FROM productos WHERE id_producto=%s", (id_prod,))


def actualizar(id_prod: int, precio: int, stock: int) -> None:
    """Actualiza precio y stock de un producto existente."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE precios SET precio_neto=%s WHERE id_producto=%s",
            (precio, id_prod),
        )
        cur.execute(
            "UPDATE productos SET stock=%s WHERE id_producto=%s",
            (stock, id_prod),
        )


# ----- Listado y exportación --------------------------------------------
def listar(
    *, stock_bajo: bool = False, sin_precio: bool = False
) -> list[dict[str, Any]]:
    """Devuelve los productos filtrados.

    Args:
        stock_bajo: Solo productos con stock ≤ 30.
        sin_precio: Solo productos sin precio asignado.

    Returns:
        Lista de dicts con ``id``, ``nombre``, ``precio`` y ``stock``.
    """
    if stock_bajo:
        sql = """
            SELECT p.id_producto, p.nombre, pr.precio_neto, p.stock
            FROM productos p
            LEFT JOIN precios pr ON p.id_producto = pr.id_producto
            WHERE p.stock <= 30
            ORDER BY p.id_producto
        """
    elif sin_precio:
        sql = """
            SELECT p.id_producto, p.nombre, pr.precio_neto, p.stock
            FROM productos p
            LEFT JOIN precios pr ON p.id_producto = pr.id_producto
            WHERE pr.precio_neto IS NULL
            ORDER BY p.id_producto
        """
    else:
        sql = """
            SELECT p.id_producto, p.nombre, pr.precio_neto, p.stock
            FROM productos p
            LEFT JOIN precios pr ON p.id_producto = pr.id_producto
            ORDER BY p.id_producto
        """
    rows = _fetch_all(sql)
    return [
        {"id": r[0], "nombre": r[1], "precio": r[2] or 0, "stock": r[3]} for r in rows
    ]


def exportar_excel() -> str:
    """Exporta el inventario a *data/inventario_exportado.xlsx*.

    Returns:
        Ruta absoluta del archivo generado.
    """
    df = pd.DataFrame(listar())
    os.makedirs("data", exist_ok=True)
    path = os.path.abspath("data/inventario_exportado.xlsx")
    df.to_excel(path, index=False)
    return path
