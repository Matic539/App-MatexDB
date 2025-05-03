"""Unit tests for the VentasService class."""

from decimal import ROUND_HALF_UP, Decimal

import pytest

from services.ventas_service import StockError, VentasService


class DummyRepoVenta:
    """Repositorio simulado para operaciones de venta."""

    def __init__(self):
        """Inicializa las estructuras de control de DummyRepoVenta."""
        self.inserted = None
        self.deleted = None

    def insertar_venta(self, venta_dict, items):
        """Simula la inserción de una venta y almacena los datos."""
        self.inserted = (venta_dict, list(items))
        return 555

    def eliminar_venta(self, id_venta):
        """Simula la eliminación de una venta registrando el id."""
        self.deleted = id_venta


class DummyRepoProd:
    """Repositorio simulado para operaciones de producto (precio y stock)."""

    def __init__(self):
        """Inicializa las estructuras de control de DummyRepoProd."""
        self.descontados = []

    def obtener_precio(self, id_prod):
        """Devuelve un precio fijo (200) para cualquier producto."""
        return 200

    def descontar_stock(self, id_prod, cantidad):
        """Simula el descuento de stock almacenando la llamada."""
        self.descontados.append((id_prod, cantidad))


@pytest.fixture
def svc(monkeypatch):
    """Provee un VentasService parcheado con repositorios DummyRepoProd y DummyRepoVenta."""
    service = VentasService()
    repoV = DummyRepoVenta()
    repoP = DummyRepoProd()
    monkeypatch.setattr(service, "producto_repo", repoP)
    monkeypatch.setattr("services.ventas_service.ventas_repo", repoV)
    return service, repoP, repoV


def test_preparar_items_stock_insuficiente(svc):
    """Debería lanzar StockError si la cantidad supera el stock disponible."""
    srv, repoP, _ = svc
    cantidades = {
        1: {
            "var": type("V", (), {"get": lambda self: "5"})(),
            "nombre": "X",
            "stock": 3,
        }
    }
    with pytest.raises(StockError):
        srv.preparar_items_venta(cantidades)


def test_preparar_items_correcto(svc):
    """Genera correctamente los items con IVA y cantidades válidas."""
    srv, repoP, _ = svc
    cantidades = {
        2: {
            "var": type("V", (), {"get": lambda self: "2"})(),
            "nombre": "Y",
            "stock": 5,
        }
    }
    items = srv.preparar_items_venta(cantidades)
    assert len(items) == 1
    it = items[0]
    assert it["id_producto"] == 2
    assert it["cantidad"] == 2
    esperado = int(Decimal(200 * 1.19 * 2).quantize(0, ROUND_HALF_UP))
    assert it["monto_producto"] == esperado


def test_crear_venta_invoca_repos(svc):
    """Crea una venta, delega en el repo y descuenta stock en producto_repo."""
    srv, repoP, repoV = svc
    items = [
        {"id_producto": 1, "cantidad": 1, "monto_producto": 238},
        {"id_producto": 3, "cantidad": 2, "monto_producto": 476},
    ]
    vid = srv.crear_venta(fecha="2025-05-02", forma_pago="tarjeta", items=items)
    assert vid == 555

    venta_dict, passed_items = repoV.inserted
    assert venta_dict["fecha"] == "2025-05-02"
    assert venta_dict["forma_pago"] == "tarjeta"
    assert venta_dict["monto_total"] == 238 + 476
    assert venta_dict["total_productos"] == 1 + 2

    # Verifica que descontó stock sobre producto_repo
    assert set(repoP.descontados) == {(1, 1), (3, 2)}
