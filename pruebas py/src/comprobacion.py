import tkinter as tk
from tkinter import messagebox
from database.db import get_connection

def abrir_comprobacion_financiera():
    ventana = tk.Toplevel()
    ventana.title("Comprobación Financiera")
    ventana.geometry("400x300")

    def verificar_diario():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT SUM(debe), SUM(haber) FROM diario")
        debe, haber = cur.fetchone()
        conn.close()

        if round(debe or 0, 2) == round(haber or 0, 2):
            return f"✅ Diario: Cuadra (${debe:,.2f} = ${haber:,.2f})"
        else:
            return f"❌ Diario: No cuadra (${debe or 0:,.2f} ≠ ${haber or 0:,.2f})"

    def verificar_balanza():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT SUM(saldos_debe), SUM(saldos_haber) FROM balanza")
        s_debe, s_haber = cur.fetchone()
        conn.close()

        if round(s_debe or 0, 2) == round(s_haber or 0, 2):
            return f"✅ Balanza: Cuadra (${s_debe:,.2f} = ${s_haber:,.2f})"
        else:
            return f"❌ Balanza: No cuadra (${s_debe or 0:,.2f} ≠ ${s_haber or 0:,.2f})"

    def verificar_resultado_vs_diario():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT perdida_operacion FROM estado_resultados ORDER BY id DESC LIMIT 1")
        resultado = cur.fetchone()
        cur.execute("SELECT SUM(debe - haber) FROM diario")
        diferencia_diario = cur.fetchone()
        conn.close()

        if resultado and diferencia_diario:
            r = round(resultado[0], 2)
            d = round(diferencia_diario[0] or 0, 2)
            if r == d:
                return f"✅ Resultado ↔ Diario: Coincide (${r:,.2f})"
            else:
                return f"⚠️ Resultado ↔ Diario: No coincide (Res: ${r:,.2f} ≠ Dif Diario: ${d:,.2f})"
        return "ℹ️ No hay datos suficientes para comparar"

    def ejecutar_comprobaciones():
        diario_msg = verificar_diario()
        balanza_msg = verificar_balanza()
        resultado_msg = verificar_resultado_vs_diario()

        messagebox.showinfo("Resultados", f"{diario_msg}\n{balanza_msg}\n{resultado_msg}")

    tk.Button(ventana, text="Ejecutar Comprobaciones", command=ejecutar_comprobaciones).pack(pady=50)
