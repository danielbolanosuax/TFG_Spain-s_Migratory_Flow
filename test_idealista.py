"""
test_idealista.py — Test aislado del collector de Idealista
Ejecutar: python test_idealista.py
NO consume el pipeline completo, solo prueba el collector.
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from collectors.idealista import get_token, search_properties, collect_idealista, _load_log

# ──────────────────────────────────────────────
# TEST 0 — Dryrun para testing
# ──────────────────────────────────────────────
# En test_idealista.py — añadir función y llamarla en main

def test_dry_run():
    """Simula la colección completa sin gastar ni una petición."""
    print("\n🔍 TEST 0: Dry run completo (0 peticiones)...")
    from collectors.idealista import collect_idealista
    result = collect_idealista(dry_run=True)
    print(f"  ✅ Dry run OK — snapshot_date: {result['snapshot_date']}")

# En main(), añadir antes de test_token():
# test_dry_run()


# ──────────────────────────────────────────────
# TEST 1 — Solo el token (no gasta peticiones)
# ──────────────────────────────────────────────
def test_token():
    print("\n🔑 TEST 1: Autenticación OAuth2...")
    token = get_token()
    if isinstance(token, dict) and "error" in token:
        print(f"  ❌ FALLO: {token['error']}")
        return None
    print(f"  ✅ Token OK: {token[:20]}...")
    return token


# ──────────────────────────────────────────────
# TEST 2 — Una sola petición (gasta 1 de 100)
# ──────────────────────────────────────────────
def test_una_ciudad(token):
    print("\n🏘️  TEST 2: Una búsqueda (Madrid — sale) — gasta 1 petición...")
    result = search_properties(token, center="40.416775,-3.703790", operation="sale")

    if "error" in result:
        print(f"  ❌ FALLO: {result['error']}")
        return False

    total    = result.get("total", 0)
    elements = result.get("elementList", [])
    print(f"  ✅ Respuesta OK")
    print(f"     Total en mercado: {total:,} anuncios")
    print(f"     Capturados ahora: {len(elements)}")
    if elements:
        e = elements[0]
        print(f"     Ejemplo — {e.get('address', 'sin dirección')} | "
              f"{e.get('price', '?')} € | {e.get('size', '?')} m² | "
              f"{e.get('district', '?')} ({e.get('municipality', '?')})")
    return True


# ──────────────────────────────────────────────
# TEST 3 — Colección completa (gasta 14 peticiones)
# Solo ejecutar cuando TEST 2 esté confirmado OK
# ──────────────────────────────────────────────
def test_completo():
    print("\n🚀 TEST 3: Colección completa (14 peticiones)...")
    result = collect_idealista()

    if "error" in result:
        print(f"  ❌ FALLO global: {result['error']}")
        return

    total_anuncios = len(result.get("anuncios", []))
    print(f"\n  📊 RESUMEN:")
    print(f"     Anuncios totales capturados: {total_anuncios}")
    print(f"     Peticiones usadas este mes:  {result['peticiones_usadas_este_mes']}/100")
    print(f"\n  Por ciudad:")
    for ciudad, ops in result.get("ciudades", {}).items():
        for op, stats in ops.items():
            if isinstance(stats, dict) and "error" not in stats:
                print(f"     {ciudad:12} {op:5} → "
                      f"{stats.get('anuncios_capturados'):>3} anuncios | "
                      f"{stats.get('precio_medio_m2'):>8} €/m²")
            else:
                print(f"     {ciudad:12} {op:5} → ❌ {stats.get('error', '?')[:60]}")


# ──────────────────────────────────────────────
# ESTADO DEL CONTADOR — sin gastar nada
# ──────────────────────────────────────────────
def show_counter():
    from datetime import datetime
    month_key = datetime.now().strftime("%Y-%m")
    log = _load_log()
    usado = log.get(month_key, 0)
    print(f"\n📊 CONTADOR: {usado}/100 peticiones usadas en {month_key}")
    print(f"   Quedan: {100 - usado} peticiones este mes")


# ──────────────────────────────────────────────
# MAIN — elige qué test ejecutar
# ──────────────────────────────────────────────
# En test_idealista.py — en el bloque main, deja así:

if __name__ == "__main__":
    show_counter()
    token = test_token()
    if not token:
        sys.exit(1)

    # TEST 2 — comenta esta línea ya que está confirmado ✅
    # ok = test_una_ciudad(token)

    # TEST 3 — descomenta esta línea
    test_completo()

    show_counter()
    print("\n✅ Tests finalizados")