# Análisis del Diagrama ER

Este documento describe la estructura de la base de datos `matex_db`, incluyendo tablas, columnas, relaciones y restricciones.

## 1. Tabla **productos**
- **Descripción**: Almacena la información básica de cada producto.
- **Columnas**:  
  - `id_producto` (INT): Clave primaria, identificador único de producto.  
  - `nombre` (TEXT): Nombre descriptivo del producto.  
  - `stock` (INT): Cantidad disponible en inventario. :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}

## 2. Tabla **precios**
- **Descripción**: Contiene los datos de precios asociados a productos.
- **Columnas**:  
  - `id_producto` (INT): Clave primaria y foránea, referencia a `productos.id_producto`.  
  - `precio_neto` (NUMERIC): Precio de venta sin impuestos.  
  - `costo_neto` (NUMERIC): Costo neto.  
  - `utilidad_neta` (NUMERIC): Ganancia neta.  
- **Relación**:  
  - 1 **Producto** ↔ 0..1 **Precios** (un producto puede tener cero o un registro de precio) :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}

## 3. Tabla **ventas**
- **Descripción**: Registra cada transacción de venta.
- **Columnas**:  
  - `id_venta` (INT): Clave primaria de la venta.  
  - `fecha` (DATE): Fecha de realización de la venta.  
  - `forma_pago` (TEXT): Medio de pago utilizado.  
  - `monto_total` (NUMERIC): Suma total de la venta.  
  - `total_productos` (INT): Número de ítems vendidos. :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}

## 4. Tabla **ventas_producto**
- **Descripción**: Detalle de productos incluidos en cada venta.
- **Columnas**:  
  - `id_venta` (INT): Clave foránea a `ventas.id_venta`.  
  - `id_producto` (INT): Clave foránea a `productos.id_producto`.  
  - `cantidad` (INT): Cantidad del producto vendido.  
  - `monto_producto` (NUMERIC): Precio total de ese producto en la venta.  
- **Relaciones**:  
  - 1 **Venta** ↔ * **ventas_producto** (una venta puede incluir múltiples productos) :contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}  
  - 1 **Producto** ↔ * **ventas_producto** (un producto puede aparecer en varias ventas) :contentReference[oaicite:8]{index=8}:contentReference[oaicite:9]{index=9}

## 5. Restricciones y claves
- **Claves primarias (PK)**:  
  - `productos.id_producto`  
  - `precios.id_producto`  
  - `ventas.id_venta`  
- **Claves foráneas (FK)**:  
  - `precios.id_producto` → `productos.id_producto`  
  - `ventas_producto.id_venta` → `ventas.id_venta`  
  - `ventas_producto.id_producto` → `productos.id_producto`
