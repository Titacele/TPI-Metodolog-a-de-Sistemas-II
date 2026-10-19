"""Interfaz de consola.

Es la unica parte del sistema que lee del teclado e imprime. Traduce las
excepciones de negocio en mensajes 'Error: ...' (antes cada metodo del gestor
imprimia por su cuenta, CS-11). Las funciones de entrada/salida se inyectan
para poder probar la interfaz sin una terminal real.
"""
from errores import ErrorDeNegocio
from modelos import DatosEstudiante, DatosSolicitud, FiltroSolicitudes, TipoSolicitud

ENCABEZADO_LISTADO = "ID   FECHA       TIPO             PRIORIDAD  ESTADO       LEGAJO  RESPONSABLE"


class EntradaInvalidaError(ErrorDeNegocio):
    """El usuario tipeo algo que no se puede interpretar (por ejemplo, un id no numerico)."""


class Consola:
    def __init__(self, servicio, leer=input, escribir=print):
        self._servicio = servicio
        self._leer = leer
        self._escribir = escribir
        self._opciones = {
            "1": ("Registrar estudiante", self._registrar_estudiante),
            "2": ("Registrar solicitud", self._registrar_solicitud),
            "3": ("Asignar responsable", self._asignar_responsable),
            "4": ("Cambiar estado", self._cambiar_estado),
            "5": ("Buscar / filtrar solicitudes", self._buscar),
            "6": ("Ver detalle de solicitud", self._ver_detalle),
            "7": ("Reporte", self._reporte),
        }

    # ------------------------------------------------------------ bucle principal
    def ejecutar(self):
        while True:
            self._mostrar_menu()
            opcion = self._leer("Opcion: ").strip()
            if opcion == "0":
                self._escribir("Hasta luego")
                return
            if opcion not in self._opciones:
                self._escribir("Opcion invalida")
                continue
            _, accion = self._opciones[opcion]
            try:
                accion()
            except ErrorDeNegocio as error:
                self._escribir(f"Error: {error}")

    def _mostrar_menu(self):
        self._escribir("")
        self._escribir("==== SISTEMA DE SOLICITUDES ACADEMICAS ====")
        for clave, (titulo, _) in self._opciones.items():
            self._escribir(f"{clave}. {titulo}")
        self._escribir("0. Salir")

    # ------------------------------------------------------------------ acciones
    def _registrar_estudiante(self):
        datos = DatosEstudiante(
            legajo=self._leer("Legajo: ").strip(),
            nombre=self._leer("Nombre: "),
            email=self._leer("Email: ").strip(),
        )
        estudiante = self._servicio.registrar_estudiante(datos)
        self._escribir(f"Estudiante registrado: {estudiante.legajo} - {estudiante.nombre}")

    def _registrar_solicitud(self):
        legajo = self._leer("Legajo: ").strip()
        datos_estudiante = None
        if not self._servicio.existe_estudiante(legajo):
            self._escribir("Estudiante nuevo, complete sus datos")
            datos_estudiante = DatosEstudiante(legajo, self._leer("Nombre: "),
                                               self._leer("Email: ").strip())
        self._escribir("Tipos: " + ", ".join(TipoSolicitud.valores()))
        datos = DatosSolicitud(
            legajo=legajo,
            tipo=self._leer("Tipo: ").strip(),
            descripcion=self._leer("Descripcion: "),
            materia=self._leer("Materia (opcional): "),
            urgente=self._leer("Urgente (s/n): ").strip().lower() == "s",
            canal=self._leer("Canal (web/presencial/email): ").strip(),
        )
        resultado = self._servicio.registrar_solicitud(datos, datos_estudiante)
        if resultado.estudiante_dado_de_alta:
            self._escribir(f"(Se dio de alta al estudiante {legajo})")
        solicitud = resultado.solicitud
        self._escribir(f"Solicitud #{solicitud.id} registrada con prioridad {solicitud.prioridad.etiqueta}")

    def _asignar_responsable(self):
        id_solicitud = self._leer_entero("ID solicitud: ", "ID invalido")
        for responsable in self._servicio.listar_responsables():
            self._escribir(f"{responsable.id}. {responsable.nombre} - {responsable.area}")
        id_responsable = self._leer_entero("ID responsable: ", "ID invalido")
        solicitud, responsable = self._servicio.asignar_responsable(id_solicitud, id_responsable)
        self._escribir(f"Solicitud #{solicitud.id} asignada a {responsable.nombre} ({responsable.area})")

    def _cambiar_estado(self):
        id_solicitud = self._leer_entero("ID solicitud: ", "ID invalido")
        nuevo = self._leer("Nuevo estado (en_proceso/resuelta/rechazada): ").strip()
        anterior = self._servicio.cambiar_estado(id_solicitud, nuevo)
        self._escribir(f"Solicitud #{id_solicitud}: {anterior.value} -> {nuevo}")

    def _buscar(self):
        estado = self._leer("Estado (enter = todos): ").strip()
        tipo = self._leer("Tipo (enter = todos): ").strip()
        legajo = self._leer("Legajo (enter = todos): ").strip()
        prioridad = self._leer("Prioridad minima 1-3 (enter = todas): ").strip()
        prioridad_minima = self._a_entero(prioridad, "prioridad invalida") if prioridad else 0
        encontradas = self._servicio.buscar(FiltroSolicitudes(estado, tipo, legajo, prioridad_minima))
        self._mostrar_listado(encontradas)

    def _ver_detalle(self):
        solicitud, estudiante = self._servicio.obtener_detalle(
            self._leer_entero("ID solicitud: ", "ID invalido"))
        self._escribir(f"Solicitud #{solicitud.id} - {solicitud.tipo.value}")
        self._escribir(f"  Estudiante: {estudiante.nombre} ({estudiante.legajo}, {estudiante.email})")
        if solicitud.materia:
            self._escribir(f"  Materia: {solicitud.materia}")
        self._escribir(f"  Descripcion: {solicitud.descripcion}")
        self._escribir(f"  Prioridad: {solicitud.prioridad.etiqueta} | Estado: {solicitud.estado.value}"
                       f" | Canal: {solicitud.canal.value}")
        self._escribir("  Historial:")
        for evento in solicitud.historial:
            self._escribir(f"    - {evento}")

    def _reporte(self):
        reporte = self._servicio.generar_reporte()
        self._escribir("=== REPORTE DE SOLICITUDES ===")
        self._escribir(f"Total de solicitudes: {reporte.total}")
        self._escribir("Por estado:")
        for estado, cantidad in reporte.por_estado.items():
            self._escribir(f"  {estado.value}: {cantidad}")
        self._escribir("Por tipo:")
        for tipo, cantidad in reporte.por_tipo.items():
            self._escribir(f"  {tipo.value}: {cantidad}")
        self._escribir("Abiertas por prioridad:")
        for prioridad, cantidad in reporte.abiertas_por_prioridad.items():
            self._escribir(f"  {prioridad.etiqueta}: {cantidad}")
        self._escribir("Carga por responsable (abiertas):")
        for responsable, cantidad in reporte.carga_por_responsable:
            self._escribir(f"  {responsable.nombre} ({responsable.area}): {cantidad}")
        porcentaje = "0" if reporte.porcentaje_cerradas is None else str(reporte.porcentaje_cerradas)
        self._escribir(f"Porcentaje cerradas: {porcentaje}%")

    # ----------------------------------------------------------------- auxiliares
    def _mostrar_listado(self, solicitudes):
        if not solicitudes:
            self._escribir("No se encontraron solicitudes")
            return
        self._escribir(ENCABEZADO_LISTADO)
        for s in solicitudes:
            self._escribir(f"{s.id:<5}{s.fecha:<12}{s.tipo.value:<17}{s.prioridad.etiqueta:<11}"
                           f"{s.estado.value:<13}{s.legajo:<8}{self._nombre_responsable(s)}")
        self._escribir(f"Total: {len(solicitudes)}")

    def _nombre_responsable(self, solicitud):
        if solicitud.responsable is None:
            return "-"
        return self._servicio.obtener_responsable(solicitud.responsable).nombre

    def _leer_entero(self, mensaje, error):
        return self._a_entero(self._leer(mensaje), error)

    @staticmethod
    def _a_entero(texto, error):
        try:
            return int(texto)
        except ValueError as excepcion:
            raise EntradaInvalidaError(error) from excepcion
