"""Provide report generation and export utilities for the application."""

import os
from datetime import date

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# -------------------------------------------------------------------
# Service functions (implement or import from repository/report_repository)
# -------------------------------------------------------------------
def get_summary_report(start_date: date, end_date: date) -> dict:
    """Devuelve las métricas de resumen de ventas para el rango de fechas indicado."""
    # TODO: llamar a repository.report_repository.fetch_summary(...)
    raise NotImplementedError


def get_top_quantity_report(start_date: date, end_date: date) -> list[dict]:
    """Devuelve los top 5 productos por cantidad vendida en el rango de fechas indicado."""
    # TODO: llamar a repository.report_repository.fetch_top_quantity(...)
    raise NotImplementedError


def get_top_revenue_report(start_date: date, end_date: date) -> list[dict]:
    """Devuelve los top 5 productos por ingresos en el rango de fechas indicado."""
    # TODO: llamar a repository.report_repository.fetch_top_revenue(...)
    raise NotImplementedError


def get_top_profit_report(start_date: date, end_date: date) -> list[dict]:
    """Devolver productos ordenados por beneficio total en el rango de fechas indicado."""
    # TODO: llamar a repository.report_repository.fetch_top_profit(...)
    raise NotImplementedError


class ExportError(Exception):
    """Error al exportar reportes a archivos."""

    pass


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
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame(data)
            # Capitalizar títulos de columna
            df.columns = [col.replace("_", " ").title() for col in df.columns]
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        writer.save()


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
