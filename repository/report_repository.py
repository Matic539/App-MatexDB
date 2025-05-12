"""Operaciones de acceso a datos para generación de reportes de ventas."""

from datetime import date
from typing import Dict, List

from psycopg2.extras import RealDictCursor

from repository.db import get_conn


def fetch_summary(start_date: date, end_date: date) -> Dict[str, float]:
    """Devuelve el total de ventas netas, la cantidad de ventas y el ticket promedio en el rango de fechas indicado."""
    sql = """
        SELECT
            COALESCE(SUM(vp.cantidad * pr.precio_neto), 0)::numeric AS ventas_netas,
            (SELECT COUNT(*) FROM ventas WHERE fecha BETWEEN %s AND %s) AS cantidad_ventas,
            CASE
                WHEN (SELECT COUNT(*) FROM ventas
                    WHERE fecha BETWEEN %s AND %s) = 0
                THEN 0.0
                ELSE COALESCE(SUM(vp.cantidad * pr.precio_neto), 0)::numeric / (SELECT COUNT(*) FROM ventas WHERE fecha BETWEEN %s AND %s)
            END AS ticket_promedio
            FROM ventas_producto vp
            JOIN ventas v   ON vp.id_venta    = v.id_venta
            JOIN precios pr ON vp.id_producto = pr.id_producto
            WHERE v.fecha BETWEEN %s AND %s;
    """
    params = (
        start_date,
        end_date,  # para COUNT ventas
        start_date,
        end_date,  # para CASE … COUNT ventas
        start_date,
        end_date,  # para cálculo ticket_promedio
        start_date,
        end_date,  # para la suma neta en el FROM
    )
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_top_quantity(start_date: date, end_date: date) -> List[Dict[str, int]]:
    """Devuelve los 5 productos con mayor cantidad vendida en el rango de fechas indicado."""
    sql = """
        SELECT
            p.nombre,
            SUM(vp.cantidad)::INT AS total_cantidad
        FROM ventas_producto vp
        JOIN ventas v ON vp.id_venta = v.id_venta
        JOIN productos p ON vp.id_producto = p.id_producto
        WHERE v.fecha BETWEEN %s AND %s
        GROUP BY p.nombre
        ORDER BY total_cantidad DESC
        LIMIT 5;
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (start_date, end_date))
        return cur.fetchall()


def fetch_top_revenue(start_date: date, end_date: date) -> List[Dict[str, float]]:
    """Devuelve los 5 productos que generaron mayores ingresos netos en el rango de fechas indicado."""
    sql = """
        SELECT
            p.nombre,
            COALESCE(SUM(vp.cantidad * pr.precio_neto), 0) AS total_ingresos
        FROM ventas_producto vp
        JOIN ventas v ON vp.id_venta = v.id_venta
        JOIN precios pr ON vp.id_producto = pr.id_producto
        JOIN productos p ON vp.id_producto = p.id_producto
        WHERE v.fecha BETWEEN %s AND %s
        GROUP BY p.nombre
        ORDER BY total_ingresos DESC
        LIMIT 5;
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (start_date, end_date))
        return cur.fetchall()


def fetch_top_profit(start_date: date, end_date: date) -> List[Dict[str, float]]:
    """Devuelve los productos ordenados por utilidad neta total (cantidad * utilidad_neta) en el rango de fechas indicado."""
    sql = """
        SELECT
            p.nombre,
            COALESCE(SUM(vp.cantidad * pr.utilidad_neta), 0) AS utilidad_total
        FROM ventas_producto vp
        JOIN ventas v ON vp.id_venta = v.id_venta
        JOIN productos p ON vp.id_producto = p.id_producto
        JOIN precios pr ON p.id_producto = pr.id_producto
        WHERE v.fecha BETWEEN %s AND %s
        GROUP BY p.nombre
        ORDER BY utilidad_total DESC;
    """
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (start_date, end_date))
        return cur.fetchall()
