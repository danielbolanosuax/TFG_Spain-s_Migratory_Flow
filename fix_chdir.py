# fix_chdir.py — ejecutar desde el root del proyecto
import json
from pathlib import Path

OLD = 'os.chdir("/workspaces/TFG_Spain-s_Migratory_Flow")'
NEW = '''# ROOT dinámico — funciona en local, CI y cualquier entorno
ROOT = Path.cwd()
while not (ROOT / "requirements.txt").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
os.chdir(ROOT)'''

notebooks = [
    "notebooks/04_merge/04_merge.ipynb",
    "notebooks/03_visualizacion/03_ambiental.ipynb",
    "notebooks/03_visualizacion/03_economico.ipynb",
    "notebooks/03_visualizacion/03_conectividad.ipynb",
    "notebooks/03_visualizacion/03_evr.ipynb",
    "notebooks/05_insights/08_visualizaciones_finales.ipynb",
    "notebooks/05_insights/09_analisis_genero.ipynb",
    "notebooks/05_insights/07_regresion.ipynb",
    "notebooks/05_insights/05_analisis_descriptivo.ipynb",
    "notebooks/05_insights/06_correlacion.ipynb",
    "notebooks/01_exploracion/01_economico.ipynb",
    "notebooks/01_exploracion/01_conectividad.ipynb",
    "notebooks/02_limpieza/02_concectividad.ipynb",
    "notebooks/02_limpieza/02_economico.ipynb",
    "notebooks/02_limpieza/02_evr.ipynb",
]

for nb_path in notebooks:
    path = Path(nb_path)
    nb = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            if 'os.chdir("/workspaces/' in src:
                cell["source"] = [
                    line.replace(OLD, NEW)
                    for line in cell["source"]
                ]
                changed = True
    if changed:
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"✅ Parcheado: {nb_path}")
    else:
        print(f"⚠️  Sin cambios: {nb_path}")

print("\n🎉 Listo.")