# collectors/idealista.py
# Colector de precios de vivienda via API Idealista v3.5
# Documentación: oauth2 + property-search-api-v3.5
# Límite: 100 peticiones/mes — CRÍTICO respetar este límite

import requests
import base64
import json
import os
from datetime import datetime


# ──────────────────────────────────────────────
# CREDENCIALES
# ──────────────────────────────────────────────
API_KEY = os.getenv("IDEALISTA_API_KEY", "eynr8cy6j091vrd385j1i44fxyvzr8bs")
SECRET  = os.getenv("IDEALISTA_SECRET",  "UUBIW2zTpJEC")


# ──────────────────────────────────────────────
# CIUDADES OBJETIVO
# ──────────────────────────────────────────────
CITIES = {
    "madrid":    "40.416775,-3.703790",
    "barcelona": "41.385064,2.173403",
    "valencia":  "39.469907,-0.376288",
    "sevilla":   "37.389092,-5.984459",
    "zaragoza":  "41.648823,-0.889085",
    "malaga":    "36.721261,-4.421265",
    "bilbao":    "43.263012,-2.934985",
}


# ──────────────────────────────────────────────
# CONTROL DE PETICIONES
# ──────────────────────────────────────────────
REQUESTS_LOG = os.path.join(
    os.path.dirname(__file__), "..", "data", "idealista_requests_log.json"
)
MAX_MONTHLY   = 100
SAFETY_BUFFER = 20  # Nunca gastar las últimas 20 — reserva de emergencia


def _load_log():
    if os.path.exists(REQUESTS_LOG):
        with open(REQUESTS_LOG) as f:
            return json.load(f)
    return {}


def _save_log(log):
    os.makedirs(os.path.dirname(REQUESTS_LOG), exist_ok=True)
    with open(REQUESTS_LOG, "w") as f:
        json.dump(log, f, indent=2)


def _check_and_register_request(dry_run=False):
    """
    Verifica el límite mensual con buffer de seguridad.
    dry_run=True → solo comprueba, NO registra ni gasta petición.
    Lanza Exception si se supera el límite efectivo (MAX - SAFETY_BUFFER).
    """
    month_key      = datetime.now().strftime("%Y-%m")
    log            = _load_log()
    count          = log.get(month_key, 0)
    limite_efectivo = MAX_MONTHLY - SAFETY_BUFFER  # 80 peticiones reales disponibles

    if count >= MAX_MONTHLY:
        raise Exception(
            f"⛔ LÍMITE TOTAL alcanzado: {count}/{MAX_MONTHLY} en {month_key}. "
            f"Reinicia el mes o contacta con Idealista."
        )

    if count >= limite_efectivo:
        raise Exception(
            f"⚠️  BUFFER DE SEGURIDAD activado: {count}/{MAX_MONTHLY} usadas. "
            f"Quedan solo {MAX_MONTHLY - count} (buffer reservado: {SAFETY_BUFFER}). "
            f"No se ejecutará hasta el próximo mes para proteger el límite."
        )

    if dry_run:
        print(f"  🔍 [DRY RUN] Sería petición {count + 1}/{MAX_MONTHLY} — no registrada")
        return count

    log[month_key] = count + 1
    _save_log(log)
    print(f"  📊 Petición {count + 1}/{MAX_MONTHLY} | quedan {MAX_MONTHLY - count - 1} "
          f"({SAFETY_BUFFER} en buffer reservado)")
    return count + 1


# ──────────────────────────────────────────────
# AUTENTICACIÓN OAuth2
# ──────────────────────────────────────────────
def get_token():
    credentials = f"{API_KEY}:{SECRET}"
    encoded     = base64.b64encode(credentials.encode()).decode()

    url     = "https://api.idealista.com/oauth/token"
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type":  "application/x-www-form-urlencoded;charset=UTF-8",
    }
    data = "grant_type=client_credentials&scope=read"

    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        r.raise_for_status()
        token_data = r.json()
        print(f"  🔑 Token obtenido. Expira en {token_data.get('expires_in', '?')} segundos")
        return token_data["access_token"]
    except Exception as e:
        return {"error": f"Error obteniendo token: {str(e)}"}


# ──────────────────────────────────────────────
# BÚSQUEDA
# multipart/form-data con requests requiere files={}, NO data={}
# Cada campo va como (None, valor) — así curl -F lo hace internamente
# NO se pone Content-Type manualmente — requests genera el boundary correcto
# ──────────────────────────────────────────────
def search_properties(token, center, operation="sale", page=1, dry_run=False):
    _check_and_register_request(dry_run=dry_run)

    if dry_run:
        print(f"  🔍 [DRY RUN] Simularía: center={center} op={operation} pág={page}")
        return {"elementList": [], "total": 0, "_dry_run": True}

    url     = "https://api.idealista.com/3.5/es/search"
    headers = {"Authorization": f"Bearer {token}"}
    files   = {
        "center":       (None, center),
        "distance":     (None, "15000"),
        "propertyType": (None, "homes"),
        "operation":    (None, operation),
        "maxItems":     (None, "50"),
        "numPage":      (None, str(page)),
        "country":      (None, "es"),
        "locale":       (None, "es"),
    }

    try:
        r = requests.post(url, headers=headers, files=files, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────
# PROCESADO
# ──────────────────────────────────────────────
def _parse_elements(elements, city, operation, snapshot_date):
    rows = []
    for item in elements:
        price = item.get("price")
        size  = item.get("size")
        if not price or not size:
            continue
        rows.append({
            "snapshot_date":  snapshot_date,
            "city":           city,
            "operation":      operation,
            "propertyCode":   item.get("propertyCode"),
            "price":          price,
            "size_m2":        size,
            "price_m2":       round(price / size, 2),
            "rooms":          item.get("rooms"),
            "bathrooms":      item.get("bathrooms"),
            "floor":          item.get("floor"),
            "exterior":       item.get("exterior"),
            "district":       item.get("district"),
            "municipality":   item.get("municipality"),
            "neighborhood":   item.get("neighborhood"),
            "province":       item.get("province"),
            "latitude":       item.get("latitude"),
            "longitude":      item.get("longitude"),
            "newDevelopment": item.get("newDevelopment"),
            "status":         item.get("status"),
            "url":            item.get("url"),
        })
    return rows


# ──────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────
def collect_idealista(dry_run=False):
    """
    Recoge precios de vivienda de Idealista para las 7 ciudades objetivo.
    dry_run=True → simula todo el flujo sin hacer llamadas reales (0 peticiones).
    """
    if dry_run:
        print("  🔍 [DRY RUN] Modo simulación — no se gastarán peticiones")

    snapshot_date = datetime.now().strftime("%Y-%m-%d")
    result = {
        "timestamp":                  datetime.now().isoformat(),
        "snapshot_date":              snapshot_date,
        "fuente":                     "Idealista API v3.5",
        "peticiones_usadas_este_mes": None,
        "dry_run":                    dry_run,
        "ciudades":                   {},
    }

    print("  🔑 Autenticando en Idealista API...")
    token = get_token()
    if isinstance(token, dict) and "error" in token:
        result["error"] = token["error"]
        return result

    all_rows = []

    for city, center in CITIES.items():
        result["ciudades"][city] = {}

        for operation in ["sale", "rent"]:
            print(f"  🏘️  {city.upper()} — {operation}...")
            try:
                data = search_properties(token, center, operation=operation, dry_run=dry_run)

                # Dry run — no hay datos reales, saltar
                if data.get("_dry_run"):
                    result["ciudades"][city][operation] = {"dry_run": True}
                    continue

                if "error" in data:
                    print(f"  ❌ Error: {data['error']}")
                    result["ciudades"][city][operation] = {"error": data["error"]}
                    continue

                elements       = data.get("elementList", [])
                rows           = _parse_elements(elements, city, operation, snapshot_date)
                all_rows.extend(rows)

                precio_m2_vals = [r["price_m2"] for r in rows]
                result["ciudades"][city][operation] = {
                    "total_anuncios_mercado": data.get("total", 0),
                    "anuncios_capturados":    len(rows),
                    "precio_medio_m2":   round(sum(precio_m2_vals) / len(precio_m2_vals), 2) if precio_m2_vals else None,
                    "precio_mediano_m2": sorted(precio_m2_vals)[len(precio_m2_vals) // 2]    if precio_m2_vals else None,
                }
                print(f"  → {len(rows)} anuncios | "
                      f"precio medio {result['ciudades'][city][operation]['precio_medio_m2']} €/m²")

            except Exception as e:
                # Buffer o límite alcanzado — parar inmediatamente
                if "BUFFER" in str(e) or "LÍMITE" in str(e):
                    print(f"\n{e}")
                    result["advertencia"] = str(e)
                    # Salir de ambos bucles
                    city = None
                    break
                print(f"  ❌ {city}/{operation}: {e}")
                result["ciudades"][city][operation] = {"error": str(e)}

        if city is None:
            break

    log = _load_log()
    month_key = datetime.now().strftime("%Y-%m")
    result["peticiones_usadas_este_mes"] = log.get(month_key, 0)
    result["anuncios"]                   = all_rows

    print(f"\n  ✅ Total anuncios procesados: {len(all_rows)}")
    print(f"  📊 Peticiones usadas este mes: {result['peticiones_usadas_este_mes']}/{MAX_MONTHLY}")

    return result