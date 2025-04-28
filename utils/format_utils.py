"""format utils."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from locale import LC_NUMERIC, format_string, setlocale
from typing import SupportsFloat, SupportsInt

Num = int | float | Decimal | SupportsInt | SupportsFloat

setlocale(LC_NUMERIC, "")


def format_money(amount: Num, currency: str = "$") -> str:
    """Formatea un número con separador de miles y símbolo monetario."""
    try:
        value = Decimal(str(amount))  # ← cast a str para cualquier Num
    except (InvalidOperation, ValueError, TypeError):
        value = Decimal(0)

    formatted = format_string("%d", value, grouping=True)
    return f"{currency}{formatted}"
