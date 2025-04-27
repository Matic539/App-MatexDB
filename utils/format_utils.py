from locale import setlocale, LC_NUMERIC, format_string
from decimal import Decimal
from typing import Union

setlocale(LC_NUMERIC, "")

def format_money(amount: Union[int, float, Decimal], currency: str = "$") -> str:
    try:
        value = Decimal(amount)
    except (ValueError, ArithmeticError):
        value = Decimal(0)
    formatted = format_string("%d", value, grouping=True)
    return f"{currency}{formatted}"