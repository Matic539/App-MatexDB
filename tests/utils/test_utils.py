"""Unit tests for format and validation utilities."""

from decimal import Decimal

import pytest

from utils.format_utils import format_money
from utils.validation_utils import is_int, is_valid_date


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_, expected",
    [
        (1000, "$1,000"),  # entero
        (1234567.0, "$1,234,567"),  # float
        (Decimal("9876543"), "$9,876,543"),  # Decimal
        ("abc", "$0"),  # no numérico
    ],
)
def test_format_money(input_, expected):
    """Comprueba que format_money aplica coma como separador de miles."""
    assert format_money(input_) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "value, expected",
    [
        ("123", True),
        ("0", True),
        ("-5", True),
        ("abc", False),
        (None, False),
    ],
)
def test_is_int(value, expected):
    """Verifica que is_int detecta correctamente valores enteros válidos."""
    assert is_int(value) is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "date_str, fmt, expected",
    [
        ("2025-01-01", "%Y-%m-%d", True),
        ("01-01-2025", "%Y-%m-%d", False),
        ("2025/01/01", "%Y-%m-%d", False),
    ],
)
def test_is_valid_date(date_str, fmt, expected):
    """Valida que is_valid_date reconozca cadenas con el formato esperado."""
    assert is_valid_date(date_str, fmt) is expected
