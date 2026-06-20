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
# CREDENCIALES (ya están en tu .env del proyecto)
# ──────────────────────────────────────────────
API_KEY = os.getenv("IDEALISTA_API_KEY", "eynr8cy6j091vrd385j1i44fxyvzr8bs")
SECRET   = os.getenv("IDEALISTA_SECRET",  "UUBIW2zTpJEC")

# ──────────────────────────────────────────────
# CIUDADES OBJETIVO — adaptadas a tu análisis migratorio
# Cada ciudad = 2 peticiones (sale + rent) = 14 peticiones/mes
# Quedan 86 peticiones de margen para el resto del mes
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
# CONTROL DE PETICIONES — archivo de log mensual
# Se guarda en data/ igual que el resto de tu proyecto
# ──────────────────────────────────────────────
REQUESTS_LOG = os.path.join(
    os.path.dirname(__file__), "..", "data", "idealista_requests_log.json"
)
MAX_MONTHLY = 100


def _load_log():
    """Lee el log de peticiones del mes actual."""
    if os.path.exists(REQUESTS_LOG):
        with open(REQUESTS_LOG) as f:
            return json.load(f)
    return {}


def _save_log(log):
    os.makedirs(os.path.dirname(REQUESTS_LOG), exist_ok=True)
    with open(REQUESTS_LOG, "w") as f:
        json.dump(log, f, indent=2)


def _check_and_register_request():
    """
    Verifica que no hemos superado las 100 peticiones del mes.
    Si todo OK, registra la petición y devuelve True.
    Si se supera el límite, lanza una excepción — no hace la llamada.
    """
    month_key = datetime.now().strftime("%Y-%m")
    log = _load_log()
    count = log.get(month_key, 0)

    if count >= MAX_MONTHLY:
        raise Exception(
            f"⛔ LÍMITE ALCANZADO: {count}/{MAX_MONTHLY} peticiones en {month_key}. "
            f"No se realizará ninguna llamada más hasta el próximo mes."
        )

    log[month_key] = count + 1
    _save_log(log)
    print(f"  📊 Petición {count + 1}/{MAX_MONTHLY} del mes {month_key}")
    return count + 1


# ──────────────────────────────────────────────
# AUTENTICACIÓN OAuth2
# Según documentación: POST /oauth/token con credenciales en Base64
# ──────────────────────────────────────────────
def get_token():
    """
    Obtiene el Bearer Token de Idealista.
    El token dura ~12 horas (43.199 segundos según la documentación).
    Esta llamada NO cuenta en el límite de 100 — es de autenticación.
    """
    credentials = f"{API_KEY}:{SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    url = "https://api.idealista.com/oauth/token"
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "read",   # Solo lectura — lo único que necesitamos
    }

    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        r.raise_for_status()
        token_data = r.json()
        print(f"  🔑 Token obtenido. Expira en {token_data.get('expires_in', '?')} segundos")
        return token_data["access_token"]
    except Exception as e:
        return {"error": f"Error obteniendo token: {str(e)}"}


# ──────────────────────────────────────────────
# LLAMADA A LA API DE BÚSQUEDA
# Endpoint documentado: POST /3.5/es/search
# ──────────────────────────────────────────────
def search_properties(token, center, operation="sale", page=1):
    """
    Búsqueda de propiedades por coordenadas.
    - center: "latitud,longitud" en WGS84 (obligatorio según documentación)
    - operation: "sale" o "rent" (únicos valores permitidos)
    - maxItems: 50 (máximo permitido por la API)
    - Cada llamada a esta función = 1 petición de las 100 mensuales
    """
    _check_and_register_request()   # ← Verifica límite ANTES de llamar

    url = "https://api.idealista.com/3.5/es/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "multipart/form-data",
    }
    params = {
        "center":       center,
        "distance":     15000,       # 15 km de radio
        "propertyType": "homes",     # viviendas residenciales
        "operation":    operation,
        "maxItems":     50,          # máximo que permite la API
        "numPage":      page,
        "country":      "es",
        "locale":       "es",
    }

    try:
        r = requests.post(url, headers=headers, data=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────
# PROCESADO — extrae los campos relevantes para el TFG
# ──────────────────────────────────────────────
def _parse_elements(elements, city, operation, snapshot_date):
    """
    Transforma la lista de anuncios en filas planas.
    Solo extrae los campos útiles para análisis de migración + vivienda.
    """
    rows = []
    for item in elements:
        price = item.get("price")
        size  = item.get("size")
        if not price or not size:
            continue   # Descarta anuncios sin precio ni tamaño
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
# FUNCIÓN PRINCIPAL — collect_idealista()
# Mismo patrón que collect_economico() en economico.py
# ──────────────────────────────────────────────
def collect_idealista():
    """
    Recoge precios de vivienda de las principales ciudades españolas.
    Ejecuta: 7 ciudades × 2 operaciones = 14 peticiones al mes.
    Guarda un snapshot JSON en data/ (igual que el resto de collectors).
    """
    snapshot_date = datetime.now().strftime("%Y-%m-%d")
    result = {
        "timestamp":     datetime.now().isoformat(),
        "snapshot_date": snapshot_date,
        "fuente":        "Idealista API v3.5",
        "peticiones_usadas_este_mes": None,
        "ciudades": {}
    }

    # Obtener token una sola vez para todas las ciudades
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
                data = search_properties(token, center, operation=operation)

                if "error" in data:
                    print(f"  ❌ Error: {data['error']}")
                    result["ciudades"][city][operation] = {"error": data["error"]}
                    continue

                total     = data.get("total", 0)
                elements  = data.get("elementList", [])
                rows      = _parse_elements(elements, city, operation, snapshot_date)
                all_rows.extend(rows)

                result["ciudades"][city][operation] = {
                    "total_anuncios_mercado": total,
                    "anuncios_capturados":    len(rows),
                    "precio_medio_m2":        round(
                        sum(r["price_m2"] for r in rows) / len(rows), 2
                    ) if rows else None,
                    "precio_mediano_m2":      sorted(
                        [r["price_m2"] for r in rows]
                    )[len(rows) // 2] if rows else None,
                }
                print(f"  → {len(rows)} anuncios | precio medio {result['ciudades'][city][operation]['precio_medio_m2']} €/m²")

            except Exception as e:
                # Si se agota el límite mensual, para todo y guarda lo que hay
                if "LÍMITE ALCANZADO" in str(e):
                    print(f"\n{e}")
                    result["advertencia"] = str(e)
                    break
                print(f"  ❌ {city}/{operation}: {e}")
                result["ciudades"][city][operation] = {"error": str(e)}

    # Resumen de peticiones usadas
    log = _load_log()
    month_key = datetime.now().strftime("%Y-%m")
    result["peticiones_usadas_este_mes"] = log.get(month_key, 0)

    # Guardar lista plana de anuncios para cruzar con datos migratorios
    result["anuncios"] = all_rows
    print(f"\n  ✅ Total anuncios procesados: {len(all_rows)}")
    print(f"  📊 Peticiones usadas este mes: {result['peticiones_usadas_este_mes']}/{MAX_MONTHLY}")

    return result