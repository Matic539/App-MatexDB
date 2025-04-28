<h1 align="center">Matex – Administrador de Ventas y Stock</h1>

<p align="center">
  <em>Prototipo de escritorio construido en Python + Tkinter • PostgreSQL local (fase beta)</em>
</p>

![ci-badge](https://img.shields.io/github/actions/workflow/status/<TU-USUARIO>/MatexApp/ci.yml?branch=main)
![version](https://img.shields.io/badge/version-1.0.0-blue)

---

## ✨ Funcionalidades

- Ingreso de ventas con cálculo de IVA y control de stock
- Historial con filtros de fecha y exportación a Excel
- Inventario editable (alta, baja, modificación, filtros)
- Eliminación de ventas con reversión automática de stock
- Arquitectura en capas (UI / Services / Repository) lista para pruebas y escalado

## 🚀 Stack técnico

| Capa | Tecnología |
|------|------------|
| GUI  | **Tkinter** + ttk |
| BD   | **PostgreSQL 15** (local) |
| ORM  | SQL sin ORM (psycopg2.pool) |
| Empaquetado | PyInstaller |
| Docs | Sphinx / MkDocs |
| CI   | GitHub Actions |
