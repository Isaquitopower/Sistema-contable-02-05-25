import tkinter as tk
from database.db import initialize_database
from src.arqueo_caja import abrir_arqueo_caja
from src.estado_resultados import abrir_estado_resultados
from src.contabilidad import abrir_procedimiento_contable
from src.comprobacion import abrir_comprobacion_financiera

# Inicializar Base de Datos
initialize_database()

# Ventana Principal
root = tk.Tk()
root.title("Control Financiero MJ")
root.geometry("500x400")

def salir_app():
    root.destroy()

# Botones
tk.Button(root, text="Arqueo de Caja", width=30, height=2, command=abrir_arqueo_caja).pack(pady=10)
tk.Button(root, text="Estado de Resultados", width=30, height=2, command=abrir_estado_resultados).pack(pady=10)
tk.Button(root, text="Procedimiento Contable", width=30, height=2, command=abrir_procedimiento_contable).pack(pady=10)
tk.Button(root, text="Comprobación Financiera", width=30, height=2, command=abrir_comprobacion_financiera).pack(pady=10)
tk.Button(root, text="Salir", width=30, height=2, command=salir_app).pack(pady=10)

# Ejecutar ventana
root.mainloop()
