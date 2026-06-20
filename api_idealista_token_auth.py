import base64
import requests

API_KEY = "eynr8cy6j091vrd385j1i44fxyvzr8bs"
SECRET = "UUBIW2zTpJEC"

# Paso 1: Codificar credenciales en Base64 (RFC 1738)
credentials = f"{API_KEY}:{SECRET}"
encoded = base64.b64encode(credentials.encode()).decode()

# Paso 2: Solicitar token
def get_token():
    url = "https://api.idealista.com/oauth/token"
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "read"  # solo lectura, según documentación
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()["access_token"]