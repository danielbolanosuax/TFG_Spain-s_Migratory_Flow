import requests, os, json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
AEMET_KEY = os.getenv("AEMET_API_KEY")

def get_clima_aemet():
    headers = {"api_key": AEMET_KEY}
    today = datetime.now().strftime("%Y-%m-%dT00:00:00UTC")
    url = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{today}/fechafin/{today}/todasestaciones"
    r1 = requests.get(url, headers=headers).json()
    if "datos" in r1:
        return requests.get(r1["datos"], headers=headers).json()
    return {}

def get_calidad_aire_miteco():
    # Datos diarios calidad aire MITECO
    url = "https://catalogo.datosabiertos.miteco.gob.es/catalogo/api/3/action/datastore_search?resource_id=DATOS_DIARIOS_CALIDAD_AIRE&limit=500"
    return requests.get(url).json()

def collect_ambiental():
    return {
        "clima_aemet": get_clima_aemet(),
        "calidad_aire": get_calidad_aire_miteco(),
    }
