# Sistema de Gestión de Solicitudes Académicas

**TPI – Metodología de Sistemas II · Tecnicatura Universitaria en Programación a Distancia (UTN)**
Integrantes: María Celeste Reinaudo · [Nombre completo] Rivas

Prototipo de consola en Python para registrar solicitudes de estudiantes, clasificarlas por tipo,
prioridad y estado, asignarlas a un responsable y obtener reportes. El objetivo del trabajo no es
agregar funcionalidad sino **mejorar la calidad interna** del sistema: diagnosticar deuda técnica,
aplicar SOLID y Clean Code, refactorizar de forma segura y revisar el código con criterios profesionales.

## Funcionalidades

1. Registrar estudiante (legajo de 5 dígitos, nombre y email validados)
2. Registrar solicitud: certificado, equivalencia, cambio de comisión, reclamo de nota o baja de materia. La prioridad (ALTA/MEDIA/BAJA) se calcula sola según el tipo, la urgencia y el canal.
3. Asignar responsable (la solicitud pasa a *en proceso*)
4. Cambiar estado: pendiente → en proceso → resuelta / rechazada
5. Buscar y filtrar por estado, tipo, legajo y prioridad mínima
6. Ver detalle con historial de cambios
7. Reporte: totales por estado y tipo, abiertas por prioridad, carga por responsable y % de cerradas

Entidades: Estudiante, Solicitud, Responsable (con área) y Estado. Datos sintéticos, sin personas reales.

## Tecnologías

- Python 3.10 o superior, sin dependencias para ejecutar
- Persistencia en archivo JSON
- pytest + coverage (pruebas), radon, pylint y flake8 (métricas de calidad)

## Instalación y uso

```bash
git clone <url-del-repositorio>
cd <carpeta>
python solicitudes/main.py
```

Los datos se guardan en `datos/solicitudes.json` (incluye datos de ejemplo). Para usar otro archivo:
`SOLICITUDES_DATA=otra/ruta.json python solicitudes/main.py`.

### Pruebas y métricas

```bash
pip install -r requirements-dev.txt
python -m pytest              # 70 pruebas
bash scripts/verificar.sh     # pruebas + cobertura de ramas + métricas -> docs/evidencias/
```

## Versión inicial y versión refactorizada

| Tag | Contenido |
|---|---|
| `estado-inicial` | Sistema base con problemas de diseño (una clase de 325 líneas) |
| `etapa-diagnostico` | Diagnóstico de calidad y 16 code smells |
| `etapa-refactoring` | Refactorings R1–R6 aplicados |
| `etapa-pruebas` | Pruebas unitarias, cobertura y evidencias |
| `etapa-docs` | Documentación completa |
| `estado-refactorizado` | Estado final del código |

```bash
git checkout estado-inicial         # ver la versión original
git checkout estado-refactorizado   # ver la versión final
git diff estado-inicial estado-refactorizado -- solicitudes/
```

## Estructura

```
solicitudes/
  main.py          punto de entrada (arma las dependencias)
  consola.py       interfaz de usuario
  servicio.py      casos de uso
  modelos.py       enums, entidades y objetos de datos
  prioridad.py     política de prioridad (una regla por tipo)
  reportes.py      cálculo del reporte
  repositorio.py   persistencia (abstracción, memoria y JSON)
  errores.py       excepciones del dominio
tests/             golden master + pruebas unitarias
docs/              diagnóstico, SOLID, refactorings, pruebas, code review, uso de IA, evidencias
scripts/           verificar.sh
```

## Resultados

| Métrica | Inicial | Final |
|---|---|---|
| Complejidad ciclomática promedio | 11,3 | 2,1 |
| Complejidad máxima por función | 28 | 7 |
| pylint | 8,66 | 10,00 |
| Avisos flake8 | 17 | 0 |
| Pruebas automatizadas | 0 | 70 (99 % cobertura de ramas) |


