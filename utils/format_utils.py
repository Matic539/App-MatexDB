"""format utils."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import SupportsFloat, SupportsInt

Num = int | float | Decimal | SupportsInt | SupportsFloat


def format_money(amount: Num, currency: str = "$") -> str:
    """Formatea un número con coma como separador de miles y símbolo monetario."""
    try:
        # Convertimos a Decimal a partir de str para aceptar cualquier Num
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        value = Decimal(0)

    # formateo con coma agrupando miles, e.g. 1,000
    formatted = f"{int(value):,}"
    return f"{currency}{formatted}"
