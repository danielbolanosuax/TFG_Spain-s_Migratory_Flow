"""
scheduler.py — Orquestador diario de collectors

Ejecuta los collectors:
- economico
- ambiental
- conectividad
- evr

Guarda la salida como JSON en:
data/{categoria}/{año}/{mes}/{dd_mm_yyyy}.json

Modo standalone:
    python scheduler.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

from collectors.economico import collect_economico
from collectors.ambiental import collect_ambiental
from collectors.conectividad import collect_conectividad
from collectors.evr import collect as collect_evr

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

def save_json(categoria: str, datos: dict) -> None:
    """Guarda el JSON de un collector en data/{categoria}/{año}/{mes}/{fecha}.json."""
    ahora = datetime.now()
    fecha = ahora.strftime("%d_%m_%Y")
    anio = ahora.strftime("%Y")
    mes = ahora.strftime("%m")

    carpeta = ROOT / "data" / categoria / anio / mes
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta = carpeta / f"{fecha}.json"
    with ruta.open("w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"  ✅ {ruta.relative_to(ROOT)}")

def job_diario() -> None:
    """Ejecuta una pasada completa de todos los collectors."""
    print(f"\n🚀 Pipeline arrancado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    print("📊 Económico...")
    save_json("economico", collect_economico())

    print("🌿 Ambiental...")
    save_json("ambiental", collect_ambiental())

    print("📡 Conectividad...")
    save_json("conectividad", collect_conectividad())

    print("🔀 EVR — Flujos migratorios...")
    save_json("evr", collect_evr())

    print("🎉 Pipeline completado.\n")

if __name__ == "__main__":
    # Ejecuta inmediatamente al arrancar
    job_diario()

    # Programa ejecución diaria a las 07:00 (hora de Madrid)
    scheduler = BlockingScheduler(timezone="Europe/Madrid")
    scheduler.add_job(job_diario, "cron", hour=7, minute=0)
    print("⏰ Scheduler activo (07:00 Madrid). Ctrl+C para parar.")
    scheduler.start()