"""Manejo de conexiones PostgreSQL (capa *Repository*).

Contiene un pool global de conexiones y un *context manager* `get_conn`
que garantiza **commit/rollback** y la devolución segura al pool.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from decouple import config
from psycopg2.extensions import connection
from psycopg2.pool import SimpleConnectionPool

# -------------------------------------------------------------------------
# Configuración de la cadena de conexión
# -------------------------------------------------------------------------
_DB_URL: dict[str, str | int] = {
    "dbname": config("DB_NAME", default="matex_db"),
    "user": config("DB_USER", default="postgres"),
    "password": config("DB_PASSWORD", default=""),
    "host": config("DB_HOST", default="localhost"),
    "port": config("DB_PORT", cast=int, default=5432),
}

_pool: Optional[SimpleConnectionPool] = None


# -------------------------------------------------------------------------
# API pública
# -------------------------------------------------------------------------
def init_pool(minconn: int = 1, maxconn: int = 10) -> None:
    """Inicializa el pool global de conexiones.

    Args:
        minconn: Conexiones mínimas a mantener.
        maxconn: Conexiones máximas permitidas.

    Side effects:
        Crea la variable global ``_pool`` si aún no existe.

    Raises:
        psycopg2.Error: Si la conexión a la BD falla.
    """
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn, maxconn, **_DB_URL)


@contextmanager
def get_conn() -> Generator[connection, None, None]:
    """Context manager que entrega una conexión del pool."""
    if _pool is None:
        init_pool()

    # Garantiza al type-checker que _pool ya no es None
    assert _pool is not None, "El pool de conexiones no está inicializado"

    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)
