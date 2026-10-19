# Sistema de Gestión de Solicitudes Académicas

Prototipo de consola en Python para registrar solicitudes de estudiantes
(certificados, equivalencias, cambios de comisión, reclamos de nota y bajas de materia),
clasificarlas por tipo, prioridad y estado, asignarlas a un responsable y obtener reportes simples.

## Uso

```bash
python solicitudes/main.py
```

Los datos se guardan en `datos/solicitudes.json` (se puede cambiar con la variable de entorno `SOLICITUDES_DATA`).
