import json, os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from collectors.economico import collect_economico
from collectors.ambiental import collect_ambiental
from collectors.conectividad import collect_conectividad

def save_json(categoria: str, datos: dict):
    fecha = datetime.now().strftime("%d_%m_%Y")
    anio  = datetime.now().strftime("%Y")
    mes   = datetime.now().strftime("%m")
    carpeta = f"data/{categoria}/{anio}/{mes}"
    os.makedirs(carpeta, exist_ok=True)
    ruta = f"{carpeta}/{fecha}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {ruta}")

def job_diario():
    print(f"\n🚀 Pipeline arrancado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("📊 Económico...")
    save_json("economico", collect_economico())
    print("🌿 Ambiental...")
    save_json("ambiental", collect_ambiental())
    print("📡 Conectividad...")
    save_json("conectividad", collect_conectividad())
    print("🎉 Pipeline completado.\n")

# --- Lanzar una vez ahora + programar diariamente ---
if __name__ == "__main__":
    job_diario()  # ejecuta inmediatamente al arrancar
    scheduler = BlockingScheduler(timezone="Europe/Madrid")
    scheduler.add_job(job_diario, 'cron', hour=7, minute=0)
    print("⏰ Scheduler activo (07:00 Madrid). Ctrl+C para parar.")
    scheduler.start()
