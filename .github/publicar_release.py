#!/usr/bin/env python3
"""Publica un paquete de actualización como «release» de GitHub (lo usa el distribuidor, no el cliente).

    python scripts/publicar_release.py PROYECTO_ALLAS_actualizacion_1.21.zip [--repo usuario/repositorio] [--simular]

Necesita la herramienta «gh» de GitHub con la sesión iniciada (gh auth login). Crea la release vX.Y con el paquete firmado
adjunto y, como texto, la entrada de esa versión del CHANGELOG que va dentro del propio paquete. Si la release ya existe,
no hace nada (para reemplazar el archivo, bórrela antes en GitHub). El repositorio debe ser PÚBLICO."""
import argparse
import io
import re
import subprocess
import sys
import zipfile

REPO_DEFECTO = "locometopa/proyecto-allas-versiones"


def notas_de(zip_ruta, version):
    with zipfile.ZipFile(zip_ruta) as z:
        txt = z.read("programa/CHANGELOG.md").decode("utf-8", "replace")
    m = re.search(r"^## " + re.escape(version) + r"\b.*?$(.*?)(?=^## |\Z)", txt, re.S | re.M)
    return (m.group(1).strip() if m else "") or f"Versión {version}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paquete")
    ap.add_argument("--repo", default=REPO_DEFECTO)
    ap.add_argument("--simular", action="store_true", help="solo muestra lo que publicaría")
    a = ap.parse_args()
    m = re.search(r"actualizaci[oó]n_v?(\d+(?:\.\d+)+)\.zip$", a.paquete, re.I)
    if not m:
        sys.exit("El archivo debe llamarse PROYECTO_ALLAS_actualizacion_X.Y.zip")
    v = m.group(1)
    notas = notas_de(a.paquete, v)
    print(f"Release v{v} en {a.repo}\n---\n{notas}\n---")
    if a.simular:
        return
    r = subprocess.run(["gh", "release", "view", f"v{v}", "--repo", a.repo], capture_output=True)
    if r.returncode == 0:
        sys.exit(f"La release v{v} ya existe; no se ha cambiado nada.")
    subprocess.run(["gh", "release", "create", f"v{v}", a.paquete, "--repo", a.repo, "--title", f"Versión {v}", "--notes", notas],
                   check=True)
    print("Publicada.")


if __name__ == "__main__":
    main()
