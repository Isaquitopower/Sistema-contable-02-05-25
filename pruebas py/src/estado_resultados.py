import tkinter as tk
from tkinter import messagebox
from database.db import get_connection
from datetime import datetime

def abrir_estado_resultados():
    ventana = tk.Toplevel()
    ventana.title("Estado de Resultados")
    ventana.geometry("400x700")

    campos = {
        "Ventas Totales": 350000,
        "Descuentos s/Ventas": 35000,
        "Devoluciones s/Ventas": 18000,
        "Rebajas s/Ventas": 7000,
        "Compras": 600000,
        "Gastos de Compras": 1500000,
        "Devoluciones s/Compras": 120000,
        "Rebajas s/Compras": 15000,
        "Descuentos s/Compras": 60000,
        "Inventario Final": 57150,
        "Gastos de Operación": 5000
    }

    entradas = {}

    for campo, valor in campos.items():
        tk.Label(ventana, text=f"{campo} ($):").pack()
        entry = tk.Entry(ventana)
        entry.insert(0, str(valor))
        entry.pack()
        entradas[campo] = entry

    def calcular_y_guardar():
        try:
            # Obtener datos
            ventas_totales = float(entradas["Ventas Totales"].get())
            desc_ventas = float(entradas["Descuentos s/Ventas"].get())
            dev_ventas = float(entradas["Devoluciones s/Ventas"].get())
            reb_ventas = float(entradas["Rebajas s/Ventas"].get())
            compras = float(entradas["Compras"].get())
            gastos_compras = float(entradas["Gastos de Compras"].get())
            dev_compras = float(entradas["Devoluciones s/Compras"].get())
            reb_compras = float(entradas["Rebajas s/Compras"].get())
            desc_compras = float(entradas["Descuentos s/Compras"].get())
            inventario_final = float(entradas["Inventario Final"].get())
            gastos_operacion = float(entradas["Gastos de Operación"].get())

            # Cálculos
            ventas_net = ventas_totales - desc_ventas - dev_ventas - reb_ventas
            compras_totales = compras + gastos_compras
            compras_net = compras_totales - dev_compras - reb_compras - desc_compras
            costo_ventas = compras_net - inventario_final
            utilidad_bruta = ventas_net - costo_ventas
            perdida_operacion = utilidad_bruta - gastos_operacion
            fecha = datetime.now().strftime("%Y-%m-%d")

            # Guardar en DB
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO estado_resultados (
                    ventas_totales, descuentos_ventas, devoluciones_ventas, rebajas_ventas,
                    ventas_net, compras, gastos_compras, devoluciones_compras,
                    rebajas_compras, descuentos_compras, compras_net,
                    inventario_final, costo_ventas, utilidad_bruta,
                    gastos_operacion, perdida_operacion, fecha
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ventas_totales, desc_ventas, dev_ventas, reb_ventas,
                ventas_net, compras, gastos_compras, dev_compras,
                reb_compras, desc_compras, compras_net,
                inventario_final, costo_ventas, utilidad_bruta,
                gastos_operacion, perdida_operacion, fecha
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Resultado", f"Ventas Netas: ${ventas_net:,.2f}\nCosto de Ventas: ${costo_ventas:,.2f}\nPérdida de Operación: ${perdida_operacion:,.2f}")
            ventana.destroy()

        except ValueError:
            messagebox.showerror("Error", "Revisa los valores ingresados.")

    tk.Button(ventana, text="Calcular y Guardar", command=calcular_y_guardar).pack(pady=20)
