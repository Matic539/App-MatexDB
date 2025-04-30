# Instalación

> **Tiempo estimado:** 5 – 10 min  
> Funciona en **Windows, macOS y Linux**. Solo necesitas Python ≥ 3.11 y una
> instancia local de PostgreSQL (o remota si ya la tienes).

---

## 1. Requisitos

| Software | Versión mínima | Comprobación |
|----------|----------------|--------------|
| Python   | 3.11           | `python --version` |
| pip      | 23             | `pip --version` |
| Git      | 2.30           | `git --version` |
| PostgreSQL | 13           | `psql --version` |

> En Windows puedes instalar **Python** desde
> <https://www.python.org/> y **PostgreSQL** con
> <https://www.postgresql.org/download/>.<br>
> Asegúrate de marcar “Add Python to PATH” y anotar la contraseña de `postgres`
> durante la instalación de Postgres.

---

## 2. Clona el repositorio

```bash
git clone https://github.com/Matic539/App-MatexDB.git
cd App-MatexDB
```

---

## 3. Crea y activa un entorno virtual

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
> Verás el prefijo (venv) en la consola.<br>
> Para salir del entorno más tarde: deactivate.

---

## 4. Instala dependencias

```bash
pip install -r requirements.txt
```
Si vas a trabajar en el código (hooks, docs, tests):
```bash
pip install -r requirements-dev.txt
pre-commit install   # activa los hooks de calidad
```

---

## 5. Copia y edita el archivo .env

```bash
cp .env.example .env
```
Abre .env y ajusta si es necesario:
```bash
DB_NAME=matex_db
DB_USER=postgres
DB_PASSWORD=postgres   # ← tu contraseña
DB_HOST=localhost
DB_PORT=5432
```

---

## 6. Prepara la base de datos

2. Crea la BD y las tablas:
(En la carpeta db/ se encuentra el schema.sql de la database.)

---

## 7. Lanza la aplicación

```bash
python -m app.main
```
> La ventana Matex vX.Y.Z — Administrador de Ventas debería abrirse sin errores.

---

## 8. Actualizar dependencias

```bash
pip list --outdated        # muestra paquetes
pip install -U <paquete>   # actualiza uno
```

---

## 9. Desinstalar / limpiar

```bash
deactivate         # sale del venv
rm -rf venv        # elimina el entorno virtual
```


