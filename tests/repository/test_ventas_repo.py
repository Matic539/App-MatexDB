# tests/repository/test_ventas_repo.py

"""Integration tests for the ventas_repo module."""

import datetime
import sys

import pytest

from repository.producto_repo import crear as crear_prod
from repository.producto_repo import obtener_productos, obtener_stock
from repository.ventas_repo import detalle as detalle_venta
from repository.ventas_repo import eliminar_venta, insertar_venta
from repository.ventas_repo import listar as listar_ventas

if sys.platform.startswith("win"):
    pytest.skip(
        "Tests de integración con PostgreSQL sólo en entornos POSIX (Linux/CI)",
        allow_module_level=True,
    )


@pytest.mark.integration
def test_ventas_crud(postgres_db):
    """Test CRUD on ventas_repo and ensure stock is adjusted and restored."""
    # --- Pre: crear un producto para vender ---
    crear_prod("ProdParaVenta", precio=100, stock=20)
    prods = obtener_productos()
    idp, nombre, stock_inicial = prods[-1]
    assert nombre == "ProdParaVenta"
    assert stock_inicial == 20

    # --- 1) Insertar una venta con ese producto ---
    fecha = datetime.date.today().strftime("%Y-%m-%d")
    venta = {
        "fecha": fecha,
        "forma_pago": "efectivo",
        "monto_total": 200,
        "total_productos": 2,
    }
    items = [{"id_producto": idp, "cantidad": 2, "monto_producto": 200}]
    id_venta = insertar_venta(venta, items)
    assert isinstance(id_venta, int)

    # --- 2) Listar ventas y comprobar que aparece la nuestra ---
    ventas = listar_ventas()
    matched = [v for v in ventas if v["id"] == id_venta]
    assert len(matched) == 1
    v = matched[0]
    assert v["forma"] == venta["forma_pago"]
    assert v["total_prod"] == 2
    assert int(v["monto"]) == 200

    # --- 3) Consultar detalle de la venta ---
    detalles = detalle_venta(id_venta)
    assert len(detalles) == 1
    det = detalles[0]
    assert det["nombre"] == "ProdParaVenta"
    assert det["cantidad"] == 2

    # --- 4) El stock se debe haber descontado ---
    stock_despues = obtener_stock(idp)
    assert stock_despues == stock_inicial - 2

    # --- 5) Eliminar la venta y comprobar restauración de stock ---
    eliminar_venta(id_venta)
    assert obtener_stock(idp) == stock_inicial
    assert all(v["id"] != id_venta for v in listar_ventas())
