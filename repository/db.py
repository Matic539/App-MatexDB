from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from decouple import config

_DB_URL = dict(
    dbname=config("DB_NAME"),
    user=config("DB_USER"),
    password=config("DB_PASSWORD"),
    host=config("DB_HOST", default="localhost"),
    port=config("DB_PORT", cast=int, default=5432),
)

_pool: Optional[SimpleConnectionPool] = None

def init_pool(minconn=1, maxconn=10):
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn, maxconn, **_DB_URL)

@contextmanager
def get_conn():
    if _pool is None:
        init_pool()
    conn = _pool.getconn()  # type: ignore[arg-type]
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)