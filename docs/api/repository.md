# Repositorios

Esta sección documenta la capa de **Repositorios** (SQL puro) que encapsula los `SELECT`/`INSERT`/`UPDATE`/`DELETE` contra PostgreSQL.

---

## repository.db

Este módulo gestiona el _pool_ de conexiones y el contexto transaccional:

::: repository.db

---

## repository.producto_repo

Operaciones CRUD sobre la entidad **Producto** y su precio.

::: repository.producto_repo

---

## repository.ventas_repo

Operaciones CRUD y consultas sobre **Ventas** y su detalle (`ventas_producto`).

::: repository.ventas_repo
