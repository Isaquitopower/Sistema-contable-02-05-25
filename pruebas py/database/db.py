import sqlite3
import os

DB_NAME = "controlfinanciero.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def initialize_database():
    if not os.path.exists(DB_NAME):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE arqueo_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                saldo_inicial REAL,
                entradas REAL,
                salidas REAL,
                saldo_esperado REAL,
                saldo_real REAL,
                diferencia REAL,
                fecha TEXT
            );
        ''')

        cursor.execute('''
            CREATE TABLE estado_resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ventas_totales REAL,
                descuentos_ventas REAL,
                devoluciones_ventas REAL,
                rebajas_ventas REAL,
                ventas_net REAL,
                compras REAL,
                gastos_compras REAL,
                devoluciones_compras REAL,
                rebajas_compras REAL,
                descuentos_compras REAL,
                compras_net REAL,
                inventario_final REAL,
                costo_ventas REAL,
                utilidad_bruta REAL,
                gastos_operacion REAL,
                perdida_operacion REAL,
                fecha TEXT
            );
        ''')

        cursor.execute('''
            CREATE TABLE diario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                cuenta TEXT,
                debe REAL,
                haber REAL
            );
        ''')

        cursor.execute('''
            CREATE TABLE mayor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta TEXT,
                debe REAL,
                haber REAL,
                saldo REAL
            );
        ''')

        cursor.execute('''
            CREATE TABLE balanza (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta TEXT,
                movimientos_debe REAL,
                movimientos_haber REAL,
                saldos_debe REAL,
                saldos_haber REAL
            );
        ''')

        conn.commit()
        conn.close()

# Ejecutar solo si se corre directamente
if __name__ == "__main__":
    initialize_database()
