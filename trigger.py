"""
trigger.py — Pipeline completo TFG Spain's Migratory Flow
Orden: scheduler → 01_exploracion → 02_limpieza → 03_visualizacion
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

VENV_PYTHON = str(ROOT / ".venv" / "bin" / "python")
PYTHON = VENV_PYTHON if Path(VENV_PYTHON).exists() else sys.executable

LOG_DIR = ROOT / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

NOTEBOOKS = [
    # ── FASE 1: Exploración ───────────────────────────────────
    "notebooks/01_exploracion/01_economico.ipynb",
    "notebooks/01_exploracion/01_ambiental.ipynb",
    "notebooks/01_exploracion/01_conectividad.ipynb",
    "notebooks/01_exploracion/01_evr.ipynb",

    # ── FASE 2: Limpieza ──────────────────────────────────────
    "notebooks/02_limpieza/02_ambiental.ipynb",
    "notebooks/02_limpieza/02_economico.ipynb",
    "notebooks/02_limpieza/02_concectividad.ipynb",   # ← typo original del archivo
    "notebooks/02_limpieza/02_evr.ipynb",

    # ── FASE 3: aún no existe, se saltarán ───────────────────
    # "notebooks/03_visualizacion/03_merge_maestro.ipynb",
]

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
    log("── PASO 1: Recolección de datos (job_diario) ──")
    script = """
import sys, os
sys.path.insert(0, os.getcwd())
from collectors.economico import collect_economico
from collectors.ambiental import collect_ambiental
import json
from datetime import datetime
from pathlib import Path

def save_json(categoria, datos):
    fecha = datetime.now().strftime("%d_%m_%Y")
    anio  = datetime.now().strftime("%Y")
    mes   = datetime.now().strftime("%m")
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
print("🏁 Recolección completada.")
"""
    return run_step(
        "job_diario (sin scheduler bloqueante)",
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

def main():
    log("=" * 60)
    log(f"🚀 TRIGGER INICIADO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"📁 ROOT: {ROOT}")
    log(f"🐍 Python: {PYTHON}")
    log("=" * 60)

    # ── PASO 1: Recolección ───────────────────────────────────
    ok = run_scheduler_once()
    if not ok:
        log("🛑 Fallo en recolección. Abortando pipeline.")
        sys.exit(1)

    # ── PASO 2+3: Notebooks en orden ─────────────────────────
    log("\n── PASO 2/3: Ejecutando notebooks ──")
    failed = []
    for nb in NOTEBOOKS:
        ok = run_notebook(nb)
        if not ok:
            failed.append(nb)
            # Fase 1 (exploracion) y Fase 2 (limpieza) son bloqueantes entre sí
            # Si falla un 02_, no tiene sentido ejecutar el 03_
            if "03_visualizacion" not in nb and not ok:
                log(f"🛑 Fallo crítico en {nb}. Abortando resto del pipeline.")
                break

    # ── Resumen ───────────────────────────────────────────────
    log("\n" + "=" * 60)
    if not failed:
        log("🎉 PIPELINE COMPLETADO SIN ERRORES")
    else:
        log(f"⚠️  PIPELINE COMPLETADO CON {len(failed)} FALLOS:")
        for f in failed:
            log(f"   ❌ {f}")
    log(f"📋 Log: {LOG_FILE}")
    log("=" * 60)

if __name__ == "__main__":
    main()