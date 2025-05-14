import pytest
from datetime import date
from repository import report_repository

class FakeCursor:
    def __init__(self, one=None, all_=None):
        self._one = one
        self._all = all_
    def execute(self, sql, params):
        """Stubbear la ejecución de la consulta."""
        return None
    def fetchone(self):
        """Devolver el resultado único mockeado."""
        return self._one
    def fetchall(self):
        """Devolver la lista mockeada."""
        return self._all
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

class FakeConn:
    def __init__(self, cursor):
        self._cursor = cursor
    def cursor(self, cursor_factory=None):
        return self._cursor
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

@pytest.fixture
def fake_summary_conn(monkeypatch):
    """Mockea get_conn para devolver un resultado de fetch_summary."""
    example = {'ventas_netas': 100, 'cantidad_ventas': 2, 'ticket_promedio': 50}
    cursor = FakeCursor(one=example)
    conn = FakeConn(cursor)
    monkeypatch.setattr(report_repository, 'get_conn', lambda: conn)
    return example

def test_fetch_summary_returns_correct_dict(fake_summary_conn):
    res = report_repository.fetch_summary(date(2025,5,1), date(2025,5,2))
    assert res == fake_summary_conn

@pytest.fixture
def fake_list_conn(monkeypatch):
    """Mockea get_conn para devolver resultados de las consultas de lista."""
    example = [{'nombre': 'X', 'total_cantidad': 3}]
    cursor = FakeCursor(all_=example)
    conn = FakeConn(cursor)
    monkeypatch.setattr(report_repository, 'get_conn', lambda: conn)
    return example

def test_fetch_top_quantity_returns_list(fake_list_conn):
    res = report_repository.fetch_top_quantity(date(2025,5,1), date(2025,5,2))
    assert res == fake_list_conn

def test_fetch_top_revenue_returns_list(fake_list_conn):
    res = report_repository.fetch_top_revenue(date(2025,5,1), date(2025,5,2))
    assert res == fake_list_conn

def test_fetch_top_profit_returns_list(fake_list_conn):
    res = report_repository.fetch_top_profit(date(2025,5,1), date(2025,5,2))
    assert res == fake_list_conn