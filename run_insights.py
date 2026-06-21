# run_insights.py
"""
Ejecuta secuencialmente todos los notebooks de 05_insights
usando papermill. Se lanza después del trigger + merge completo.
"""

import logging
from pathlib import Path
from datetime import datetime

import papermill as pm

# ─────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────
LOG_DIR = Path("output") / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# RUTAS Y NOTEBOOKS
# ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
NB_DIR = ROOT / "notebooks" / "05_insights"
OUT_DIR = ROOT / "output" / "executed_notebooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOTEBOOKS = [
    "05_analisis_descriptivo.ipynb",
    "06_correlacion.ipynb",
    "07_regresion.ipynb",
    "08_visualizaciones_finales.ipynb",
    "09_analisis_genero.ipynb",
]

# ─────────────────────────────────────────────────────────────
# EJECUCIÓN
# ─────────────────────────────────────────────────────────────
def run_all():
    for nb in NOTEBOOKS:
        nb_in = NB_DIR / nb
        nb_out = OUT_DIR / nb.replace(".ipynb", "_executed.ipynb")

        if not nb_in.exists():
            log.warning(f"⚠️  Notebook no encontrado, se omite: {nb_in}")
            continue

        log.info(f"▶ Ejecutando: {nb}")
        try:
            pm.execute_notebook(
                input_path=str(nb_in),
                output_path=str(nb_out),
                kernel_name="python3",
                cwd=str(ROOT),       # working dir = raíz del repo
                progress_bar=False,
            )
            log.info(f"✅ Completado: {nb}")
        except Exception as e:
            log.error(f"❌ Error en {nb}: {e}")
            # Si falla uno, detenemos el pipeline para no generar insights inconsistentes
            raise

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 50)
    log.info("🚀 run_insights.py — inicio")
    log.info("=" * 50)
    run_all()
    log.info("🏁 Todos los notebooks de insights completados")
    log.info(f"📋 Log completo: {LOG_FILE}")