"""Genera los archivos golden a partir de la version ACTUAL del sistema.

Se ejecuto una unica vez sobre la version inicial (tag estado-inicial).
No volver a ejecutarlo despues de refactorizar: el objetivo es comparar contra
el comportamiento original.

Uso:  python tests/generar_golden.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from escenarios import ESCENARIOS  # noqa: E402
from utils import GOLDEN, ejecutar_escenario  # noqa: E402


def main():
    GOLDEN.mkdir(exist_ok=True)
    for nombre, corridas in ESCENARIOS.items():
        with tempfile.TemporaryDirectory() as carpeta:
            salida, datos = ejecutar_escenario(corridas, Path(carpeta) / "datos.json")
        (GOLDEN / f"{nombre}.salida.txt").write_text(salida, encoding="utf-8")
        (GOLDEN / f"{nombre}.datos.json").write_text(datos, encoding="utf-8")
        print(f"golden generado: {nombre}")


if __name__ == "__main__":
    main()
