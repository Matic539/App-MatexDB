from typing import List, Dict, Tuple
import pandas as pd
import os

from repository.db import get_conn

# ---------- Helpers ----------
def _fetch_all(sql: str, params=()) -> List[Tuple]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# ---------- API ----------
def obtener_productos():
    return _fetch_all("SELECT id_producto, nombre, stock FROM productos ORDER BY id_producto")

def obtener_precio(id_prod: int) -> int:
    res = _fetch_all("SELECT precio_neto FROM precios WHERE id_producto=%s", (id_prod,))
    return int(res[0][0]) if res else 0

def obtener_stock(id_prod: int) -> int:
    res = _fetch_all("SELECT stock FROM productos WHERE id_producto=%s", (id_prod,))
    return int(res[0][0]) if res else 0

def descontar_stock(id_prod: int, cantidad: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE productos SET stock=stock-%s WHERE id_producto=%s", (cantidad, id_prod))

# CRUD básico
def crear(nombre: str, precio: int, stock: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO productos (nombre, stock) VALUES (%s,%s) RETURNING id_producto", (nombre, stock))
        id_prod = cur.fetchone()[0]
        cur.execute("INSERT INTO precios (id_producto, precio_neto) VALUES (%s,%s)", (id_prod, precio))

def eliminar(id_prod: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM precios WHERE id_producto=%s", (id_prod,))
        cur.execute("DELETE FROM productos WHERE id_producto=%s", (id_prod,))

def actualizar(id_prod: int, precio: int, stock: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE precios SET precio_neto=%s WHERE id_producto=%s", (precio, id_prod))
        cur.execute("UPDATE productos SET stock=%s WHERE id_producto=%s", (stock, id_prod))

def listar(stock_bajo=False, sin_precio=False) -> List[Dict]:
    if stock_bajo:
        sql ="""SELECT p.id_producto, p.nombre, pr.precio_neto, p.stock
                FROM productos p LEFT JOIN precios pr ON p.id_producto=pr.id_producto
                WHERE p.stock<=30 ORDER BY p.id_producto"""
    elif sin_precio:
        sql ="""SELECT p.id_producto, p.nombre, pr.precio_neto, p.stock
                FROM productos p LEFT JOIN precios pr ON p.id_producto=pr.id_producto
                WHERE pr.precio_neto IS NULL ORDER BY p.id_producto"""
    else:
        sql ="""SELECT p.id_producto, p.nombre, pr.precio_neto, p.stock
                FROM productos p LEFT JOIN precios pr ON p.id_producto=pr.id_producto
                ORDER BY p.id_producto"""
    rows = _fetch_all(sql)
    return [dict(id=r[0], nombre=r[1], precio=r[2] or 0, stock=r[3]) for r in rows]

def exportar_excel() -> str:
    df = pd.DataFrame(listar())
    os.makedirs("data", exist_ok=True)
    path = "data/inventario_exportado.xlsx"
    df.to_excel(path, index=False)
    return os.path.abspath(path)