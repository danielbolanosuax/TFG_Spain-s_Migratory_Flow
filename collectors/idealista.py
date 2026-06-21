# collectors/idealista.py
# Colector de precios de vivienda via Idealista Property Search API v3.5
# Documentación: oauth2 + property-search-api-v3.5
# Límite: 100 peticiones/mes — CRÍTICO respetar este límite
#
# Credenciales:
#   IDEALISTA_API_KEY  en entorno / .env
#   IDEALISTA_SECRET   en entorno / .env
#
# Uso desde trigger.py:
#   from collectors.idealista import collect_idealista
#   datos = collect_idealista(dry_run=False, pages_per_segment=1)

from __future__ import annotations

import os
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv 


# ──────────────────────────────────────────────
# PATHS BASE (robusto)
# ──────────────────────────────────────────────

# collectors/idealista.py → collectors/ → ROOT (proyecto)
_HERE = Path(__file__).resolve().parent          # .../collectors
ROOT = _HERE.parent                              # raíz del repo

# Cargar variables desde .env en la raíz
load_dotenv(ROOT / ".env")

REQUESTS_LOG = ROOT / "data" / "idealista_requests_log.json"

MAX_MONTHLY = 100
SAFETY_BUFFER = 20  # Nunca gastar las últimas 20 — reserva de emergencia


# ──────────────────────────────────────────────
# CREDENCIALES
# ──────────────────────────────────────────────

# No se ponen valores por defecto para evitar filtrar claves por error.
API_KEY = os.getenv("IDEALISTA_API_KEY")
SECRET = os.getenv("IDEALISTA_SECRET")

if not API_KEY or not SECRET:
    # Levantamos la excepción sólo cuando se use el colector; eso permite
    # importar el módulo sin reventar los tests.
    pass


# ──────────────────────────────────────────────
# CIUDADES OBJETIVO
# ──────────────────────────────────────────────

CITIES: Dict[str, str] = {
    "madrid": "40.416775,-3.703790",
    "barcelona": "41.385064,2.173403",
    "valencia": "39.469907,-0.376288",
    "sevilla": "37.389092,-5.984459",
    "zaragoza": "41.648823,-0.889085",
    "malaga": "36.721261,-4.421265",
    "bilbao": "43.263012,-2.934985",
}

OPERATIONS = ["sale", "rent"]  # venta y alquiler


# ──────────────────────────────────────────────
# CONTROL DE PETICIONES
# ──────────────────────────────────────────────

def _load_log() -> Dict[str, int]:
    if REQUESTS_LOG.exists():
        with open(REQUESTS_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_log(log: Dict[str, int]) -> None:
    REQUESTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(REQUESTS_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


def _check_and_register_request(dry_run: bool = False, n: int = 1) -> int:
    """
    Verifica el límite mensual con buffer de seguridad.

    - dry_run=True → solo comprueba, NO registra ni gasta petición.
    - n → número de peticiones que se quieren registrar (por defecto 1).

    Lanza Exception si se supera el límite efectivo (MAX_MONTHLY - SAFETY_BUFFER).
    Devuelve el total acumulado tras el registro (o el valor actual en dry_run).
    """
    month_key = datetime.now().strftime("%Y-%m")
    log = _load_log()
    count = log.get(month_key, 0)
    limite_efectivo = MAX_MONTHLY - SAFETY_BUFFER  # p.ej. 80 peticiones reales

    if count + n > MAX_MONTHLY:
        raise RuntimeError(
            f"⛔ LÍMITE TOTAL alcanzado: {count}/{MAX_MONTHLY} en {month_key}. "
            f"Intentabas añadir {n} peticiones más. Reinicia el mes o contacta con Idealista."
        )

    if count + n > limite_efectivo:
        raise RuntimeError(
            f"⚠️ BUFFER DE SEGURIDAD activado: {count}/{MAX_MONTHLY} usadas. "
            f"Quedan solo {MAX_MONTHLY - count} (buffer reservado: {SAFETY_BUFFER}). "
            f"El collector no se ejecutará hasta el próximo mes para proteger el límite."
        )

    if dry_run:
        print(
            f" 🔍 [DRY RUN] Serían peticiones {count + 1}–{count + n}/{MAX_MONTHLY} "
            f"— no se registran"
        )
        return count

    # Registrar
    log[month_key] = count + n
    _save_log(log)
    print(
        f" 📊 Peticiones {count + 1}–{count + n}/{MAX_MONTHLY} | "
        f"quedan {MAX_MONTHLY - count - n} (buffer={SAFETY_BUFFER})"
    )
    return count + n


# ──────────────────────────────────────────────
# AUTENTICACIÓN OAuth2
# ──────────────────────────────────────────────

def get_token() -> str:
    """
    Obtiene un token OAuth2 Bearer para la API de Idealista.

    Lanza RuntimeError si faltan credenciales o si la petición falla.
    """
    if not API_KEY or not SECRET:
        raise RuntimeError(
            "❌ Credenciales Idealista no configuradas. "
            "Define IDEALISTA_API_KEY e IDEALISTA_SECRET en el entorno o en .env."
        )

    credentials = f"{API_KEY}:{SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    url = "https://api.idealista.com/oauth/token"
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    data = "grant_type=client_credentials&scope=read"

    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        r.raise_for_status()
        token_data = r.json()
        print(f" 🔑 Token obtenido. Expira en {token_data.get('expires_in', '?')} segundos")
        return token_data["access_token"]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Error obteniendo token de Idealista: {e}") from e


# ──────────────────────────────────────────────
# BÚSQUEDA
# ──────────────────────────────────────────────

def search_properties(
    token: str,
    center: str,
    operation: str = "sale",
    page: int = 1,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Lanza una búsqueda contra la API de Idealista.

    - center: "lat,lon"
    - operation: "sale" o "rent"
    - page: página (1, 2, ...)
    """
    # Cada llamada cuenta como 1 petición
    _check_and_register_request(dry_run=dry_run, n=1)

    if dry_run:
        print(f" 🔍 [DRY RUN] Simularía: center={center} op={operation} pág={page}")
        return {"elementList": [], "total": 0, "_dry_run": True}

    url = "https://api.idealista.com/3.5/es/search"
    headers = {"Authorization": f"Bearer {token}"}
    # multipart/form-data con requests → usar files, no data
    files = {
        "center": (None, center),
        "distance": (None, "15000"),
        "propertyType": (None, "homes"),
        "operation": (None, operation),
        "maxItems": (None, "50"),
        "numPage": (None, str(page)),
        "country": (None, "es"),
        "locale": (None, "es"),
    }

    try:
        r = requests.post(url, headers=headers, files=files, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        # Mostramos cuerpo recortado para debug
        body = ""
        try:
            body = r.text[:300]
        except Exception:  # noqa: BLE001
            body = "<sin cuerpo>"
        return {"error": f"HTTP {r.status_code}: {body}", "exception": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


# ──────────────────────────────────────────────
# PROCESADO
# ──────────────────────────────────────────────

def _parse_elements(
    elements: List[Dict[str, Any]],
    city: str,
    operation: str,
    snapshot_date: str,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in elements:
        price = item.get("price")
        size = item.get("size")
        if price is None or size in (None, 0):
            continue
        try:
            price_f = float(price)
            size_f = float(size)
        except (TypeError, ValueError):
            continue

        rows.append(
            {
                "snapshot_date": snapshot_date,
                "city": city,
                "operation": operation,
                "propertyCode": item.get("propertyCode"),
                "price": price_f,
                "size_m2": size_f,
                "price_m2": round(price_f / size_f, 2),
                "rooms": item.get("rooms"),
                "bathrooms": item.get("bathrooms"),
                "floor": item.get("floor"),
                "exterior": item.get("exterior"),
                "district": item.get("district"),
                "municipality": item.get("municipality"),
                "neighborhood": item.get("neighborhood"),
                "province": item.get("province"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "newDevelopment": item.get("newDevelopment"),
                "status": item.get("status"),
                "url": item.get("url"),
            }
        )
    return rows


# ──────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────

def collect_idealista(
    dry_run: bool = False,
    pages_per_segment: int = 1,
) -> Dict[str, Any]:
    """
    Recoge precios de vivienda de Idealista para las 7 ciudades objetivo.

    Parámetros
    ----------
    dry_run:
        True  → simula todo el flujo sin llamadas reales (0 peticiones).
        False → realiza llamadas reales (respeta el límite mensual).
    pages_per_segment:
        Nº de páginas por (ciudad, operación). Cada página son máx 50 anuncios:
          1 →  1 página  * 7 ciudades * 2 ops = 14 peticiones
          2 →  2 páginas * 7 ciudades * 2 ops = 28 peticiones
          3 →  3 páginas * 7 ciudades * 2 ops = 42 peticiones
    """
    if pages_per_segment < 1:
        raise ValueError("pages_per_segment debe ser >= 1")

    if dry_run:
        print(
            f" 🔍 [DRY RUN] Modo simulación — no se gastarán peticiones "
            f"(pages_per_segment={pages_per_segment})"
        )

    snapshot_date = datetime.now().strftime("%Y-%m-%d")
    month_key = datetime.now().strftime("%Y-%m")

    result: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "snapshot_date": snapshot_date,
        "fuente": "Idealista API v3.5",
        "peticiones_usadas_este_mes": None,
        "dry_run": dry_run,
        "pages_per_segment": pages_per_segment,
        "ciudades": {},
        "anuncios": [],
    }

    # Token (si no es dry_run)
    token: str | None
    if dry_run:
        token = None
    else:
        token = get_token()

    all_rows: List[Dict[str, Any]] = []
    seen_codes: set[str] = set()

    # Bucle ciudad × operación × página
    for city, center in CITIES.items():
        result["ciudades"][city] = {}
        for operation in OPERATIONS:
            print(f" 🏘️ {city.upper()} — {operation}...")
            ciudad_rows: List[Dict[str, Any]] = []
            total_mercado = 0

            for page in range(1, pages_per_segment + 1):
                print(f"    · página {page}/{pages_per_segment}")

                data = search_properties(
                    token=token if token is not None else "",
                    center=center,
                    operation=operation,
                    page=page,
                    dry_run=dry_run,
                )

                # Dry run
                if data.get("_dry_run"):
                    total_mercado = 0
                    continue

                # Error HTTP u otro
                if "error" in data:
                    print(f"    ❌ Error: {data['error']}")
                    result["ciudades"][city][operation] = {
                        "error": data["error"],
                        "dry_run": dry_run,
                    }
                    # Saltamos al siguiente operation; no intentamos más páginas
                    ciudad_rows = []
                    break

                if page == 1:
                    total_mercado = data.get("total", 0)

                elements = data.get("elementList", []) or []
                rows = _parse_elements(elements, city, operation, snapshot_date)

                # Deduplicar por propertyCode
                for r in rows:
                    code = r.get("propertyCode")
                    if code and code not in seen_codes:
                        seen_codes.add(code)
                        ciudad_rows.append(r)

            # Si hubo error en alguna página ya hemos registrado error arriba
            if operation not in result["ciudades"][city]:
                pm2_vals = [r["price_m2"] for r in ciudad_rows]

                result["ciudades"][city][operation] = {
                    "total_anuncios_mercado": int(total_mercado),
                    "anuncios_capturados": len(ciudad_rows),
                    "precio_medio_m2": round(sum(pm2_vals) / len(pm2_vals), 2)
                    if pm2_vals
                    else None,
                    "precio_mediano_m2": (
                        sorted(pm2_vals)[len(pm2_vals) // 2] if pm2_vals else None
                    ),
                    "dry_run": dry_run,
                }

                print(
                    f"    → {len(ciudad_rows)} anuncios | "
                    f"precio medio "
                    f"{result['ciudades'][city][operation]['precio_medio_m2']} €/m²"
                )

            all_rows.extend(ciudad_rows)

    result["anuncios"] = all_rows

    # Meter en el resultado cuántas peticiones lleva el mes
    log = _load_log()
    result["peticiones_usadas_este_mes"] = log.get(month_key, 0)

    print()
    print(f" ✅ Total anuncios capturados: {len(all_rows)}")
    print(
        f"    Peticiones usadas este mes: "
        f"{result['peticiones_usadas_este_mes']}/{MAX_MONTHLY}"
    )

    return result