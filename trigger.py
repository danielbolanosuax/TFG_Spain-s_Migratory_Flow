"""
trigger.py — Pipeline completo TFG Spain's Migratory Flow
Orden: recolección → 01_exploracion → 02_limpieza → 03_visualizacion → 04_merge → 05_insights

Collectors incluidos en PASO 1:
  - economico   (INE, Catastro, Ministerio Vivienda)
  - ambiental   (AEMET, calidad aire)
  - idealista   (API v3.5 — precios vivienda en tiempo real, máx 100 req/mes)

Notebooks idelaista incluidos en fases 01→03:
  - 01_exploracion/01_idealista.ipynb
  - 02_limpieza/02_idealista.ipynb
  - 03_visualizacion/03_idealista.ipynb
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

LOG_DIR = ROOT / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


FASES = {
    "01_exploracion": [
        "notebooks/01_exploracion/01_economico.ipynb",
        "notebooks/01_exploracion/01_ambiental.ipynb",
        "notebooks/01_exploracion/01_conectividad.ipynb",
        "notebooks/01_exploracion/01_evr.ipynb",
        "notebooks/01_exploracion/01_idealista.ipynb",   # ← NUEVO
    ],
    "02_limpieza": [
        "notebooks/02_limpieza/02_ambiental.ipynb",
        "notebooks/02_limpieza/02_economico.ipynb",
        "notebooks/02_limpieza/02_concectividad.ipynb",
        "notebooks/02_limpieza/02_evr.ipynb",
        "notebooks/02_limpieza/02_idealista.ipynb",      # ← NUEVO
    ],
    "03_visualizacion": [
        "notebooks/03_visualizacion/03_ambiental.ipynb",
        "notebooks/03_visualizacion/03_economico.ipynb",
        "notebooks/03_visualizacion/03_conectividad.ipynb",
        "notebooks/03_visualizacion/03_evr.ipynb",
        "notebooks/03_visualizacion/03_idealista.ipynb", # ← NUEVO
    ],
    "04_merge": [
        "notebooks/04_merge/04_merge.ipynb",
    ],
}


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_step(label: str, cmd: list) -> bool:
    log(f"▶  {label}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"✅ OK — {label}")
        return True
    else:
        log(f"❌ FALLO — {label}")
        log(result.stderr[-2000:])
        return False


def run_scheduler_once():
    """
    PASO 1 — Recolección de datos.
    Ejecuta todos los collectors en un único subproceso Python para evitar
    bloqueos del scheduler. Idealista se ejecuta con manejo de límite mensual:
    si el límite de 100 req/mes ya fue alcanzado, el collector lo comunica
    en el JSON de salida pero NO aborta el pipeline — los demás collectors
    siguen ejecutándose con normalidad.
    """
    log("── PASO 1: Recolección de datos ──")
    script = """
import sys, os
sys.path.insert(0, os.getcwd())

from collectors.economico  import collect_economico
from collectors.ambiental  import collect_ambiental
from collectors.idealista  import collect_idealista   # ← NUEVO

import json
from datetime import datetime
from pathlib import Path


def save_json(categoria, datos):
    fecha   = datetime.now().strftime("%d_%m_%Y")
    anio    = datetime.now().strftime("%Y")
    mes     = datetime.now().strftime("%m")
    carpeta = Path(f"data/{categoria}/{anio}/{mes}")
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{fecha}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"✅ Guardado: {ruta}")


print("📦 Económico...")
save_json("economico", collect_economico())

print("🌿 Ambiental...")
save_json("ambiental", collect_ambiental())

print("🏠 Idealista (precios vivienda)...")
try:
    resultado = collect_idealista()
    save_json("idealista", resultado)
    # Advertir si se acercó al límite mensual pero sin abortar el pipeline
    usadas = resultado.get("peticiones_usadas_este_mes", 0)
    if usadas and usadas >= 80:
        print(f"⚠️  AVISO: {usadas}/100 peticiones Idealista usadas este mes.")
    if "advertencia" in resultado:
        print(f"⚠️  {resultado['advertencia']}")
except Exception as e:
    # Límite alcanzado u otro error — se loguea pero NO se aborta el pipeline
    print(f"⚠️  Idealista saltado: {e}")

print("🏁 Recolección completada.")
"""
    return run_step(
        "job_diario (economico + ambiental + idealista)",
        [PYTHON, "-c", script]
    )


def run_notebook(nb_path: str) -> bool:
    nb = ROOT / nb_path
    if not nb.exists():
        log(f"⚠️  Notebook no encontrado, saltando: {nb_path}")
        return True
    return run_step(
        nb.name,
        [
            PYTHON, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=600",
            "--ExecutePreprocessor.kernel_name=python3",
            str(nb)
        ]
    )


def run_insights() -> bool:
    """Ejecuta run_insights.py si existe."""
    script = ROOT / "run_insights.py"
    if not script.exists():
        log("⚠️  run_insights.py no encontrado, saltando fase insights.")
        return True
    log("── FASE: 05_insights ──")
    return run_step(
        "run_insights.py",
        [PYTHON, str(script)]
    )


def main():
    log("=" * 60)
    log(f"🚀 TRIGGER INICIADO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"📁 ROOT: {ROOT}")
    log(f"🐍 Python: {PYTHON}")
    log("=" * 60)

    # ── PASO 1: Recolección ───────────────────────────────────
    if not run_scheduler_once():
        log("🛑 Fallo en recolección. Abortando pipeline.")
        sys.exit(1)

    # ── PASOS 2–5: Fases de notebooks ────────────────────────
    failed_total = []

    for fase, notebooks in FASES.items():
        log(f"\n── FASE: {fase} ──")
        fase_ok = True

        for nb in notebooks:
            ok = run_notebook(nb)
            if not ok:
                failed_total.append(nb)
                fase_ok = False
                log(f"🛑 Fallo crítico en {nb}. Abortando fase '{fase}' y siguientes.")
                break

        if not fase_ok:
            log(f"⛔ Pipeline detenido en fase '{fase}'.")
            break

    # ── PASO 6: Insights (solo si fases anteriores OK) ───────
    if not failed_total:
        if not run_insights():
            failed_total.append("run_insights.py")

    # ── Resumen ───────────────────────────────────────────────
    log("\n" + "=" * 60)
    if not failed_total:
        log("🎉 PIPELINE COMPLETADO SIN ERRORES")
    else:
        log(f"⚠️  PIPELINE COMPLETADO CON {len(failed_total)} FALLOS:")
        for f in failed_total:
            log(f"   ❌ {f}")
    log(f"📋 Log: {LOG_FILE}")
    log("=" * 60)


if __name__ == "__main__":
    main()
