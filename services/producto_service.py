"""Reglas de negocio relacionadas con productos (stock y precios)."""

from __future__ import annotations

from repository import producto_repo


class ProductoService:
    """Facade sobre `producto_repo` para encapsular reglas simples de negocio."""

    def __init__(self) -> None:
        self.repo = producto_repo

    # ------------------------------------------------------------------ API
    def listar(self, *, stock_bajo: bool = False, sin_precio: bool = False) -> list[dict[str, int | str]]:
        """Devuelve productos según filtros.

        Args:
            stock_bajo: Solo productos con stock ≤ 30.
            sin_precio: Solo productos sin precio asignado.

        Returns:
            Lista de diccionarios con ``id``, ``nombre``, ``precio`` y ``stock``.
        """
        return self.repo.listar(stock_bajo=stock_bajo, sin_precio=sin_precio)

    def alta(self, nombre: str, precio: int, stock: int) -> None:
        """Crea un producto nuevo."""
        self.repo.crear(nombre, precio, stock)

    def baja(self, id_prod: int) -> None:
        """Elimina un producto por ID (cascada borra el precio)."""
        self.repo.eliminar(id_prod)

    def modificar(self, id_prod: int, precio: int, stock: int) -> None:
        """Actualiza precio y stock de un producto existente."""
        self.repo.actualizar(id_prod, precio, stock)

    def exportar_excel(self) -> str:
        """Genera un archivo Excel con el inventario.

        Returns:
            Ruta absoluta del archivo creado.
        """
        return self.repo.exportar_excel()
