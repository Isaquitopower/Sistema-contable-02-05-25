import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Sistema Contable MJ", layout="wide")
st.title("📘 Sistema Contable - Sucursal C. MJ")
st.markdown("---")

# Conexión a base de datos SQLite
conn = sqlite3.connect("contabilidad.db")
c = conn.cursor()

# Crear tablas si no existen
c.execute(
    """CREATE TABLE IF NOT EXISTS diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    concepto TEXT,
    debe REAL,
    haber REAL
)"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS arqueo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    efectivo_caja REAL,
    total_esperado REAL,
    diferencia REAL
)"""
)
conn.commit()

# --------- SECCIÓN LIBRO DIARIO ---------
st.header("📌 Libro Diario")
with st.form("form_diario"):
    fecha = st.date_input("Fecha")
    concepto = st.text_input("Concepto")
    debe = st.number_input("Debe", min_value=0.0, step=100.0)
    haber = st.number_input("Haber", min_value=0.0, step=100.0)
    submit_diario = st.form_submit_button("Guardar asiento")

    if submit_diario:
        c.execute(
            "INSERT INTO diario (fecha, concepto, debe, haber) VALUES (?, ?, ?, ?)",
            (fecha.strftime("%Y-%m-%d"), concepto, debe, haber),
        )
        conn.commit()
        st.success("Asiento guardado correctamente.")

asientos = pd.read_sql("SELECT * FROM diario", conn)
if not asientos.empty:
    total_debe = asientos["debe"].sum()
    total_haber = asientos["haber"].sum()
    st.dataframe(asientos, use_container_width=True)
    st.markdown(f"**Totales** → Debe: ${total_debe:,.2f} | Haber: ${total_haber:,.2f}")

# --------- SECCIÓN LIBRO MAYOR ---------
st.header("📒 Libro Mayor")
if not asientos.empty:
    mayor = (
        asientos.groupby("concepto").agg({"debe": "sum", "haber": "sum"}).reset_index()
    )
    st.dataframe(
        mayor.rename(columns={"concepto": "Cuenta", "debe": "Debe", "haber": "Haber"}),
        use_container_width=True,
    )

# --------- SECCIÓN BALANZA DE COMPROBACIÓN ---------
st.header("📊 Balanza de Comprobación")
if not asientos.empty:
    movimientos = (
        asientos.groupby("concepto").agg({"debe": "sum", "haber": "sum"}).reset_index()
    )
    movimientos["saldo_debe"] = movimientos.apply(
        lambda row: row["debe"] - row["haber"] if row["debe"] > row["haber"] else 0,
        axis=1,
    )
    movimientos["saldo_haber"] = movimientos.apply(
        lambda row: row["haber"] - row["debe"] if row["haber"] > row["debe"] else 0,
        axis=1,
    )
    movimientos = movimientos.rename(
        columns={
            "concepto": "CUENTAS",
            "debe": "DEBE_MOV",
            "haber": "HABER_MOV",
            "saldo_debe": "DEBE_SALDO",
            "saldo_haber": "HABER_SALDO",
        }
    )
    st.dataframe(
        movimientos[["CUENTAS", "DEBE_MOV", "HABER_MOV", "DEBE_SALDO", "HABER_SALDO"]],
        use_container_width=True,
    )

# --------- SECCIÓN ESTADO DE RESULTADOS ---------
st.header("📈 Estado de Resultados")


def get_val(df, cuenta_nombre):
    row = df[df["CUENTAS"].str.lower() == cuenta_nombre.lower()]
    if not row.empty:
        return (
            row.iloc[0]["HABER_MOV"]
            if cuenta_nombre.lower() == "ventas"
            else row.iloc[0]["DEBE_MOV"]
        )
    return 0


ventas = get_val(movimientos, "Ventas")
compras = get_val(movimientos, "Compras")
gastos_operacion = get_val(movimientos, "Gastos de operacion")
descuentos_ventas = get_val(movimientos, "Descuento ventas")
devoluciones_ventas = get_val(movimientos, "Devolucion ventas")
rebajas_ventas = get_val(movimientos, "Rebaja ventas")

ventas_netas = ventas - descuentos_ventas - devoluciones_ventas - rebajas_ventas
costo_ventas = compras
utilidad_bruta = ventas_netas - costo_ventas
perdida_operacion = utilidad_bruta - gastos_operacion

col1, col2 = st.columns(2)
with col1:
    st.metric("Ventas Netas", f"${ventas_netas:,.2f}")
    st.metric("Costo de Ventas", f"${costo_ventas:,.2f}")
    st.metric("Utilidad Bruta", f"${utilidad_bruta:,.2f}")

with col2:
    st.metric("Gastos de Operación", f"${gastos_operacion:,.2f}")
    st.metric("Pérdida de Operación", f"${perdida_operacion:,.2f}")

# --------- SECCIÓN ARQUEO DE CAJA ---------
st.header("💵 Arqueo de Caja")
with st.form("arqueo_form"):
    fecha_arq = st.date_input("Fecha del arqueo", key="fecha_arq")
    efectivo_en_caja = st.number_input("Efectivo en caja", min_value=0.0, step=100.0)
    total_esperado = st.number_input(
        "Total esperado en caja", min_value=0.0, step=100.0
    )
    diferencia = efectivo_en_caja - total_esperado
    submit_arqueo = st.form_submit_button("Guardar arqueo")

    if submit_arqueo:
        c.execute(
            "INSERT INTO arqueo (fecha, efectivo_caja, total_esperado, diferencia) VALUES (?, ?, ?, ?)",
            (
                fecha_arq.strftime("%Y-%m-%d"),
                efectivo_en_caja,
                total_esperado,
                diferencia,
            ),
        )
        conn.commit()
        st.success(f"Diferencia guardada: ${diferencia:,.2f}")

arqueos = pd.read_sql("SELECT * FROM arqueo", conn)
st.dataframe(arqueos, use_container_width=True)

st.markdown("---")
st.info(
    "Todos los datos se almacenan localmente en SQLite. Puedes reiniciar los datos eliminando el archivo 'contabilidad.db'."
)
