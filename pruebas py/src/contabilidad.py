import tkinter as tk
from tkinter import ttk
from database.db import get_connection
from datetime import datetime

def abrir_procedimiento_contable():
    ventana = tk.Toplevel()
    ventana.title("Procedimiento Contable")
    ventana.geometry("700x500")

    notebook = ttk.Notebook(ventana)
    notebook.pack(expand=True, fill="both")

    # Pestañas
    frame_diario = tk.Frame(notebook)
    frame_mayor = tk.Frame(notebook)
    frame_balanza = tk.Frame(notebook)

    notebook.add(frame_diario, text="Libro Diario")
    notebook.add(frame_mayor, text="Mayor")
    notebook.add(frame_balanza, text="Balanza")

    # ------------------- LIBRO DIARIO -------------------
    cols = ("Fecha", "Cuenta", "Debe", "Haber")
    tree_diario = ttk.Treeview(frame_diario, columns=cols, show="headings")
    for col in cols:
        tree_diario.heading(col, text=col)
    tree_diario.pack(fill="both", expand=True)

    def cargar_diario():
        tree_diario.delete(*tree_diario.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT fecha, cuenta, debe, haber FROM diario")
        for fila in cur.fetchall():
            tree_diario.insert("", "end", values=fila)
        conn.close()

    # ------------------- MAYOR -------------------
    cols_mayor = ("Cuenta", "Debe", "Haber", "Saldo")
    tree_mayor = ttk.Treeview(frame_mayor, columns=cols_mayor, show="headings")
    for col in cols_mayor:
        tree_mayor.heading(col, text=col)
    tree_mayor.pack(fill="both", expand=True)

    def cargar_mayor():
        tree_mayor.delete(*tree_mayor.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT cuenta, debe, haber, saldo FROM mayor")
        for fila in cur.fetchall():
            tree_mayor.insert("", "end", values=fila)
        conn.close()

    # ------------------- BALANZA -------------------
    cols_balanza = ("Cuenta", "Mov. Debe", "Mov. Haber", "Saldo Debe", "Saldo Haber")
    tree_balanza = ttk.Treeview(frame_balanza, columns=cols_balanza, show="headings")
    for col in cols_balanza:
        tree_balanza.heading(col, text=col)
    tree_balanza.pack(fill="both", expand=True)

    def cargar_balanza():
        tree_balanza.delete(*tree_balanza.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT cuenta, movimientos_debe, movimientos_haber, saldos_debe, saldos_haber FROM balanza")
        for fila in cur.fetchall():
            tree_balanza.insert("", "end", values=fila)
        conn.close()

    # Botones para recargar datos
    tk.Button(frame_diario, text="Recargar Diario", command=cargar_diario).pack(pady=5)
    tk.Button(frame_mayor, text="Recargar Mayor", command=cargar_mayor).pack(pady=5)
    tk.Button(frame_balanza, text="Recargar Balanza", command=cargar_balanza).pack(pady=5)

    cargar_diario()
    cargar_mayor()
    cargar_balanza()
