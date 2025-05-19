"""Proporciona la pestaña de interfaz de usuario para generar y exportar informes de ventas."""

from datetime import timedelta
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry

from services.report_service import (
    ExportError,
    export_report,
    get_summary_report,
    get_top_profit_report,
    get_top_quantity_report,
    get_top_revenue_report,
)


class ReportesTab(ttk.Frame):
    """Crea una pestaña que contiene controles y tablas para la generación y exportación de informes de ventas."""

    def __init__(self, master, *args, **kwargs):
        """Initialize the report tab UI with date selectors, buttons, and tables."""
        super().__init__(master, *args, **kwargs)

        # ─── Selección de rango de fechas ─────────────────────────────────────────
        ttk.Label(self, text="Fecha inicio:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_inicio = DateEntry(self, date_pattern="yyyy-MM-dd")
        self.date_inicio.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Fecha fin:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.date_fin = DateEntry(self, date_pattern="yyyy-MM-dd")
        self.date_fin.grid(row=0, column=3, padx=5, pady=5)

        # ─── Spinbox Días comparación ───────────────────────────────────────────────
        ttk.Label(self, text="Días comparación:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.spin_days = ttk.Spinbox(self, from_=0, to=365, width=5)
        self.spin_days.grid(row=0, column=5, padx=5, pady=5)
        # Inicializar en 0 para que .get() no devuelva cadena vacía
        self.spin_days.insert(0, "0")

        # ─── Botón Generar reporte ─────────────────────────────────────────────────
        self.btn_generar = ttk.Button(self, text="Generar reporte", command=self.on_generate_report)
        self.btn_generar.grid(row=0, column=6, padx=5, pady=5)

        # ─── Botones de exportación (inicialmente deshabilitados) ────────────────
        self.btn_export_excel = ttk.Button(self, text="Exportar Excel", command=self.on_export_excel, state="disabled")
        self.btn_export_excel.grid(row=2, column=2, padx=5, pady=5, sticky="e")

        self.btn_export_pdf = ttk.Button(self, text="Exportar PDF", command=self.on_export_pdf, state="disabled")
        self.btn_export_pdf.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # ─── Contenedor de pestañas para las tablas ───────────────────────────────
        self.tab_control = ttk.Notebook(self)
        self.frames = {}
        self.trees = {}

        tabs = [
            ("Resumen", ["ventas_netas", "cantidad_ventas", "ticket_promedio"]),
            ("Top Cantidad", ["nombre", "total_cantidad"]),
            ("Top Ingresos", ["nombre", "total_ingresos"]),
            ("Top Utilidad", ["nombre", "utilidad_total"]),
            ("Comparativo", ["Métrica", "Actual", "Anterior", "Variación"]),
        ]

        for title, cols in tabs:
            frame = ttk.Frame(self.tab_control)
            self.tab_control.add(frame, text=title)

            if title == "Comparativo":
                # Label para mostrar rangos de fechas
                lbl = ttk.Label(frame, text="", anchor="w")
                lbl.grid(row=0, column=0, sticky="w", padx=5, pady=5)
                self.lbl_comparison_period = lbl

                tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="none")
                # Configurar encabezados y columnas
                for col in cols:
                    tree.heading(col, text=col.replace("_", " ").title())
                    tree.column(col, anchor="center")

                tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
                frame.grid_rowconfigure(1, weight=1)
                frame.grid_columnconfigure(0, weight=1)
            else:
                # Pestañas normales
                tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="none")
                for col in cols:
                    tree.heading(col, text=col.replace("_", " ").title())
                    tree.column(col, anchor="center")
                tree.pack(fill="both", expand=True)

            self.frames[title] = frame
            self.trees[title] = tree

        self.tab_control.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        # ─── Configuración de grid para expansión ─────────────────────────────────
        self.grid_rowconfigure(1, weight=1)
        for c in range(7):
            self.grid_columnconfigure(c, weight=1)

        # Estado interno para almacenar datos de reporte
        self.report_data = {}

    def on_generate_report(self):
        """Generate report data and populate tables based on the selected date range."""
        start = self.date_inicio.get_date()
        end = self.date_fin.get_date()

        if end < start:
            messagebox.showerror("Rango inválido", "La fecha fin debe ser igual o posterior a la fecha inicio.")
            return

        try:
            self.report_data["Resumen"] = get_summary_report(start, end)
            self.report_data["Top Cantidad"] = get_top_quantity_report(start, end)
            self.report_data["Top Ingresos"] = get_top_revenue_report(start, end)
            self.report_data["Top Utilidad"] = get_top_profit_report(start, end)
        except Exception as e:
            messagebox.showerror("Error al generar reporte", str(e))
            return

        # Limpiamos todas las tablas y rellenamos solo las no-comparativo
        for title, tree in self.trees.items():
            tree.delete(*tree.get_children())
            if title == "Comparativo":
                continue
            data = self.report_data.get(title, [])
            if isinstance(data, dict):
                vals = [self._fmt_number(v) for v in data.values()]
                tree.insert("", "end", values=vals)
            else:
                for row in data:
                    vals = [self._fmt_number(v) if isinstance(v, (int, float)) else v for v in row.values()]
                    tree.insert("", "end", values=vals)

        # ─── Comparativo si days > 0 ───────────────────────────────────────────────
        try:
            days = int(self.spin_days.get())
        except ValueError:
            days = 0
        if days > 0:
            from services.report_service import get_comparison_report

            comp = get_comparison_report(start, end, days)
            # Mostrar rangos de fechas
            prev_end = start - timedelta(days=1)
            prev_start = prev_end - timedelta(days=days - 1)
            self.lbl_comparison_period.config(
                text=f"Actual: {start.isoformat()} a {end.isoformat()}    " f"Anterior: {prev_start.isoformat()} a {prev_end.isoformat()}"
            )
            self.report_data["Comparativo"] = comp
            tree = self.trees["Comparativo"]
            tree.delete(*tree.get_children())
            for key in comp["actual"]:
                metric = key.replace("_", " ").title()
                actual = comp["actual"][key]
                anterior = comp["anterior"][key]
                vari = comp["variacion"][key]
                tree.insert("", "end", values=[metric, self._fmt_number(actual), self._fmt_number(anterior), self._fmt_percent(vari)])

        # Habilitar botones de exportación
        self.btn_export_excel.configure(state="normal")
        self.btn_export_pdf.configure(state="normal")

    def on_export_excel(self):
        """Export the last generated report to an Excel file chosen by the user."""
        if not self.report_data:
            messagebox.showwarning("Sin datos", "Primero genere un reporte antes de exportar.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return

        try:
            export_report(self.report_data, format="excel", destination_path=path)
            messagebox.showinfo("Éxito", f"Reporte Excel guardado en:\n{path}")
        except ExportError as e:
            messagebox.showerror("Error exportando Excel", str(e))

    def on_export_pdf(self):
        """Export the last generated report to a PDF file chosen by the user."""
        if not self.report_data:
            messagebox.showwarning("Sin datos", "Primero genere un reporte antes de exportar.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path:
            return

        try:
            export_report(self.report_data, format="pdf", destination_path=path)
            messagebox.showinfo("Éxito", f"Reporte PDF guardado en:\n{path}")
        except ExportError as e:
            messagebox.showerror("Error exportando PDF", str(e))

    @staticmethod
    def _fmt_number(value: int | float) -> str:
        """Devuelve el número con separador de miles por comas. Ej: 1000000 → '1,000,000'."""
        return f"{value:,.0f}"

    @staticmethod
    def _fmt_percent(value: float) -> str:
        """Devuelve el valor como porcentaje con dos decimales, p. ej. '12.34%'."""
        return f"{value:.2%}"
