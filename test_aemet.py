import requests, json
from dotenv import load_dotenv
import os

load_dotenv()
AEMET_KEY = os.getenv("AEMET_API_KEY")
headers = {"api_key": AEMET_KEY, "Accept": "application/json"}

url = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
r1 = requests.get(url, headers=headers).json()
datos = requests.get(r1["datos"], headers=headers).json()

print(f"✅ {len(datos)} estaciones capturadas")
print(f"Ejemplo — {datos[0]['ubi']}: temp={datos[0].get('ta','?')}°C  hr={datos[0].get('hr','?')}%  prec={datos[0].get('prec','?')}mm")
print(f"Ejemplo — {datos[1]['ubi']}: temp={datos[1].get('ta','?')}°C  hr={datos[1].get('hr','?')}%  prec={datos[1].get('prec','?')}mm")
print(f"Ejemplo — {datos[2]['ubi']}: temp={datos[2].get('ta','?')}°C  hr={datos[2].get('hr','?')}%  prec={datos[2].get('prec','?')}mm")
