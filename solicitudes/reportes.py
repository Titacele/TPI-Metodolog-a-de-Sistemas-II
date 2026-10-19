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
    return Reporte(
        total=len(solicitudes),
        por_estado=_contar_por(solicitudes, "estado", Estado),
        por_tipo=_sin_ceros(_contar_por(solicitudes, "tipo", TipoSolicitud)),
        abiertas_por_prioridad=_contar_por(abiertas, "prioridad", sorted(Prioridad, reverse=True)),
        carga_por_responsable=_carga_por_responsable(abiertas, responsables),
        porcentaje_cerradas=_porcentaje(len(solicitudes) - len(abiertas), len(solicitudes)),
    )


def _contar_por(solicitudes, atributo, valores):
    """Cuenta las solicitudes por cada valor posible del atributo, respetando el orden dado."""
    conteo = Counter(getattr(s, atributo) for s in solicitudes)
    return {valor: conteo[valor] for valor in valores}


def _sin_ceros(conteo):
    return {clave: cantidad for clave, cantidad in conteo.items() if cantidad > 0}


def _carga_por_responsable(abiertas, responsables):
    conteo = Counter(s.responsable for s in abiertas)
    return [(responsable, conteo[responsable.id]) for responsable in responsables]


def _porcentaje(parte, total):
    return round(parte * 100 / total, 1) if total else None
