"""Punto de entrada de la aplicación Matex.

Lanza la ventana principal y arranca el bucle de eventos de Tkinter.
"""

from ui.main_window import MainWindow


def main() -> None:
    """Crea la ventana principal y entra en `mainloop()`."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
