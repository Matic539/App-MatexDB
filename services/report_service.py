"""Proporciona utilidades de generación y exportación de informes para la aplicación."""

import os
from datetime import date, timedelta

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from repository.report_repository import (
    fetch_summary,
    fetch_top_profit,
    fetch_top_quantity,
    fetch_top_revenue,
)


class ExportError(Exception):
    """Error al exportar reportes a archivos."""

    pass


def get_summary_report(start_date: date, end_date: date) -> dict:
    """Obtiene los totales de venta, cantidad de ventas y ticket promedio para el rango de fechas indicado."""
    raw = fetch_summary(start_date, end_date)
    # Redondear y convertir a entero
    return {
        "ventas_netas": int(round(raw["ventas_netas"])),
        "cantidad_ventas": int(raw["cantidad_ventas"]),
        "ticket_promedio": int(round(raw["ticket_promedio"])),
    }


def get_top_quantity_report(start_date: date, end_date: date) -> list[dict]:
    """Obtiene los 5 productos con mayor cantidad vendida en el rango de fechas indicado."""
    items = fetch_top_quantity(start_date, end_date)
    return [{"nombre": i["nombre"], "total_cantidad": int(i["total_cantidad"])} for i in items]


def get_top_revenue_report(start_date: date, end_date: date) -> list[dict]:
    """Obtiene los 5 productos que generaron mayores ingresos netos en el rango de fechas indicado."""
    items = fetch_top_revenue(start_date, end_date)
    # redondear ingresos a entero
    return [{"nombre": i["nombre"], "total_ingresos": int(round(i["total_ingresos"]))} for i in items]


def get_top_profit_report(start_date: date, end_date: date) -> list[dict]:
    """Obtiene los productos ordenados por utilidad neta total en el rango de fechas indicado."""
    items = fetch_top_profit(start_date, end_date)
    # redondear utilidad a entero
    return [{"nombre": i["nombre"], "utilidad_total": int(round(i["utilidad_total"]))} for i in items]


def get_comparison_report(start_date: date, end_date: date, days: int) -> dict:
    """
    Obtiene un comparativo entre el periodo actual y el periodo anterior.

    Args:
        start_date: Fecha de inicio del periodo actual.
        end_date:   Fecha de fin del periodo actual.
        days:       Número de días hacia atrás para el periodo anterior.

    Returns:
        {
            "actual":    {...},  # {'ventas_netas': int, 'cantidad_ventas': int, 'ticket_promedio': int}
            "anterior":  {...},  # mismos keys para el periodo anterior
            "variacion": {...}   # variación porcentual: (actual - anterior) / anterior
        }
    """
    # Definir rango anterior: termina justo un día antes del inicio actual
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    # Resúmenes ya redondeados e formateados por get_summary_report
    actual = get_summary_report(start_date, end_date)
    anterior = get_summary_report(prev_start, prev_end)
    # Calcular variaciones porcentuales
    variacion = {}
    for key in actual:
        prev = anterior.get(key, 0)
        curr = actual.get(key, 0)
        if prev:
            variacion[key] = (curr - prev) / prev
        else:
            variacion[key] = 1.0 if curr else 0.0
    return {"actual": actual, "anterior": anterior, "variacion": variacion}


def export_report(report_data: dict, format: str, destination_path: str) -> str:
    """
    Genera un archivo (Excel o PDF) con los datos de report data.

    Args:
        report_data: Diccionario con claves de pestañas y valores dict o list.
        format: 'excel' o 'pdf'.
        destination_path: Ruta completa donde guardar el archivo.

    Returns:
        La misma destination_path si tuvo éxito.

    Raises:
        ExportError: Cualquier fallo durante la generación o escritura.
    """
    try:
        dirname = os.path.dirname(destination_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        if format == "excel":
            _export_to_excel(report_data, destination_path)
        elif format == "pdf":
            _export_to_pdf(report_data, destination_path)
        else:
            raise ExportError(f"Formato '{format}' no soportado.")
    except Exception as e:
        raise ExportError(f"No se pudo exportar el reporte: {e}")
    return destination_path


def _export_to_excel(report_data: dict, path: str):
    """H interno: escribe report data a un Excel con una hoja por sección."""
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        for sheet_name, data in report_data.items():
            if sheet_name == "Comparativo":
                # data tiene keys "actual","anterior","variacion"
                # armamos filas por métrica
                rows = []
                for key, actual in data["actual"].items():
                    anterior = data["anterior"][key]
                    vari = data["variacion"][key]
                    rows.append({"Métrica": key.replace("_", " ").title(), "Actual": actual, "Anterior": anterior, "Variación (%)": f"{vari:.2%}"})
                df = pd.DataFrame(rows)
            else:
                # resto de hojas igual que antes
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                else:
                    df = pd.DataFrame(data)
                df.columns = [col.replace("_", " ").title() for col in df.columns]
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)


def _export_to_pdf(report_data: dict, path: str):
    """H interno: escribe report data a un PDF con tablas y títulos."""
    doc = SimpleDocTemplate(path, pagesize=landscape(letter), title="Reporte de Ventas")
    styles = getSampleStyleSheet()
    story = []

    for title, data in report_data.items():
        # Título de sección
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Spacer(1, 12))

        # Preparar datos para la tabla
        if title == "Comparativo":
            cols = ["Métrica", "Actual", "Anterior", "Variación (%)"]
            rows = []
            for key, actual in data["actual"].items():
                anterior = data["anterior"][key]
                vari = f"{data['variacion'][key]:.2%}"
                rows.append([key.replace("_", " ").title(), actual, anterior, vari])
        else:
            if isinstance(data, dict):
                cols = list(data.keys())
                rows = [list(data.values())]
            else:
                cols = list(data[0].keys()) if data else []
                rows = [list(item.values()) for item in data]

        table_data = [cols] + rows
        tbl = Table(table_data, hAlign="CENTER")
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(tbl)
        story.append(Spacer(1, 24))

    doc.build(story)
