# Uso rápido

En esta guía recorrerás el flujo típico: registrar una venta, consultar el historial y actualizar inventario.  
Las capturas corresponden a la versión `v0.1.0`; tu pantalla puede variar ligeramente.

---

## 1. Ingreso de Ventas

![Ingreso de Ventas]

1. **Selecciona la fecha** (por defecto hoy).  
2. **Escoge la forma de pago** en el desplegable.  
3. Para cada producto introduce la **cantidad** vendida.  
   *El stock disponible se muestra entre paréntesis.*  
4. Pulsa **🔄** si agregaste productos nuevos y quieres refrescar la lista.  
5. Haz clic en **Confirmar venta** para ver el resumen:  
   - Total de artículos  
   - Monto con IVA (19 %)  
6. Revisa y, si todo es correcto, pulsa **Guardar venta**.  
   Aparecerá un mensaje ✅ y el stock se descuenta automáticamente.

---

## 2. Historial de Ventas

![Historial]

- El panel superior permite filtrar por **rango de fechas**.  
- Doble clic en cualquier fila para abrir el **detalle de productos**.  
- **Exportar a Excel** genera `data/ventas_exportadas.xlsx` con todas las columnas.

---

## 3. Control de Inventario

![Inventario]

| Botón | Acción |
|-------|--------|
| **Ver todos** | Lista completa de productos |
| **Stock bajo** | Solo artículos con ≤ 30 unidades |
| **Sin precio** | Productos sin valor asignado |
| **Exportar a Excel** | Guarda el inventario en `data/inventario_exportado.xlsx` |
| **Agregar Producto** | Abre ventana para nombre, precio y stock inicial |
| *(Doble clic en una fila)* | Edita precio y stock |

Para eliminar un producto, selecciónalo y pulsa **Eliminar Producto**.

---

## 4. Uso de la pestaña Reportes

La pestaña **Reportes** permite generar y exportar métricas de ventas en un rango de fechas:

1. Haz clic en **Reportes** en la barra de pestañas.  
2. Selecciona la **Fecha inicio** y **Fecha fin** con los DatePickers.  
3. Pulsa **Generar reporte**:
   - Se mostrarán cuatro tablas:  
     - **Resumen**: ventas netas, cantidad de ventas y ticket promedio.  
     - **Top Cantidad**: productos más vendidos por unidades.  
     - **Top Ingresos**: productos con mayores ingresos netos.  
     - **Top Utilidad**: productos con mayor utilidad neta.
4. Pulsa **Exportar Excel** o **Exportar PDF** para descargar el informe en el formato deseado.
5. Los valores están calculados sobre precio neto (sin IVA), redondeados a entero y formateados con separador de miles (por ejemplo, `1,234,567`).

---

## 5. Eliminar Ventas

En la pestaña **Eliminar Ventas** introduce el **ID de venta** y pulsa **Eliminar**.  
El stock de cada producto se restaura automáticamente.

![Eliminar]

---

## 6. Atajos de teclado

| Acción                     | Tecla |
|----------------------------|-------|
| Desplazarse por productos  | Rueda del ratón |
| Refrescar lista de productos | `Ctrl + R` *(equivale al botón 🔄)* |
| Cerrar ventana de detalle  | `Esc` |

---

## 7. Directorios generados

| Carpeta / Archivo            | Contenido |
|------------------------------|-----------|
| `data/ventas_exportadas.xlsx` | Historial exportado |
| `data/inventario_exportado.xlsx` | Inventario exportado |
| `logs/` (opcional) | Registro de errores si habilitas logging |
| `.env` | Variables de conexión a BD |

---

## 8. Preguntas frecuentes

<details>
<summary>¿Puedo anular solo un producto dentro de una venta?</summary>

Por ahora no: debes eliminar la venta completa y volver a ingresarla
con los productos corregidos. Esta funcionalidad se añadirá en futuras versiones.
</details>

<details>
<summary>¿Cómo imprimo un recibo?</summary>

En la versión prototipo no hay impresión directa.
Como alternativa exporta a Excel y genera tu formato desde allí.
</details>

---

_Si encuentras algún bug o tienes sugerencias, crea un
[Issue en GitHub](https://github.com/Matic539/App-MatexDB/issues) o
envía un correo a **matias.lopez.renato@gmail.com**._
