"""Fixtures para pytest: integra pytest-postgresql y carga el esquema SQL de test."""

import os

import pytest

import repository.db as db_mod

pytest_plugins = ["pytest_postgresql"]


@pytest.fixture
def postgres_db(postgresql):
    """Fixture de integración.

    Arranca un Postgres de prueba, setea las vars de entorno para repository.db,
    reinicia el pool y carga el esquema.
    """
    # 1) Leer datos de conexión
    dsn = postgresql.dsn()

    # 2) Poner en env vars para decouple
    os.environ["DB_NAME"] = dsn["dbname"]
    os.environ["DB_USER"] = dsn["user"]
    os.environ["DB_PASSWORD"] = dsn.get("password", "")
    os.environ["DB_HOST"] = dsn.get("host", "localhost")
    os.environ["DB_PORT"] = str(dsn["port"])

    # 3) Forzar recreación del pool con la nueva config
    db_mod._pool = None

    # 4) Cargar tu esquema SQL
    schema = open("db/schema.sql", encoding="utf-8").read()
    conn = postgresql
    cur = conn.cursor()
    cur.execute(schema)
    conn.commit()
    cur.close()

    yield postgresql
    # teardown automático del fixture postgresql
