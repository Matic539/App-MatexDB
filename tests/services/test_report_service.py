from datetime import date, timedelta

import pandas as pd
import pytest

from services import report_service


def test_get_summary_report_rounding(monkeypatch):
    """Verifica que get_summary_report redondee correctamente al entero."""
    raw = {"ventas_netas": 123.6, "cantidad_ventas": 2, "ticket_promedio": 61.3}
    # Monkeypatch al repositorio
    monkeypatch.setattr(report_service, "fetch_summary", lambda s, e: raw)
    out = report_service.get_summary_report(date(2025, 5, 1), date(2025, 5, 2))
    assert out == {"ventas_netas": 124, "cantidad_ventas": 2, "ticket_promedio": 61}


def test_get_top_reports_rounding(monkeypatch):
    raw_q = [{"nombre": "A", "total_cantidad": 5.0}]
    raw_r = [{"nombre": "A", "total_ingresos": 250.7}]
    raw_p = [{"nombre": "A", "utilidad_total": 80.2}]
    monkeypatch.setattr(report_service, "fetch_top_quantity", lambda s, e: raw_q)
    monkeypatch.setattr(report_service, "fetch_top_revenue", lambda s, e: raw_r)
    monkeypatch.setattr(report_service, "fetch_top_profit", lambda s, e: raw_p)

    q = report_service.get_top_quantity_report(date(2025, 5, 1), date(2025, 5, 2))
    r = report_service.get_top_revenue_report(date(2025, 5, 1), date(2025, 5, 2))
    p = report_service.get_top_profit_report(date(2025, 5, 1), date(2025, 5, 2))

    assert q == [{"nombre": "A", "total_cantidad": 5}]
    assert r == [{"nombre": "A", "total_ingresos": 251}]
    assert p == [{"nombre": "A", "utilidad_total": 80}]


def test_export_report_excel(tmp_path):
    """Genera un Excel y comprueba su contenido."""
    data = {"Resumen": {"ventas_netas": 1000, "cantidad_ventas": 3, "ticket_promedio": 333}}
    out = tmp_path / "rep.xlsx"
    report_service.export_report(data, "excel", str(out))
    assert out.exists()
    # Lectura con pandas
    df = pd.read_excel(out, sheet_name="Resumen")
    assert list(df.columns) == ["Ventas Netas", "Cantidad Ventas", "Ticket Promedio"]
    assert df.iloc[0].to_list() == [1000, 3, 333]


def test_export_report_pdf(tmp_path):
    """Genera un PDF y comprueba que el archivo no está vacío."""
    data = {"Resumen": {"ventas_netas": 500, "cantidad_ventas": 2, "ticket_promedio": 250}}
    out = tmp_path / "rep.pdf"
    report_service.export_report(data, "pdf", str(out))
    assert out.exists() and out.stat().st_size > 0


def test_get_comparison_report_nonzero(monkeypatch):
    """Verifica variaciones cuando el periodo anterior tiene valores > 0."""
    # Datos de ejemplo
    actual = {"ventas_netas": 200, "cantidad_ventas": 4, "ticket_promedio": 50}
    anterior = {"ventas_netas": 100, "cantidad_ventas": 2, "ticket_promedio": 25}

    start = date(2025, 2, 1)
    end = date(2025, 2, 15)
    days = 15
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    def fake_get_summary(s, e):
        if s == start and e == end:
            return actual
        elif s == prev_start and e == prev_end:
            return anterior
        else:
            pytest.skip(f"Called with unexpected dates: {s}–{e}")

    monkeypatch.setattr(report_service, "get_summary_report", fake_get_summary)

    comp = report_service.get_comparison_report(start, end, days)
    assert comp["actual"] == actual
    assert comp["anterior"] == anterior

    # variaciones porcentuales
    assert comp["variacion"]["ventas_netas"] == pytest.approx((200 - 100) / 100)
    assert comp["variacion"]["cantidad_ventas"] == pytest.approx((4 - 2) / 2)
    assert comp["variacion"]["ticket_promedio"] == pytest.approx((50 - 25) / 25)


def test_get_comparison_report_zero_previous(monkeypatch):
    """Verifica que si el periodo anterior es cero, la variación sea 1.0 o 0.0."""
    actual = {"ventas_netas": 0, "cantidad_ventas": 0, "ticket_promedio": 0}
    anterior = {"ventas_netas": 0, "cantidad_ventas": 0, "ticket_promedio": 0}

    start = date(2025, 3, 1)
    end = date(2025, 3, 10)
    days = 5
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    def fake_get_summary(s, e):
        # siempre devolvemos el mismo dict mockeado
        return actual if (s == start and e == end) else anterior

    monkeypatch.setattr(report_service, "get_summary_report", fake_get_summary)

    comp = report_service.get_comparison_report(start, end, days)
    assert comp["actual"] == actual
    assert comp["anterior"] == anterior

    # Como anterior todos ceros:
    # - si actual > 0 variación = 1.0, pero aquí actual es cero → variación = 0.0
    for key, val in comp["variacion"].items():
        assert val == 0.0
