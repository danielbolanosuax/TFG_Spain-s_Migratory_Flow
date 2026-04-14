# run_insights.py
"""
Ejecuta secuencialmente todos los notebooks de 05_insights
usando papermill. Se lanza después del trigger + merge.
"""
import papermill as pm
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"output/logs/insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

ROOT     = Path(__file__).parent
NB_DIR   = ROOT / "notebooks" / "05_insights"
OUT_DIR  = ROOT / "output" / "executed_notebooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOTEBOOKS = [
    "05_analisis_descriptivo.ipynb",
    "06_correlacion.ipynb",
    "07_regresion.ipynb",
    "08_visualizaciones_finales.ipynb",
    "09_analisis_genero.ipynb",
]

def run_all():
    for nb in NOTEBOOKS:
        nb_in  = NB_DIR / nb
        nb_out = OUT_DIR / nb.replace(".ipynb", "_executed.ipynb")

        log.info(f"▶ Ejecutando: {nb}")
        try:
            pm.execute_notebook(
                input_path=str(nb_in),
                output_path=str(nb_out),
                kernel_name="python3",
                cwd=str(ROOT),          # ← working dir = raíz del repo
                progress_bar=False,
            )
            log.info(f"✅ Completado: {nb}")
        except Exception as e:
            log.error(f"❌ Error en {nb}: {e}")
            raise  # Si falla uno, para el pipeline

if __name__ == "__main__":
    log.info("=" * 50)
    log.info("🚀 run_insights.py — inicio")
    log.info("=" * 50)
    run_all()
    log.info("🏁 Todos los notebooks de insights completados")