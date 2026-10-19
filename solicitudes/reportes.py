"""Calculo del reporte de solicitudes.

Antes 'reporte()' calculaba e imprimia a la vez, con cinco bucles casi iguales
(CC 24). Ahora se calculan los datos y la interfaz decide como mostrarlos.
"""
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from modelos import Estado, Prioridad, Responsable, TipoSolicitud


@dataclass(frozen=True)
class Reporte:
    total: int
    por_estado: Dict[Estado, int]
    por_tipo: Dict[TipoSolicitud, int]          # solo tipos con al menos una solicitud
    abiertas_por_prioridad: Dict[Prioridad, int]  # de ALTA a BAJA
    carga_por_responsable: List[Tuple[Responsable, int]]
    porcentaje_cerradas: Optional[float]        # None si no hay solicitudes


def generar_reporte(solicitudes, responsables):
    abiertas = [s for s in solicitudes if s.estado.esta_abierta]
    estados = Counter(s.estado for s in solicitudes)
    tipos = Counter(s.tipo for s in solicitudes)
    prioridades = Counter(s.prioridad for s in abiertas)
    carga = Counter(s.responsable for s in abiertas)
    cerradas = len(solicitudes) - len(abiertas)

    return Reporte(
        total=len(solicitudes),
        por_estado={estado: estados[estado] for estado in Estado},
        por_tipo={tipo: tipos[tipo] for tipo in TipoSolicitud if tipos[tipo] > 0},
        abiertas_por_prioridad={p: prioridades[p] for p in sorted(Prioridad, reverse=True)},
        carga_por_responsable=[(r, carga[r.id]) for r in responsables],
        porcentaje_cerradas=round(cerradas * 100 / len(solicitudes), 1) if solicitudes else None,
    )
