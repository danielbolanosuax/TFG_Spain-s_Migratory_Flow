import requests

# IDs de tablas INE más relevantes:
# 4247 = Tasa de paro EPA por CCAA
# 9946 = Renta media por hogar (ECV)
# 2852 = Densidad de población

INE_TABLES = {
    "tasa_paro": "4247",
    "renta_media": "9946",
    "densidad_poblacion": "2852",
}

def get_ine_tabla(tabla_id: str):
    url = f"https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tabla_id}?tip=AM"
    return requests.get(url).json()

def collect_economico():
    result = {}
    for nombre, tid in INE_TABLES.items():
        result[nombre] = get_ine_tabla(tid)
    return result
