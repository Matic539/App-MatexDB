"""Package utils."""

from .eliminar_tab import EliminarTab
from .historial_tab import HistorialTab
from .ingreso_tab import IngresoTab
from .inventario_tab import InventarioTab
from .reportes_tab import ReportesTab

__all__ = [
    "IngresoTab",
    "HistorialTab",
    "InventarioTab",
    "EliminarTab",
    "ReportesTab",
]
