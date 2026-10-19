"""Utilidades para ejecutar el sistema como caja negra desde los tests."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MAIN = RAIZ / "solicitudes" / "main.py"
GOLDEN = Path(__file__).resolve().parent / "golden"

_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


def normalizar(texto):
    """Reemplaza las fechas por un marcador para que la comparacion no dependa del dia."""
    return _FECHA.sub("<FECHA>", texto)


def ejecutar(lineas, archivo_datos):
    """Ejecuta main.py alimentando las lineas por stdin y devuelve la salida normalizada."""
    entorno = dict(os.environ, SOLICITUDES_DATA=str(archivo_datos), PYTHONIOENCODING="utf-8")
    comando = [sys.executable, str(MAIN)]
    if os.environ.get("MEDIR_COBERTURA"):
        # permite medir la cobertura tambien dentro del subproceso (ver README)
        comando = [sys.executable, "-m", "coverage", "run", "--parallel-mode", "--branch",
                   f"--source={RAIZ / 'solicitudes'}", f"--data-file={RAIZ / '.coverage'}", str(MAIN)]
    resultado = subprocess.run(
        comando,
        input="\n".join(lineas) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=entorno,
        cwd=str(RAIZ),
        timeout=30,
    )
    return resultado.returncode, normalizar(resultado.stdout), resultado.stderr


def ejecutar_escenario(corridas, archivo_datos):
    """Ejecuta todas las corridas de un escenario sobre el mismo archivo de datos."""
    salidas = []
    for i, lineas in enumerate(corridas, start=1):
        codigo, salida, error = ejecutar(lineas, archivo_datos)
        assert codigo == 0, f"La corrida {i} termino con codigo {codigo}:\n{error}"
        salidas.append(f"##### CORRIDA {i} #####\n{salida}")
    datos = ""
    if Path(archivo_datos).exists():
        contenido = json.loads(Path(archivo_datos).read_text(encoding="utf-8"))
        datos = normalizar(json.dumps(contenido, indent=2, ensure_ascii=False, sort_keys=True))
    return "\n".join(salidas), datos
