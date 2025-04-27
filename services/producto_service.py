from repository import producto_repo

class ProductoService:
    def __init__(self):
        self.repo = producto_repo

    # ----- API -----
    def listar(self, stock_bajo=False, sin_precio=False):
        return self.repo.listar(stock_bajo, sin_precio)

    def alta(self, nombre: str, precio: int, stock: int):
        self.repo.crear(nombre, precio, stock)

    def baja(self, id_prod: int):
        self.repo.eliminar(id_prod)

    def modificar(self, id_prod: int, precio: int, stock: int):
        self.repo.actualizar(id_prod, precio, stock)

    def exportar_excel(self) -> str:
        return self.repo.exportar_excel()