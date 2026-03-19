import json, os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from collectors.economico import collect_economico
from collectors.ambiental import collect_ambiental

def save_json(categoria: str, datos: dict):
    fecha = datetime.now().strftime("%d_%m_%Y")
    anio = datetime.now().strftime("%Y")
    mes = datetime.now().strftime("%m")
    carpeta = f"data/{categoria}/{anio}/{mes}"
    os.makedirs(carpeta, exist_ok=True)
    ruta = f"{carpeta}/{fecha}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"✅ Guardado: {ruta}")

def job_diario():
    print(f"🚀 Ejecutando pipeline: {datetime.now()}")
    save_json("economico", collect_economico())
    save_json("ambiental", collect_ambiental())
    # save_json("conectividad", collect_conectividad())

scheduler = BlockingScheduler()
scheduler.add_job(job_diario, 'cron', hour=6, minute=0)  # cada día a las 6AM
print("⏰ Scheduler activo. Ctrl+C para parar.")
scheduler.start()
