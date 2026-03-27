import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings()

load_dotenv()
AEMET_KEY  = os.getenv("AEMET_API_KEY")
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "demo")

# Ciudades españolas con estaciones WAQI
CIUDADES_ESPAÑA = [
    "madrid", "barcelona", "valencia", "sevilla", "bilbao",
    "zaragoza", "malaga", "murcia", "palma", "alicante",
    "valladolid", "cordoba", "vigo", "gijon", "granada",
    "vitoria", "santander", "pamplona", "san-sebastian",
    "salamanca", "burgos", "toledo", "cadiz", "huelva",
    "tarragona", "lleida", "girona", "badajoz", "logrono",
    "albacete", "castellon", "tenerife", "las-palmas"
]

def get_observacion_aemet():
    """Observación actual TODAS las estaciones AEMET (~10000 estaciones)"""
    headers = {"api_key": AEMET_KEY, "Accept": "application/json"}
    url = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
    try:
        r1 = requests.get(url, headers=headers, timeout=15).json()
        if r1.get("estado") != 200:
            return {"error": r1.get("descripcion"), "estado": r1.get("estado")}
        datos = requests.get(r1["datos"], headers=headers, timeout=30).json()
        campos = ["idema", "ubi", "lat", "lon", "alt", "fint",
                  "ta", "tamin", "tamax", "prec", "hr",
                  "vv", "vmax", "dv", "dmax", "pres", "pres_nmar",
                  "vis", "inso", "ts", "tpr"]
        return {
            "fuente": "AEMET OpenData - Observación convencional",
            "timestamp_captura": datetime.now().isoformat(),
            "total_estaciones": len(datos),
            "estaciones": [{c: e.get(c) for c in campos} for e in datos]
        }
    except Exception as e:
        return {"error": str(e)}

def get_calidad_aire_waqi():
    """
    Calidad del aire por ciudad española vía WAQI API.
    Contaminantes: AQI, NO2, PM2.5, PM10, O3, SO2, CO, temperatura, humedad
    Actualización: horaria por estación
    """
    datos_ciudades = []
    errores = []

    for ciudad in CIUDADES_ESPAÑA:
        try:
            url = f"https://api.waqi.info/feed/{ciudad}/?token={WAQI_TOKEN}"
            r = requests.get(url, timeout=10)
            d = r.json()

            if d.get("status") == "ok":
                data   = d["data"]
                iaqi   = data.get("iaqi", {})
                ciudad_info = data.get("city", {})
                geo    = ciudad_info.get("geo", [None, None])

                datos_ciudades.append({
                    "ciudad":     ciudad,
                    "nombre":     ciudad_info.get("name"),
                    "lat":        geo[0] if len(geo) > 0 else None,
                    "lon":        geo[1] if len(geo) > 1 else None,
                    "timestamp":  data.get("time", {}).get("s"),
                    "aqi":        data.get("aqi"),
                    "dominante":  data.get("dominentpol"),
                    "NO2":        iaqi.get("no2",  {}).get("v"),
                    "PM25":       iaqi.get("pm25", {}).get("v"),
                    "PM10":       iaqi.get("pm10", {}).get("v"),
                    "O3":         iaqi.get("o3",   {}).get("v"),
                    "SO2":        iaqi.get("so2",  {}).get("v"),
                    "CO":         iaqi.get("co",   {}).get("v"),
                    "temperatura": iaqi.get("t",   {}).get("v"),
                    "humedad":    iaqi.get("h",    {}).get("v"),
                    "presion":    iaqi.get("p",    {}).get("v"),
                    "viento":     iaqi.get("w",    {}).get("v"),
                })
            else:
                errores.append({"ciudad": ciudad, "error": d.get("data", "unknown")})

        except Exception as e:
            errores.append({"ciudad": ciudad, "error": str(e)})

    return {
        "fuente": "WAQI - World Air Quality Index",
        "url_token": "https://aqicn.org/data-platform/token/",
        "timestamp_captura": datetime.now().isoformat(),
        "total_ciudades_ok": len(datos_ciudades),
        "total_errores": len(errores),
        "ciudades": datos_ciudades,
        "errores": errores
    }

def collect_ambiental():
    print("    📡 AEMET observación todas las estaciones...")
    aemet = get_observacion_aemet()
    print(f"    → {aemet.get('total_estaciones', 'error')} estaciones capturadas")

    print("    🌫️  Calidad del aire WAQI (ciudades España)...")
    aire = get_calidad_aire_waqi()
    print(f"    → {aire.get('total_ciudades_ok', 0)}/{len(CIUDADES_ESPAÑA)} ciudades OK | {aire.get('total_errores', 0)} errores")

    return {
        "timestamp": datetime.now().isoformat(),
        "observacion_meteorologica": aemet,
        "calidad_aire": aire,
    }
