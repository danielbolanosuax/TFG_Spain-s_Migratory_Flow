"""
trigger.py — Pipeline completo TFG Spain's Migratory Flow
Orden: recolección → 01_exploracion → 02_limpieza → 03_visualizacion → 04_merge → 05_insights
"""

import os
import sys
import json
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


# ─────────────────────────────────────────────────────────────
# FASES DE NOTEBOOKS
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─────────────────────────────────────────────────────────────
# RUNNER DE COMANDOS
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# PASO 1: RECOLECCIÓN DE DATOS
# Incluye: economico, ambiental, conectividad, evr, idealista
# ─────────────────────────────────────────────────────────────
def save_json(categoria: str, datos: dict):
    """Guarda el JSON de un collector en data/{categoria}/{año}/{mes}/{fecha}.json"""
    fecha   = datetime.now().strftime("%d_%m_%Y")
    anio    = datetime.now().strftime("%Y")
    mes     = datetime.now().strftime("%m")
    carpeta = ROOT / "data" / categoria / anio / mes
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{fecha}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    log(f"💾 Guardado: {ruta.relative_to(ROOT)}")


def run_coleccion() -> bool:
    """
    Ejecuta todos los collectors directamente en el mismo proceso.
    Ventaja: más rápido, logs visibles, errores claros.
    """
    log("── PASO 1: Recolección de datos ──")

    sys.path.insert(0, str(ROOT))

    collectors = [
        ("economico",   "collectors.economico",   "collect_economico",  "📈"),
        ("ambiental",   "collectors.ambiental",   "collect_ambiental",  "🌿"),
        ("conectividad","collectors.conectividad", "collect_conectividad","🔗"),
        ("evr",         "collectors.evr",          "collect",            "🧭"),
        ("idealista",   "collectors.idealista",    "collect_idealista",  "🏠"),
    ]

    fallos = []

    for categoria, modulo, funcion, emoji in collectors:
        log(f"{emoji} Recolectando {categoria}...")
        try:
            import importlib
            mod = importlib.import_module(modulo)

            # Recarga el módulo para evitar caché en ejecuciones repetidas
            importlib.reload(mod)

            fn = getattr(mod, funcion)
            datos = fn()
            save_json(categoria, datos)
            log(f"✅ {categoria} — OK")

        except Exception as e:
            log(f"❌ {categoria} — ERROR: {e}")
            fallos.append(categoria)

    if fallos:
        log(f"⚠️  Collectors con fallos: {fallos}")
        # No abortamos el pipeline por fallos en collectors secundarios,
        # pero sí si falla economico o evr (pilares del análisis)
        criticos = [f for f in fallos if f in ("economico", "evr")]
        if criticos:
            log(f"🛑 Fallo en collectors críticos {criticos}. Abortando.")
            return False
        log("ℹ️  Fallos en collectors no críticos — el pipeline continúa.")

    return True


# ─────────────────────────────────────────────────────────────
# RUNNER DE NOTEBOOKS
# ─────────────────────────────────────────────────────────────
def run_notebook(nb_path: str) -> bool:
    nb = ROOT / nb_path
    if not nb.exists():
        log(f"⚠️  Notebook no encontrado, saltando: {nb_path}")
        return True   # No bloqueamos el pipeline por notebooks opcionales
    return run_step(
        nb.name,
        [
            PYTHON, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=600",
            "--ExecutePreprocessor.kernel_name=python3",
            str(nb),
        ]
    )


# ─────────────────────────────────────────────────────────────
# FASE INSIGHTS
# ─────────────────────────────────────────────────────────────
def run_insights() -> bool:
    script = ROOT / "run_insights.py"
    if not script.exists():
        log("⚠️  run_insights.py no encontrado, saltando fase insights.")
        return True
    log("── FASE: 05_insights ──")
    return run_step("run_insights.py", [PYTHON, str(script)])


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log(f"🚀 TRIGGER INICIADO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"📁 ROOT: {ROOT}")
    log(f"🐍 Python: {PYTHON}")
    log("=" * 60)

    # ── PASO 1: Recolección ───────────────────────────────────
    if not run_coleccion():
        log("🛑 Fallo crítico en recolección. Abortando pipeline.")
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
                log(f"🛑 Fallo en {nb}. Abortando fase '{fase}' y siguientes.")
                break

        if not fase_ok:
            log(f"⛔ Pipeline detenido en fase '{fase}'.")
            break

    # ── PASO 6: Insights (solo si fases anteriores OK) ───────
    if not failed_total:
        if not run_insights():
            failed_total.append("run_insights.py")

    # ── Resumen final ─────────────────────────────────────────
    log("\n" + "=" * 60)
    if not failed_total:
        log("🎉 PIPELINE COMPLETADO SIN ERRORES")
    else:
        log(f"⚠️  PIPELINE COMPLETADO CON {len(failed_total)} FALLOS:")
        for f in failed_total:
            log(f"   ❌ {f}")
    log(f"📋 Log completo: {LOG_FILE}")
    log("=" * 60)


if __name__ == "__main__":
    main()