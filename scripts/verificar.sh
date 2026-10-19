#!/usr/bin/env bash
# Corre todas las pruebas, mide cobertura de ramas y metricas de calidad.
# Deja los resultados en docs/evidencias/. Uso: bash scripts/verificar.sh
set -euo pipefail
cd "$(dirname "$0")/.."
EV=docs/evidencias
mkdir -p "$EV"

echo "== Pruebas ==" 
python -m pytest -v -p no:cacheprovider | tee "$EV/pruebas-resultado.txt"

echo "== Cobertura de ramas (incluye las corridas del golden master) =="
rm -f .coverage .coverage.*
MEDIR_COBERTURA=1 python -m coverage run --rcfile=.coveragerc --parallel-mode --branch \
  -m pytest -q -p no:cacheprovider > /dev/null
python -m coverage combine -q
python -m coverage report -m --include="solicitudes/*" | tee "$EV/cobertura.txt"
rm -f .coverage .coverage.*

echo "== Metricas =="
{
  echo "# Metricas version refactorizada"
  echo; echo "## radon cc -s -a (complejidad ciclomatica)"; radon cc -s -a solicitudes
  echo; echo "## radon mi -s (indice de mantenibilidad)"; radon mi -s solicitudes
  echo; echo "## pylint (config en .pylintrc)"; pylint solicitudes 2>&1 | tail -3 || true
  echo; echo "## flake8 --max-line-length=110"; flake8 --max-line-length=110 --count solicitudes || true
} | tee "$EV/metricas-final.txt"
