"""Integration tests for the producto_repo module."""

import sys

import pytest

from repository.producto_repo import (
    actualizar,
    crear,
    eliminar,
    listar,
    obtener_precio,
    obtener_productos,
    obtener_stock,
)

if sys.platform.startswith("win"):
    pytest.skip(
        "Tests de integración con PostgreSQL sólo en entornos POSIX (Linux/CI)",
        allow_module_level=True,
    )


@pytest.mark.integration
def test_producto_crud(postgres_db):
    """Test CRUD operations on producto_repo: create, read, update and delete."""
    # 1) No debería haber productos inicialmente
    assert listar() == []

    # 2) Creamos uno y recuperamos su ID
    crear("TestProd", precio=150, stock=10)
    prods = obtener_productos()
    assert len(prods) == 1
    idp, nombre, stock = prods[0]
    assert nombre == "TestProd"
    assert stock == 10

    # 3) Precio y stock vía funciones
    assert obtener_precio(idp) == 150
    assert obtener_stock(idp) == 10

    # 4) Actualizamos
    actualizar(idp, precio=200, stock=5)
    assert obtener_precio(idp) == 200
    assert obtener_stock(idp) == 5

    # 5) Eliminar y verificar que ya no está
    eliminar(idp)
    assert listar() == []
