"""
collectors/evr.py
Recoge flujos migratorios interprovinciales del INE (Operación EM)
Tablas:
  24379 — Flujo interprovincial × año × provincia origen/destino × sexo
  24380 — Saldo migratorio interprovincial × año × provincia × sexo × edad
  24339 — Flujo interprovincial × año × sexo × edad (perfil demográfico)
"""

import json
import requests
from datetime import datetime
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────
BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tabla_id}"

TABLAS = {
    'flujo_interprovincial':  24379,  # flujos provincia origen×destino×año×sexo
    'saldo_interprovincial':  24380,  # saldo neto por provincia×año×sexo×edad
    'flujo_edad_sexo':        24339,  # flujo nacional×año×sexo×edad
}

NULT = 100  # últimos N periodos (EVR es anual, 100 cubre todo el histórico)


# ── Parser genérico INE ────────────────────────────────────────────────────────
def fetch_tabla(tabla_id: int, nult: int = NULT) -> list:
    url = BASE_URL.format(tabla_id=tabla_id)
    params = {'nult': nult}
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def parse_tabla(raw: list) -> list:
    """
    Convierte lista de series INE a lista de registros planos.
    Cada serie tiene: COD, Nombre, Data[]
    Nombre contiene las dimensiones separadas por '. '
    """
    registros = []
    for serie in raw:
        nombre = serie.get('Nombre', '')
        data   = serie.get('Data', [])
        if not data:
            continue
        for punto in data:
            if punto.get('Valor') is None:
                continue
            registros.append({
                'nombre_serie': nombre,
                'anyo':         punto.get('Anyo'),
                'valor':        punto.get('Valor'),
                'secreto':      punto.get('Secreto', False),
            })
    return registros


# ── Collector principal ────────────────────────────────────────────────────────
def collect() -> dict:
    timestamp = datetime.now().isoformat()
    resultado = {'timestamp': timestamp}

    for nombre_tabla, tabla_id in TABLAS.items():
        print(f'  Descargando {nombre_tabla} (id={tabla_id})...')
        try:
            raw = fetch_tabla(tabla_id)
            registros = parse_tabla(raw)
            resultado[nombre_tabla] = {
                'tabla_id':  tabla_id,
                'series':    len(raw),
                'registros': len(registros),
                'data':      registros,
            }
            print(f'    ✅ {len(raw)} series | {len(registros)} registros')
        except Exception as e:
            print(f'    ❌ Error en {nombre_tabla}: {e}')
            resultado[nombre_tabla] = {'tabla_id': tabla_id, 'error': str(e)}

    return resultado




# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('🚀 EVR Collector — INE Estadística de Migraciones')
    print(f'   Tablas: {list(TABLAS.keys())}')
    print()
    data = collect()
    print()
    print('📊 Resumen:')
    for k, v in data.items():
        if k == 'timestamp':
            continue
        if 'error' in v:
            print(f'  ❌ {k}: {v["error"]}')
        else:
            print(f'  ✅ {k}: {v["series"]} series | {v["registros"]} registros')
    print('\n✅ Colección completa')
