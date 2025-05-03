"""Unit tests for the ProductoService class."""

import pytest

from services.producto_service import ProductoService


class DummyRepo:
    """Repositorio simulado para interceptar llamadas de ProductoService."""

    def __init__(self):
        """Inicializa las estructuras de seguimiento."""
        self.crear_args = None
        self.eliminar_args = None
        self.actualizar_args = None
        self.listar_called = False
        self.export_path = "/tmp/inv.xlsx"

    def crear(self, nombre, precio, stock):
        """Registra los parámetros recibidos para crear un producto."""
        self.crear_args = (nombre, precio, stock)

    def eliminar(self, id_prod):
        """Registra el ID del producto a eliminar."""
        self.eliminar_args = id_prod

    def actualizar(self, id_prod, precio, stock):
        """Registra los parámetros para actualizar un producto."""
        self.actualizar_args = (id_prod, precio, stock)

    def listar(self, *, stock_bajo=False, sin_precio=False):
        """Devuelve una lista de productos de ejemplo para pruebas."""
        self.listar_called = True
        return [{"id": 1, "nombre": "A", "precio": 10, "stock": 5}]

    def exportar_excel(self):
        """Simula la exportación a Excel devolviendo una ruta ficticia."""
        return self.export_path


@pytest.fixture
def svc(monkeypatch):
    """Proporciona un ProductoService con el DummyRepo parcheado."""
    service = ProductoService()
    dummy = DummyRepo()
    monkeypatch.setattr(service, "repo", dummy)
    return service, dummy


def test_listar_invoca_repo(svc):
    """Comprueba que listar() llama al método listar() del repositorio."""
    srv, rep = svc
    result = srv.listar(stock_bajo=True, sin_precio=False)
    assert rep.listar_called
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_alta_delegacion(svc):
    """Comprueba que alta() delega en crear() del repositorio."""
    srv, rep = svc
    srv.alta("ProdX", 123, 4)
    assert rep.crear_args == ("ProdX", 123, 4)


def test_baja_delegacion(svc):
    """Comprueba que baja() delega en eliminar() del repositorio."""
    srv, rep = svc
    srv.baja(99)
    assert rep.eliminar_args == 99


def test_modificar_delegacion(svc):
    """Comprueba que modificar() delega en actualizar() del repositorio."""
    srv, rep = svc
    srv.modificar(7, 55, 11)
    assert rep.actualizar_args == (7, 55, 11)


def test_exportar_excel(svc):
    """Comprueba que exportar_excel() devuelve la ruta del repositorio."""
    srv, rep = svc
    path = srv.exportar_excel()
    assert path == rep.export_path
