import streamlit as st
import pandas as pd
import sqlite3
import datetime
import matplotlib.pyplot as plt
import time
import os
from io import BytesIO
import base64

# Configuración de la página
st.set_page_config(
    page_title="Sistema Contable",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding: 1rem 1rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .subtitle {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .section {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }
    .info-box {
        background-color: #EFF6FF;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2563EB;
    }
    .stDataFrame {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .error-box {
        background-color: #FEF2F2;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #DC2626;
    }
    .success-box {
        background-color: #ECFDF5;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #059669;
    }
    .warning-box {
        background-color: #FFFBEB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #D97706;
    }
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    .dashboard-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
        text-align: center;
    }
    .dashboard-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .dashboard-label {
        font-size: 1rem;
        color: #6B7280;
    }
    .st-emotion-cache-16txtl3 {
        padding: 1rem;
    }
    .st-emotion-cache-r421ms {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Configurar la base de datos
def init_db():
    conn = sqlite3.connect('sistema_contable.db')
    c = conn.cursor()
    
    # Tabla para la información de la empresa
    c.execute('''
    CREATE TABLE IF NOT EXISTS empresa (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        rfc TEXT,
        direccion TEXT,
        telefono TEXT,
        fecha_inicio TEXT,
        fecha_fin TEXT
    )
    ''')
    
    # Tabla para el catálogo de cuentas
    c.execute('''
    CREATE TABLE IF NOT EXISTS catalogo_cuentas (
        id INTEGER PRIMARY KEY,
        codigo TEXT,
        nombre TEXT,
        tipo TEXT,
        naturaleza TEXT
    )
    ''')
    
    # Tabla para las transacciones (diario)
    c.execute('''
    CREATE TABLE IF NOT EXISTS diario (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        descripcion TEXT,
        folio INTEGER
    )
    ''')
    
    # Tabla para los movimientos (detalle de transacciones)
    c.execute('''
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY,
        diario_id INTEGER,
        cuenta_id INTEGER,
        debe REAL,
        haber REAL,
        FOREIGN KEY (diario_id) REFERENCES diario (id),
        FOREIGN KEY (cuenta_id) REFERENCES catalogo_cuentas (id)
    )
    ''')
    
    # Tabla para el arqueo de caja
    c.execute('''
    CREATE TABLE IF NOT EXISTS arqueo_caja (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        responsable TEXT,
        saldo_inicial REAL,
        saldo_final REAL,
        diferencia REAL,
        observaciones TEXT
    )
    ''')
    
    # Tabla para el detalle del arqueo de caja
    c.execute('''
    CREATE TABLE IF NOT EXISTS detalle_arqueo (
        id INTEGER PRIMARY KEY,
        arqueo_id INTEGER,
        concepto TEXT,
        denominacion TEXT,
        cantidad INTEGER,
        valor_unitario REAL,
        total REAL,
        FOREIGN KEY (arqueo_id) REFERENCES arqueo_caja (id)
    )
    ''')
    
    # Tabla para inventarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventarios (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        concepto TEXT,
        cantidad REAL,
        costo_unitario REAL,
        costo_total REAL
    )
    ''')
    
    # Insertar cuentas predeterminadas si no existen
    c.execute("SELECT COUNT(*) FROM catalogo_cuentas")
    count = c.fetchone()[0]
    
    if count == 0:
        cuentas = [
            ('1010', 'Caja', 'Activo', 'Deudora'),
            ('1020', 'Bancos', 'Activo', 'Deudora'),
            ('1030', 'IVA Acreditable', 'Activo', 'Deudora'),
            ('1040', 'Inventario', 'Activo', 'Deudora'),
            ('2010', 'IVA Trasladado', 'Pasivo', 'Acreedora'),
            ('3010', 'Capital', 'Capital', 'Acreedora'),
            ('4010', 'Ventas', 'Resultados', 'Acreedora'),
            ('4020', 'Devoluciones sobre Ventas', 'Resultados', 'Deudora'),
            ('4030', 'Rebajas sobre Ventas', 'Resultados', 'Deudora'),
            ('4040', 'Descuentos sobre Ventas', 'Resultados', 'Deudora'),
            ('5010', 'Compras', 'Resultados', 'Deudora'),
            ('5020', 'Gastos de Compras', 'Resultados', 'Deudora'),
            ('5030', 'Devoluciones sobre Compras', 'Resultados', 'Acreedora'),
            ('5040', 'Rebajas sobre Compras', 'Resultados', 'Acreedora'),
            ('5050', 'Descuentos sobre Compras', 'Resultados', 'Acreedora'),
            ('6010', 'Gastos de Operación', 'Resultados', 'Deudora'),
        ]
        c.executemany("INSERT INTO catalogo_cuentas (codigo, nombre, tipo, naturaleza) VALUES (?, ?, ?, ?)", cuentas)
    
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect('sistema_contable.db')

# Inicializar la base de datos
init_db()

# Funciones auxiliares
def get_cuenta_id(nombre_cuenta):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM catalogo_cuentas WHERE nombre = ?", (nombre_cuenta,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_cuenta_nombre(cuenta_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT nombre FROM catalogo_cuentas WHERE id = ?", (cuenta_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_naturaleza_cuenta(cuenta_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT naturaleza FROM catalogo_cuentas WHERE id = ?", (cuenta_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def obtener_cuentas():
    conn = get_conn()
    cuentas = pd.read_sql_query("SELECT id, codigo, nombre, tipo, naturaleza FROM catalogo_cuentas ORDER BY codigo", conn)
    conn.close()
    return cuentas

def obtener_diario():
    conn = get_conn()
    diario = pd.read_sql_query("""
    SELECT d.id, d.fecha, d.descripcion, d.folio, 
           c.nombre as cuenta, m.debe, m.haber
    FROM diario d
    JOIN movimientos m ON d.id = m.diario_id
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    ORDER BY d.fecha, d.id, m.id
    """, conn)
    conn.close()
    return diario

def obtener_mayor():
    conn = get_conn()
    
    # Obtener todas las cuentas
    cuentas = pd.read_sql_query("SELECT id, nombre, naturaleza FROM catalogo_cuentas", conn)
    
    # Para cada cuenta, obtener sus movimientos
    mayor = []
    
    for _, cuenta in cuentas.iterrows():
        movimientos = pd.read_sql_query("""
        SELECT d.fecha, d.descripcion, d.folio, m.debe, m.haber
        FROM movimientos m
        JOIN diario d ON m.diario_id = d.id
        WHERE m.cuenta_id = ?
        ORDER BY d.fecha, d.id
        """, (cuenta['id'],), conn)
        
        if not movimientos.empty:
            # Calcular saldos
            debe_total = movimientos['debe'].sum()
            haber_total = movimientos['haber'].sum()
            
            if cuenta['naturaleza'] == 'Deudora':
                saldo = debe_total - haber_total
            else:
                saldo = haber_total - debe_total
            
            mayor.append({
                'cuenta_id': cuenta['id'],
                'cuenta': cuenta['nombre'],
                'naturaleza': cuenta['naturaleza'],
                'movimientos': movimientos,
                'debe_total': debe_total,
                'haber_total': haber_total,
                'saldo': saldo
            })
    
    conn.close()
    return mayor

def obtener_balanza():
    conn = get_conn()
    balanza = pd.read_sql_query("""
    SELECT 
        c.id, 
        c.codigo, 
        c.nombre, 
        c.naturaleza,
        IFNULL(SUM(m.debe), 0) as total_debe, 
        IFNULL(SUM(m.haber), 0) as total_haber,
        CASE 
            WHEN c.naturaleza = 'Deudora' THEN 
                CASE 
                    WHEN IFNULL(SUM(m.debe), 0) - IFNULL(SUM(m.haber), 0) > 0 THEN 
                        IFNULL(SUM(m.debe), 0) - IFNULL(SUM(m.haber), 0)
                    ELSE 0 
                END
            ELSE 0 
        END as saldo_deudor,
        CASE 
            WHEN c.naturaleza = 'Acreedora' THEN 
                CASE 
                    WHEN IFNULL(SUM(m.haber), 0) - IFNULL(SUM(m.debe), 0) > 0 THEN 
                        IFNULL(SUM(m.haber), 0) - IFNULL(SUM(m.debe), 0)
                    ELSE 0 
                END
            WHEN c.naturaleza = 'Deudora' THEN
                CASE 
                    WHEN IFNULL(SUM(m.haber), 0) - IFNULL(SUM(m.debe), 0) > 0 THEN 
                        IFNULL(SUM(m.haber), 0) - IFNULL(SUM(m.debe), 0)
                    ELSE 0 
                END
            ELSE 0 
        END as saldo_acreedor
    FROM catalogo_cuentas c
    LEFT JOIN movimientos m ON c.id = m.cuenta_id
    GROUP BY c.id
    ORDER BY c.codigo
    """, conn)
    
    # Calcular totales
    total_debe = balanza['total_debe'].sum()
    total_haber = balanza['total_haber'].sum()
    total_saldo_deudor = balanza['saldo_deudor'].sum()
    total_saldo_acreedor = balanza['saldo_acreedor'].sum()
    
    conn.close()
    
    return balanza, total_debe, total_haber, total_saldo_deudor, total_saldo_acreedor

def obtener_estado_resultados():
    conn = get_conn()
    
    # Obtener ventas
    ventas = pd.read_sql_query("""
    SELECT SUM(m.haber - m.debe) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Ventas'
    """, conn).iloc[0]['total']
    
    if ventas is None:
        ventas = 0
    
    # Obtener devoluciones sobre ventas
    dev_ventas = pd.read_sql_query("""
    SELECT SUM(m.debe - m.haber) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Devoluciones sobre Ventas'
    """, conn).iloc[0]['total']
    
    if dev_ventas is None:
        dev_ventas = 0
    
    # Obtener rebajas sobre ventas
    reb_ventas = pd.read_sql_query("""
    SELECT SUM(m.debe - m.haber) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Rebajas sobre Ventas'
    """, conn).iloc[0]['total']
    
    if reb_ventas is None:
        reb_ventas = 0
    
    # Obtener descuentos sobre ventas
    desc_ventas = pd.read_sql_query("""
    SELECT SUM(m.debe - m.haber) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Descuentos sobre Ventas'
    """, conn).iloc[0]['total']
    
    if desc_ventas is None:
        desc_ventas = 0
    
    # Calcular ventas netas
    ventas_netas = ventas - dev_ventas - reb_ventas - desc_ventas
    
    # Obtener inventario inicial
    inv_inicial = pd.read_sql_query("""
    SELECT valor as total
    FROM sistema_valores
    WHERE concepto = 'inventario_inicial'
    """, conn)
    
    if inv_inicial.empty:
        inv_inicial = 0
    else:
        inv_inicial = inv_inicial.iloc[0]['total']
    
    # Obtener compras
    compras = pd.read_sql_query("""
    SELECT SUM(m.debe - m.haber) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Compras'
    """, conn).iloc[0]['total']
    
    if compras is None:
        compras = 0
    
    # Obtener gastos de compras
    gastos_compras = pd.read_sql_query("""
    SELECT SUM(m.debe - m.haber) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Gastos de Compras'
    """, conn).iloc[0]['total']
    
    if gastos_compras is None:
        gastos_compras = 0
    
    # Calcular compras totales
    compras_totales = compras + gastos_compras
    
    # Obtener devoluciones sobre compras
    dev_compras = pd.read_sql_query("""
    SELECT SUM(m.haber - m.debe) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Devoluciones sobre Compras'
    """, conn).iloc[0]['total']
    
    if dev_compras is None:
        dev_compras = 0
    
    # Obtener rebajas sobre compras
    reb_compras = pd.read_sql_query("""
    SELECT SUM(m.haber - m.debe) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Rebajas sobre Compras'
    """, conn).iloc[0]['total']
    
    if reb_compras is None:
        reb_compras = 0
    
    # Obtener descuentos sobre compras
    desc_compras = pd.read_sql_query("""
    SELECT SUM(m.haber - m.debe) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Descuentos sobre Compras'
    """, conn).iloc[0]['total']
    
    if desc_compras is None:
        desc_compras = 0
    
    # Calcular compras netas
    compras_netas = compras_totales - dev_compras - reb_compras - desc_compras
    
    # Calcular total de mercancías
    total_mercancias = inv_inicial + compras_netas
    
    # Obtener inventario final
    try:
        c = conn.cursor()
        c.execute("SELECT valor FROM sistema_valores WHERE concepto = 'inventario_final'")
        inv_final = c.fetchone()
        if inv_final:
            inv_final = inv_final[0]
        else:
            # Si no hay valor almacenado, intentamos crear la tabla y el registro
            try:
                c.execute('''
                CREATE TABLE IF NOT EXISTS sistema_valores (
                    id INTEGER PRIMARY KEY,
                    concepto TEXT UNIQUE,
                    valor REAL
                )
                ''')
                c.execute("INSERT OR IGNORE INTO sistema_valores (concepto, valor) VALUES ('inventario_final', 0)")
                conn.commit()
                inv_final = 0
            except Exception as e:
                st.error(f"Error al crear tabla de valores: {e}")
                inv_final = 0
    except Exception as e:
        # Si hay un error, intentamos crear la tabla
        try:
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS sistema_valores (
                id INTEGER PRIMARY KEY,
                concepto TEXT UNIQUE,
                valor REAL
            )
            ''')
            c.execute("INSERT OR IGNORE INTO sistema_valores (concepto, valor) VALUES ('inventario_final', 0)")
            c.execute("INSERT OR IGNORE INTO sistema_valores (concepto, valor) VALUES ('inventario_inicial', 0)")
            conn.commit()
            inv_final = 0
            inv_inicial = 0
        except Exception as e:
            st.error(f"Error al crear tabla de valores: {e}")
            inv_final = 0
    
    # Calcular costo de ventas
    costo_ventas = total_mercancias - inv_final
    
    # Calcular utilidad bruta
    utilidad_bruta = ventas_netas - costo_ventas
    
    # Obtener gastos de operación
    gastos_operacion = pd.read_sql_query("""
    SELECT SUM(m.debe - m.haber) as total
    FROM movimientos m
    JOIN catalogo_cuentas c ON m.cuenta_id = c.id
    WHERE c.nombre = 'Gastos de Operación'
    """, conn).iloc[0]['total']
    
    if gastos_operacion is None:
        gastos_operacion = 0
    
    # Calcular utilidad de operación
    utilidad_operacion = utilidad_bruta - gastos_operacion
    
    conn.close()
    
    return {
        'ventas': ventas,
        'dev_ventas': dev_ventas,
        'reb_ventas': reb_ventas,
        'desc_ventas': desc_ventas,
        'ventas_netas': ventas_netas,
        'inv_inicial': inv_inicial,
        'compras': compras,
        'gastos_compras': gastos_compras,
        'compras_totales': compras_totales,
        'dev_compras': dev_compras,
        'reb_compras': reb_compras,
        'desc_compras': desc_compras,
        'compras_netas': compras_netas,
        'total_mercancias': total_mercancias,
        'inv_final': inv_final,
        'costo_ventas': costo_ventas,
        'utilidad_bruta': utilidad_bruta,
        'gastos_operacion': gastos_operacion,
        'utilidad_operacion': utilidad_operacion
    }

def obtener_arqueo_caja():
    conn = get_conn()
    arqueos = pd.read_sql_query("""
    SELECT id, fecha, responsable, saldo_inicial, saldo_final, diferencia, observaciones
    FROM arqueo_caja
    ORDER BY fecha DESC
    """, conn)
    conn.close()
    return arqueos

def obtener_detalle_arqueo(arqueo_id):
    conn = get_conn()
    detalle = pd.read_sql_query("""
    SELECT id, concepto, denominacion, cantidad, valor_unitario, total
    FROM detalle_arqueo
    WHERE arqueo_id = ?
    ORDER BY id
    """, conn, params=(arqueo_id,))
    conn.close()
    return detalle

def guardar_datos_empresa(nombre, rfc, direccion, telefono, fecha_inicio, fecha_fin):
    conn = get_conn()
    c = conn.cursor()
    
    # Verificar si ya existe información de la empresa
    c.execute("SELECT COUNT(*) FROM empresa")
    count = c.fetchone()[0]
    
    if count > 0:
        # Actualizar los datos existentes
        c.execute("""
        UPDATE empresa
        SET nombre = ?, rfc = ?, direccion = ?, telefono = ?, fecha_inicio = ?, fecha_fin = ?
        WHERE id = 1
        """, (nombre, rfc, direccion, telefono, fecha_inicio, fecha_fin))
    else:
        # Insertar nuevos datos
        c.execute("""
        INSERT INTO empresa (nombre, rfc, direccion, telefono, fecha_inicio, fecha_fin)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, rfc, direccion, telefono, fecha_inicio, fecha_fin))
    
    conn.commit()
    conn.close()

def obtener_datos_empresa():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("SELECT nombre, rfc, direccion, telefono, fecha_inicio, fecha_fin FROM empresa WHERE id = 1")
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return {
            'nombre': result[0],
            'rfc': result[1],
            'direccion': result[2],
            'telefono': result[3],
            'fecha_inicio': result[4],
            'fecha_fin': result[5]
        }
    else:
        return {
            'nombre': '',
            'rfc': '',
            'direccion': '',
            'telefono': '',
            'fecha_inicio': '',
            'fecha_fin': ''
        }

def agregar_transaccion(fecha, descripcion, folio, movimientos_list):
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # Insertar en la tabla diario
        c.execute("""
        INSERT INTO diario (fecha, descripcion, folio)
        VALUES (?, ?, ?)
        """, (fecha, descripcion, folio))
        
        diario_id = c.lastrowid
        
        # Insertar movimientos
        for movimiento in movimientos_list:
            cuenta_id = movimiento['cuenta_id']
            debe = movimiento['debe']
            haber = movimiento['haber']
            
            c.execute("""
            INSERT INTO movimientos (diario_id, cuenta_id, debe, haber)
            VALUES (?, ?, ?, ?)
            """, (diario_id, cuenta_id, debe, haber))
        
        conn.commit()
        return True, "Transacción registrada correctamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al registrar la transacción: {str(e)}"
    finally:
        conn.close()

def agregar_arqueo_caja(fecha, responsable, saldo_inicial, saldo_final, diferencia, observaciones, detalles):
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # Insertar en la tabla arqueo_caja
        c.execute("""
        INSERT INTO arqueo_caja (fecha, responsable, saldo_inicial, saldo_final, diferencia, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha, responsable, saldo_inicial, saldo_final, diferencia, observaciones))
        
        arqueo_id = c.lastrowid
        
        # Insertar detalles del arqueo
        for detalle in detalles:
            c.execute("""
            INSERT INTO detalle_arqueo (arqueo_id, concepto, denominacion, cantidad, valor_unitario, total)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (arqueo_id, detalle['concepto'], detalle['denominacion'], 
                 detalle['cantidad'], detalle['valor_unitario'], detalle['total']))
        
        conn.commit()
        return True, "Arqueo de caja registrado correctamente"
    except Exception as e:
        conn.rollback()
        return False, f"Error al registrar el arqueo de caja: {str(e)}"
    finally:
        conn.close()

def actualizar_valor_sistema(concepto, valor):
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # Verificar si ya existe el concepto
        c.execute("SELECT COUNT(*) FROM sistema_valores WHERE concepto = ?", (concepto,))
        count = c.fetchone()[0]
        
        if count > 0:
            # Actualizar el valor existente
            c.execute("""
            UPDATE sistema_valores
            SET valor = ?
            WHERE concepto = ?
            """, (valor, concepto))
        else:
            # Insertar nuevo valor
            c.execute("""
            INSERT INTO sistema_valores (concepto, valor)
            VALUES (?, ?)
            """, (concepto, valor))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_df_to_csv_download_link(df, filename, text):
    """Genera un enlace para descargar un DataFrame como CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Menú principal de la aplicación
def main():
    # Sidebar para navegación
    st.sidebar.image("https://www.svgrepo.com/show/55175/accounting.svg", width=100)
    st.sidebar.markdown("<div class='subtitle'>Sistema Contable</div>", unsafe_allow_html=True)
    
    # Menú de navegación
    menu_options = [
        "Inicio",
        "Configuración",
        "Catálogo de Cuentas",
        "Registro de Transacciones",
        "Diario",
        "Libro Mayor",
        "Balanza de Comprobación",
        "Estado de Resultados",
        "Arqueo de Caja"
    ]
    
    seleccion = st.sidebar.selectbox("Menú", menu_options)
    
    # Información de la empresa
    empresa_info = obtener_datos_empresa()
    
    if empresa_info['nombre']:
        st.sidebar.markdown(f"<div class='info-box'><strong>{empresa_info['nombre']}</strong><br>{empresa_info['rfc']}</div>", unsafe_allow_html=True)
    
    # Contenido principal según la selección
    if seleccion == "Inicio":
        pagina_inicio()
    elif seleccion == "Configuración":
        pagina_configuracion()
    elif seleccion == "Catálogo de Cuentas":
        pagina_catalogo_cuentas()
    elif seleccion == "Registro de Transacciones":
        pagina_registro_transacciones()
    elif seleccion == "Diario":
        pagina_diario()
    elif seleccion == "Libro Mayor":
        pagina_libro_mayor()
    elif seleccion == "Balanza de Comprobación":
        pagina_balanza_comprobacion()
    elif seleccion == "Estado de Resultados":
        pagina_estado_resultados()
    elif seleccion == "Arqueo de Caja":
        pagina_arqueo_caja()

# Página de inicio
def pagina_inicio():
    st.markdown("<div class='title'>Sistema Contable</div>", unsafe_allow_html=True)
    
    # Obtener información de la empresa
    empresa_info = obtener_datos_empresa()
    
    if empresa_info['nombre']:
        # Si hay información de la empresa, mostrarla
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='subtitle'>Información de la Empresa</div>", unsafe_allow_html=True)
            st.markdown(f"**Nombre:** {empresa_info['nombre']}")
            st.markdown(f"**RFC:** {empresa_info['rfc']}")
            st.markdown(f"**Dirección:** {empresa_info['direccion']}")
            st.markdown(f"**Teléfono:** {empresa_info['telefono']}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='subtitle'>Período Contable</div>", unsafe_allow_html=True)
            st.markdown(f"**Fecha Inicio:** {empresa_info['fecha_inicio']}")
            st.markdown(f"**Fecha Fin:** {empresa_info['fecha_fin']}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Dashboard con resumen
        st.markdown("<div class='subtitle'>Resumen Contable</div>", unsafe_allow_html=True)
        
        # Obtener datos para el dashboard
        try:
            # Estado de resultados
            estado = obtener_estado_resultados()
            
            # Balanza
            balanza, total_debe, total_haber, total_saldo_deudor, total_saldo_acreedor = obtener_balanza()
            
            # Mostrar tarjetas de resumen
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='dashboard-number'>${estado['ventas_netas']:,.2f}</div>", unsafe_allow_html=True)
                st.markdown("<div class='dashboard-label'>Ventas Netas</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='dashboard-number'>${estado['utilidad_operacion']:,.2f}</div>", unsafe_allow_html=True)
                st.markdown("<div class='dashboard-label'>Utilidad/Pérdida</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='dashboard-number'>${total_saldo_deudor:,.2f}</div>", unsafe_allow_html=True)
                st.markdown("<div class='dashboard-label'>Total Saldo Deudor</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col4:
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='dashboard-number'>${total_saldo_acreedor:,.2f}</div>", unsafe_allow_html=True)
                st.markdown("<div class='dashboard-label'>Total Saldo Acreedor</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section'>Ventas vs Compras</div>", unsafe_allow_html=True)
                
                # Datos para el gráfico
                labels = ['Ventas', 'Compras']
                sizes = [estado['ventas'], estado['compras']]
                
                # Crear figura
                fig, ax = plt.subplots()
                ax.bar(labels, sizes, color=['#3B82F6', '#F87171'])
                ax.set_ylabel('Monto ($)')
                ax.set_title('Comparativa de Ventas y Compras')
                
                # Mostrar gráfico
                st.pyplot(fig)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section'>Composición del Estado de Resultados</div>", unsafe_allow_html=True)
                
                # Datos para el gráfico
                labels = ['Ventas Netas', 'Costo de Ventas', 'Gastos de Operación']
                sizes = [estado['ventas_netas'], estado['costo_ventas'], estado['gastos_operacion']]
                
                # Crear figura
                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#3B82F6', '#F87171', '#FBBF24'])
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                
                # Mostrar gráfico
                st.pyplot(fig)
                st.markdown("</div>", unsafe_allow_html=True)
        
        except Exception as e:
            st.warning(f"No se pueden mostrar estadísticas: {str(e)}")
            st.info("Registre transacciones para ver estadísticas.")
    
    else:
        # Si no hay información de la empresa, mostrar mensaje
        st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
        st.markdown("### ¡Bienvenido al Sistema Contable!")
        st.markdown("Para comenzar, configure la información de su empresa en el menú **Configuración**.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("### Funcionalidades principales:")
        st.markdown("""
        - Registro de transacciones contables
        - Libro Diario y Mayor
        - Balanza de Comprobación
        - Estado de Resultados
        - Arqueo de Caja
        """)
        st.markdown("</div>", unsafe_allow_html=True)

# Página de configuración
def pagina_configuracion():
    st.markdown("<div class='title'>Configuración del Sistema</div>", unsafe_allow_html=True)
    
    # Información de la empresa
    st.markdown("<div class='subtitle'>Información de la Empresa</div>", unsafe_allow_html=True)
    
    # Obtener datos actuales
    empresa_info = obtener_datos_empresa()
    
    with st.form(key="form_empresa"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre de la Empresa", value=empresa_info['nombre'])
            rfc = st.text_input("RFC", value=empresa_info['rfc'])
            direccion = st.text_input("Dirección", value=empresa_info['direccion'])
        
        with col2:
            telefono = st.text_input("Teléfono", value=empresa_info['telefono'])
            fecha_inicio = st.date_input("Fecha de Inicio del Período", 
                                       value=datetime.datetime.strptime(empresa_info['fecha_inicio'], "%Y-%m-%d").date() if empresa_info['fecha_inicio'] else datetime.date.today())
            fecha_fin = st.date_input("Fecha de Fin del Período", 
                                    value=datetime.datetime.strptime(empresa_info['fecha_fin'], "%Y-%m-%d").date() if empresa_info['fecha_fin'] else datetime.date.today())
        
        # Botón para guardar
        submit_button = st.form_submit_button(label="Guardar Información")
        
        if submit_button:
            # Validaciones
            if not nombre or not rfc:
                st.error("El nombre de la empresa y el RFC son obligatorios.")
            else:
                # Guardar la información
                guardar_datos_empresa(nombre, rfc, direccion, telefono, fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"))
                st.success("Información guardada correctamente.")
    
    # Configuración de Inventarios
    st.markdown("<div class='subtitle'>Configuración de Inventarios</div>", unsafe_allow_html=True)
    
    with st.form(key="form_inventarios"):
        # Obtener valor actual de inventario inicial
        conn = get_conn()
        c = conn.cursor()
        
        try:
            c.execute("SELECT valor FROM sistema_valores WHERE concepto = 'inventario_inicial'")
            inv_inicial = c.fetchone()
            if inv_inicial:
                inv_inicial = inv_inicial[0]
            else:
                inv_inicial = 0
            
            c.execute("SELECT valor FROM sistema_valores WHERE concepto = 'inventario_final'")
            inv_final = c.fetchone()
            if inv_final:
                inv_final = inv_final[0]
            else:
                inv_final = 0
        except:
            inv_inicial = 0
            inv_final = 0
        finally:
            conn.close()
        
        col1, col2 = st.columns(2)
        
        with col1:
            inventario_inicial = st.number_input("Inventario Inicial", value=float(inv_inicial), min_value=0.0, step=1000.0)
        
        with col2:
            inventario_final = st.number_input("Inventario Final", value=float(inv_final), min_value=0.0, step=1000.0)
        
        # Botón para guardar
        submit_button = st.form_submit_button(label="Guardar Inventarios")
        
        if submit_button:
            # Guardar valores
            result1 = actualizar_valor_sistema('inventario_inicial', inventario_inicial)
            result2 = actualizar_valor_sistema('inventario_final', inventario_final)
            
            if result1 and result2:
                st.success("Valores de inventario guardados correctamente.")
            else:
                st.error("Error al guardar los valores de inventario.")

    # Botón para reiniciar la base de datos
    st.markdown("<div class='subtitle'>Administración del Sistema</div>", unsafe_allow_html=True)
    
    if st.button("Reiniciar Base de Datos", help="ADVERTENCIA: Esta acción eliminará todos los datos registrados."):
        # Mostrar confirmación
        confirmacion = st.text_input("Escriba 'CONFIRMAR' para eliminar todos los datos:")
        
        if confirmacion == "CONFIRMAR":
            try:
                # Eliminar la base de datos
                conn = get_conn()
                conn.close()
                
                if os.path.exists('sistema_contable.db'):
                    os.remove('sistema_contable.db')
                
                # Reiniciar la base de datos
                init_db()
                
                st.success("La base de datos ha sido reiniciada correctamente.")
                st.warning("Debe configurar nuevamente los datos de la empresa.")
                
                # Esperar 2 segundos y recargar
                time.sleep(2)
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error al reiniciar la base de datos: {str(e)}")
        elif confirmacion and confirmacion != "CONFIRMAR":
            st.error("Confirmación incorrecta. La base de datos no se ha eliminado.")

# Página del catálogo de cuentas
def pagina_catalogo_cuentas():
    st.markdown("<div class='title'>Catálogo de Cuentas</div>", unsafe_allow_html=True)
    
    # Pestañas
    tab1, tab2 = st.tabs(["Catálogo de Cuentas", "Agregar Cuenta"])
    
    with tab1:
        # Mostrar catálogo de cuentas
        cuentas = obtener_cuentas()
        
        if not cuentas.empty:
            # Agrupar por tipo
            tipos = cuentas['tipo'].unique()
            
            for tipo in tipos:
                st.markdown(f"<div class='subtitle'>{tipo}</div>", unsafe_allow_html=True)
                
                # Filtrar cuentas por tipo
                cuentas_tipo = cuentas[cuentas['tipo'] == tipo]
                
                # Mostrar tabla
                st.dataframe(cuentas_tipo[['codigo', 'nombre', 'naturaleza']], use_container_width=True)
        else:
            st.info("No hay cuentas registradas.")
    
    with tab2:
        # Formulario para agregar cuenta
        with st.form(key="form_cuenta"):
            col1, col2 = st.columns(2)
            
            with col1:
                codigo = st.text_input("Código de la Cuenta")
                nombre = st.text_input("Nombre de la Cuenta")
            
            with col2:
                tipo = st.selectbox("Tipo de Cuenta", ["Activo", "Pasivo", "Capital", "Resultados"])
                naturaleza = st.selectbox("Naturaleza", ["Deudora", "Acreedora"])
            
            # Botón para guardar
            submit_button = st.form_submit_button(label="Agregar Cuenta")
            
            if submit_button:
                # Validaciones
                if not codigo or not nombre:
                    st.error("El código y el nombre de la cuenta son obligatorios.")
                else:
                    # Verificar si ya existe el código
                    conn = get_conn()
                    c = conn.cursor()
                    
                    c.execute("SELECT COUNT(*) FROM catalogo_cuentas WHERE codigo = ?", (codigo,))
                    count = c.fetchone()[0]
                    
                    if count > 0:
                        st.error(f"Ya existe una cuenta con el código {codigo}.")
                    else:
                        # Insertar nueva cuenta
                        c.execute("""
                        INSERT INTO catalogo_cuentas (codigo, nombre, tipo, naturaleza)
                        VALUES (?, ?, ?, ?)
                        """, (codigo, nombre, tipo, naturaleza))
                        
                        conn.commit()
                        st.success(f"Cuenta '{nombre}' agregada correctamente.")
                    
                    conn.close()

# Página de registro de transacciones
def pagina_registro_transacciones():
    st.markdown("<div class='title'>Registro de Transacciones</div>", unsafe_allow_html=True)
    
    # Obtener cuentas
    cuentas = obtener_cuentas()
    
    if cuentas.empty:
        st.warning("No hay cuentas registradas. Por favor, agregue cuentas en el Catálogo de Cuentas.")
        return
    
    # Crear formulario para nueva transacción
    with st.form(key="form_transaccion"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha = st.date_input("Fecha", value=datetime.date.today())
        
        with col2:
            descripcion = st.text_input("Descripción de la Transacción")
        
        with col3:
            folio = st.number_input("Folio", min_value=1, step=1)
        
        # Crear campos para movimientos
        st.markdown("<div class='section'>Movimientos</div>", unsafe_allow_html=True)
        
        # Crear una lista de cuentas para los selectbox
        opciones_cuentas = cuentas[['id', 'nombre']].copy()
        opciones_cuentas['nombre_completo'] = opciones_cuentas['nombre']
        
        # Número de movimientos (mínimo 2)
        num_movimientos = st.number_input("Número de Movimientos", min_value=2, max_value=10, value=2)
        
        # Lista para almacenar movimientos
        movimientos_list = []
        
        # Crear campos para cada movimiento
        for i in range(num_movimientos):
            st.markdown(f"<div class='section'>Movimiento {i+1}</div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cuenta_id = st.selectbox(f"Cuenta {i+1}", opciones_cuentas['nombre_completo'], key=f"cuenta_{i}")
                cuenta_id = get_cuenta_id(cuenta_id)
            
            with col2:
                debe = st.number_input(f"Debe {i+1}", min_value=0.0, step=100.0, key=f"debe_{i}")
            
            with col3:
                haber = st.number_input(f"Haber {i+1}", min_value=0.0, step=100.0, key=f"haber_{i}")
            
            # Agregar movimiento a la lista
            movimientos_list.append({
                'cuenta_id': cuenta_id,
                'debe': debe,
                'haber': haber
            })
        
        # Comprobar que cuadren debe y haber
        total_debe = sum([m['debe'] for m in movimientos_list])
        total_haber = sum([m['haber'] for m in movimientos_list])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Debe", f"${total_debe:,.2f}")
        
        with col2:
            st.metric("Total Haber", f"${total_haber:,.2f}")
        
        if total_debe != total_haber:
            st.warning("El total del Debe debe ser igual al total del Haber.")
        
        # Botón para registrar
        submit_button = st.form_submit_button(label="Registrar Transacción")
        
        if submit_button:
            # Validaciones
            if not descripcion:
                st.error("La descripción de la transacción es obligatoria.")
            elif total_debe != total_haber:
                st.error("El total del Debe debe ser igual al total del Haber.")
            elif total_debe == 0 and total_haber == 0:
                st.error("Debe haber al menos un movimiento.")
            else:
                # Registrar transacción
                success, message = agregar_transaccion(
                    fecha.strftime("%Y-%m-%d"),
                    descripcion,
                    folio,
                    movimientos_list
                )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Página de diario
def pagina_diario():
    st.markdown("<div class='title'>Libro Diario</div>", unsafe_allow_html=True)
    
    # Obtener datos de la empresa
    empresa_info = obtener_datos_empresa()
    
    if empresa_info['nombre']:
        st.markdown(f"<div class='info-box'><strong>{empresa_info['nombre']}</strong><br>RFC: {empresa_info['rfc']}<br>Período: {empresa_info['fecha_inicio']} - {empresa_info['fecha_fin']}</div>", unsafe_allow_html=True)
    
    # Obtener diario
    diario = obtener_diario()
    
    if not diario.empty:
        # Agrupar por asiento (id de diario)
        asientos = diario['id'].unique()
        
        for asiento in asientos:
            # Filtrar movimientos por asiento
            movimientos = diario[diario['id'] == asiento]
            
            # Obtener información del asiento
            fecha = movimientos['fecha'].iloc[0]
            descripcion = movimientos['descripcion'].iloc[0]
            folio = movimientos['folio'].iloc[0]
            
            # Mostrar información del asiento
            st.markdown(f"<div class='section'>Asiento {folio} - {fecha}</div>", unsafe_allow_html=True)
            st.markdown(f"<strong>Descripción:</strong> {descripcion}")
            
            # Mostrar movimientos
            tabla_movimientos = movimientos[['cuenta', 'debe', 'haber']].copy()
            tabla_movimientos['debe'] = tabla_movimientos['debe'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
            tabla_movimientos['haber'] = tabla_movimientos['haber'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
            
            st.dataframe(tabla_movimientos, use_container_width=True)
            
            # Calcular totales
            total_debe = movimientos['debe'].sum()
            total_haber = movimientos['haber'].sum()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Debe", f"${total_debe:,.2f}")
            
            with col2:
                st.metric("Total Haber", f"${total_haber:,.2f}")
            
            st.markdown("---")
        
        # Generar botón para descargar
        diario_csv = diario.copy()
        st.markdown(get_df_to_csv_download_link(diario_csv, 'libro_diario.csv', 'Descargar Libro Diario'), unsafe_allow_html=True)
    else:
        st.info("No hay transacciones registradas.")

# Página de libro mayor
def pagina_libro_mayor():
    st.markdown("<div class='title'>Libro Mayor</div>", unsafe_allow_html=True)
    
    # Obtener datos de la empresa
    empresa_info = obtener_datos_empresa()
    
    if empresa_info['nombre']:
        st.markdown(f"<div class='info-box'><strong>{empresa_info['nombre']}</strong><br>RFC: {empresa_info['rfc']}<br>Período: {empresa_info['fecha_inicio']} - {empresa_info['fecha_fin']}</div>", unsafe_allow_html=True)
    
    # Obtener libro mayor
    mayor = obtener_mayor()
    
    if mayor:
        # Para cada cuenta en el mayor
        for cuenta in mayor:
            # Mostrar información de la cuenta
            st.markdown(f"<div class='subtitle'>{cuenta['cuenta']}</div>", unsafe_allow_html=True)
            st.markdown(f"<strong>Naturaleza:</strong> {cuenta['naturaleza']}")
            
            # Mostrar movimientos
            if not cuenta['movimientos'].empty:
                tabla_movimientos = cuenta['movimientos'].copy()
                tabla_movimientos['debe'] = tabla_movimientos['debe'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
                tabla_movimientos['haber'] = tabla_movimientos['haber'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
                
                st.dataframe(tabla_movimientos, use_container_width=True)
                
                # Mostrar totales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Debe", f"${cuenta['debe_total']:,.2f}")
                
                with col2:
                    st.metric("Total Haber", f"${cuenta['haber_total']:,.2f}")
                
                with col3:
                    st.metric("Saldo", f"${abs(cuenta['saldo']):,.2f} {'Deudor' if cuenta['saldo'] >= 0 else 'Acreedor'}")
            else:
                st.info(f"No hay movimientos para la cuenta {cuenta['cuenta']}.")
            
            st.markdown("---")
    else:
        st.info("No hay transacciones registradas.")

# Página de balanza de comprobación
def pagina_balanza_comprobacion():
    st.markdown("<div class='title'>Balanza de Comprobación</div>", unsafe_allow_html=True)
    
    # Obtener datos de la empresa
    empresa_info = obtener_datos_empresa()
    
    if empresa_info['nombre']:
        st.markdown(f"<div class='info-box'><strong>{empresa_info['nombre']}</strong><br>RFC: {empresa_info['rfc']}<br>Período: {empresa_info['fecha_inicio']} - {empresa_info['fecha_fin']}</div>", unsafe_allow_html=True)
    
    # Obtener balanza
    balanza, total_debe, total_haber, total_saldo_deudor, total_saldo_acreedor = obtener_balanza()
    
    if not balanza.empty:
        # Convertir a valores legibles
        balanza_display = balanza.copy()
        balanza_display['total_debe'] = balanza_display['total_debe'].apply(lambda x: f"${x:,.2f}")
        balanza_display['total_haber'] = balanza_display['total_haber'].apply(lambda x: f"${x:,.2f}")
        balanza_display['saldo_deudor'] = balanza_display['saldo_deudor'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
        balanza_display['saldo_acreedor'] = balanza_display['saldo_acreedor'].apply(lambda x: f"${x:,.2f}" if x > 0 else "")
        
        # Mostrar balanza
        st.dataframe(balanza_display[['codigo', 'nombre', 'total_debe', 'total_haber', 'saldo_deudor', 'saldo_acreedor']], use_container_width=True)
        
        # Mostrar totales
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Movimientos Debe", f"${total_debe:,.2f}")
            st.metric("Total Saldo Deudor", f"${total_saldo_deudor:,.2f}")
        
        with col2:
            st.metric("Total Movimientos Haber", f"${total_haber:,.2f}")
            st.metric("Total Saldo Acreedor", f"${total_saldo_acreedor:,.2f}")
        
        # Verificar si la balanza cuadra
        if abs(total_debe - total_haber) < 0.01 and abs(total_saldo_deudor - total_saldo_acreedor) < 0.01:
            st.success("La balanza de comprobación está cuadrada.")
        else:
            st.error("La balanza de comprobación no está cuadrada.")
        
        # Generar botón para descargar
        st.markdown(get_df_to_csv_download_link(balanza_display, 'balanza_comprobacion.csv', 'Descargar Balanza de Comprobación'), unsafe_allow_html=True)
    else:
        st.info("No hay transacciones registradas.")

# Página de estado de resultados
def pagina_estado_resultados():
    st.markdown("<div class='title'>Estado de Resultados</div>", unsafe_allow_html=True)
    
    # Obtener datos de la empresa
    empresa_info = obtener_datos_empresa()
    
    if empresa_info['nombre']:
        st.markdown(f"<div class='card'><strong>{empresa_info['nombre']}</strong><br>RFC: {empresa_info['rfc']}<br>Estado de Resultados<br>Período: {empresa_info['fecha_inicio']} - {empresa_info['fecha_fin']}</div>", unsafe_allow_html=True)
    
    # Obtener estado de resultados
    estado = obtener_estado_resultados()
    
    # Mostrar estado de resultados
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("<div class='section'>Ingresos</div>", unsafe_allow_html=True)
        st.markdown(f"Ventas: ${estado['ventas']:,.2f}")
        st.markdown(f"(-) Devoluciones sobre Ventas: ${estado['dev_ventas']:,.2f}")
        st.markdown(f"(-) Rebajas sobre Ventas: ${estado['reb_ventas']:,.2f}")
        st.markdown(f"(-) Descuentos sobre Ventas: ${estado['desc_ventas']:,.2f}")
    
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown(f"<strong>Ventas Netas: ${estado['ventas_netas']:,.2f}</strong>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])

if __name__ == "__main__":
    main()