# Servicios

La capa de **Services** orquesta la lógica de negocio: valida reglas (stock, totales, IVA) y delega en los repositorios.

---

## services.producto_service

Encapsula las operaciones CRUD de productos y precio, añadiendo validaciones simples.

::: services.producto_service

---

## services.ventas_service

Gestiona la creación y eliminación de ventas: prepara los items, aplica IVA, persiste la venta y ajusta stock.

::: services.ventas_service
