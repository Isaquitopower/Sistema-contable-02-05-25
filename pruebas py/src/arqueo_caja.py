import tkinter as tk
from database.db import initialize_database


# Inicializar Base de Datos
initialize_database()

# Ventana Principal
root = tk.Tk()
root.title("Control Financiero MJ")
root.geometry("500x400")

# Funciones vacías por ahora
def abrir_arqueo_caja():
    pass

def abrir_estado_resultados():
    pass

def abrir_procedimiento_contable():
    pass

def abrir_comprobacion_financiera():
    pass

def salir_app():
    root.destroy()

# Botones
btn_arqueo = tk.Button(root, text="Arqueo de Caja", width=30, height=2, command=abrir_arqueo_caja)
btn_estado = tk.Button(root, text="Estado de Resultados", width=30, height=2, command=abrir_estado_resultados)
btn_procedimiento = tk.Button(root, text="Procedimiento Contable", width=30, height=2, command=abrir_procedimiento_contable)
btn_comprobacion = tk.Button(root, text="Comprobación Financiera", width=30, height=2, command=abrir_comprobacion_financiera)
btn_salir = tk.Button(root, text="Salir", width=30, height=2, command=salir_app)

# Posicionar Botones
btn_arqueo.pack(pady=10)
btn_estado.pack(pady=10)
btn_procedimiento.pack(pady=10)
btn_comprobacion.pack(pady=10)
btn_salir.pack(pady=10)

# Ejecutar ventana
root.mainloop()
