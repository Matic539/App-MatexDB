"""validation utils."""

from __future__ import annotations

from datetime import datetime


def is_int(value: object) -> bool:
    """Devuelve ``True`` si *value* puede convertirse a ``int``."""
    try:
        # acepta objetos convertibles
        int(value)  # type: ignore[call-overload]
        return True
    except (ValueError, TypeError):
        return False


def is_valid_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
    """Valida si la cadena coincide con el formato de fecha."""
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False
