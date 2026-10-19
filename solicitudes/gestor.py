from datetime import datetime

from modelos import DatosEstudiante, Estado, Prioridad, TipoSolicitud, es_valor_de
from prioridad import PoliticaPrioridad
from repositorio import RepositorioJSON


class GestorSolicitudes:
    def __init__(self, repositorio=None, politica_prioridad=None):
        self.repo = repositorio or RepositorioJSON()
        self.politica_prioridad = politica_prioridad or PoliticaPrioridad()

    def registrar_estudiante(self, datos):
        error = datos.validar()
        if error is None and self.repo.buscar_estudiante(datos.legajo) is not None:
            error = "ya existe un estudiante con ese legajo"
        if error is not None:
            print("Error: " + error)
            return False
        self.repo.estudiantes.append({"legajo": datos.legajo, "nombre": datos.nombre.strip(), "email": datos.email})
        self.repo.guardar()
        print("Estudiante registrado: " + datos.legajo + " - " + datos.nombre.strip())
        return True

    def registrar_solicitud(self, datos, datos_estudiante=None):
        """Registra una solicitud. 'datos_estudiante' solo se usa si el legajo no existe."""
        es_estudiante_nuevo = self.repo.buscar_estudiante(datos.legajo) is None
        error = None
        if es_estudiante_nuevo:
            datos_estudiante = datos_estudiante or DatosEstudiante(datos.legajo, "", "")
            error = datos_estudiante.validar()
        if error is None:
            error = datos.validar()
        if error is not None:
            print("Error: " + error)
            return False
        if es_estudiante_nuevo:
            self.repo.estudiantes.append({"legajo": datos.legajo, "nombre": datos_estudiante.nombre.strip(),
                                     "email": datos_estudiante.email})
            print("(Se dio de alta al estudiante " + datos.legajo + ")")
        id_solicitud = self.repo.siguiente_id()
        solicitud = self._crear_solicitud(id_solicitud, datos, self.politica_prioridad.calcular(datos))
        self.repo.solicitudes.append(solicitud)
        self.repo.guardar()
        print("Solicitud #" + str(id_solicitud) + " registrada con prioridad "
              + self._texto_prioridad(solicitud["prioridad"]))
        return True

    def _crear_solicitud(self, id_solicitud, datos, prioridad):
        hoy = self._hoy()
        return {
            "id": id_solicitud,
            "legajo": datos.legajo,
            "tipo": datos.tipo,
            "descripcion": datos.descripcion.strip(),
            "materia": datos.materia.strip(),
            "canal": datos.canal,
            "prioridad": int(prioridad),
            "estado": Estado.PENDIENTE.value,
            "responsable": None,
            "fecha": hoy,
            "historial": [hoy + " creada (pendiente)"],
        }

    def _hoy(self):
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _texto_prioridad(prioridad):
        return Prioridad(prioridad).etiqueta

    def asignar_responsable(self, id_sol, id_resp):
        sol = self.repo.buscar_solicitud(id_sol)
        if sol is None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return False
        r = self.repo.buscar_responsable(id_resp)
        if r is None:
            print("Error: no existe el responsable " + str(id_resp))
            return False
        if not Estado(sol["estado"]).esta_abierta:
            print("Error: la solicitud ya esta cerrada")
            return False
        sol["responsable"] = id_resp
        hoy = self._hoy()
        sol["historial"].append(hoy + " asignada a " + r["nombre"])
        if sol["estado"] == Estado.PENDIENTE:
            sol["estado"] = Estado.EN_PROCESO.value
            sol["historial"].append(hoy + " pendiente -> en_proceso")
        self.repo.guardar()
        print("Solicitud #" + str(id_sol) + " asignada a " + r["nombre"] + " (" + r["area"] + ")")
        return True

    def cambiar_estado(self, id_sol, nuevo):
        sol = self.repo.buscar_solicitud(id_sol)
        if sol is None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return "error"
        ant = sol["estado"]
        if not es_valor_de(Estado, nuevo) or not Estado(ant).puede_pasar_a(Estado(nuevo)):
            print("Error: transicion invalida " + ant + " -> " + nuevo)
            return False
        if nuevo == Estado.EN_PROCESO and sol["responsable"] is None:
            print("Error: no se puede pasar a en_proceso sin responsable asignado")
            return False
        sol["estado"] = nuevo
        hoy = self._hoy()
        sol["historial"].append(hoy + " " + ant + " -> " + nuevo)
        self.repo.guardar()
        print("Solicitud #" + str(id_sol) + ": " + ant + " -> " + nuevo)
        return True

    def buscar(self, estado, tipo, legajo, prio_min):
        l = []
        for s in self.repo.solicitudes:
            if estado != "" and s["estado"] != estado:
                continue
            if tipo != "" and s["tipo"] != tipo:
                continue
            if legajo != "" and s["legajo"] != legajo:
                continue
            if prio_min != 0 and s["prioridad"] < prio_min:
                continue
            l.append(s)
        # ordenar por prioridad desc y luego id
        l.sort(key=lambda s: (-s["prioridad"], s["id"]))
        if len(l) == 0:
            print("No se encontraron solicitudes")
            return l
        print("ID   FECHA       TIPO             PRIORIDAD  ESTADO       LEGAJO  RESPONSABLE")
        for s in l:
            pr = self._texto_prioridad(s["prioridad"])
            resp = "-"
            if s["responsable"] is not None:
                resp = self.repo.buscar_responsable(s["responsable"])["nombre"]
            print(f"{s['id']:<5}{s['fecha']:<12}{s['tipo']:<17}{pr:<11}{s['estado']:<13}{s['legajo']:<8}{resp}")
        print("Total: " + str(len(l)))
        return l

    def ver_detalle(self, id_sol):
        sol = self.repo.buscar_solicitud(id_sol)
        if sol is None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return
        est = self.repo.buscar_estudiante(sol["legajo"])
        print("Solicitud #" + str(sol["id"]) + " - " + sol["tipo"])
        print("  Estudiante: " + est["nombre"] + " (" + est["legajo"] + ", " + est["email"] + ")")
        if sol["materia"] != "":
            print("  Materia: " + sol["materia"])
        print("  Descripcion: " + sol["descripcion"])
        pr = self._texto_prioridad(sol["prioridad"])
        print("  Prioridad: " + pr + " | Estado: " + sol["estado"] + " | Canal: " + sol["canal"])
        print("  Historial:")
        for h in sol["historial"]:
            print("    - " + h)

    def reporte(self):
        print("=== REPORTE DE SOLICITUDES ===")
        print("Total de solicitudes: " + str(len(self.repo.solicitudes)))
        print("Por estado:")
        for est in Estado:
            c = 0
            for s in self.repo.solicitudes:
                if s["estado"] == est:
                    c = c + 1
            print("  " + est.value + ": " + str(c))
        print("Por tipo:")
        for t in TipoSolicitud:
            c = 0
            for s in self.repo.solicitudes:
                if s["tipo"] == t:
                    c = c + 1
            if c > 0:
                print("  " + t.value + ": " + str(c))
        print("Abiertas por prioridad:")
        for p in sorted(Prioridad, reverse=True):
            c = 0
            for s in self.repo.solicitudes:
                if s["prioridad"] == p and Estado(s["estado"]).esta_abierta:
                    c = c + 1
            pr = self._texto_prioridad(p)
            print("  " + pr + ": " + str(c))
        print("Carga por responsable (abiertas):")
        for r in self.repo.responsables:
            c = 0
            for s in self.repo.solicitudes:
                if s["responsable"] == r["id"] and Estado(s["estado"]).esta_abierta:
                    c = c + 1
            print("  " + r["nombre"] + " (" + r["area"] + "): " + str(c))
        cerradas = 0
        for s in self.repo.solicitudes:
            if not Estado(s["estado"]).esta_abierta:
                cerradas = cerradas + 1
        if len(self.repo.solicitudes) > 0:
            print("Porcentaje cerradas: " + str(round(cerradas * 100 / len(self.repo.solicitudes), 1)) + "%")
        else:
            print("Porcentaje cerradas: 0%")

    def listar_responsables(self):
        for r in self.repo.responsables:
            print(str(r["id"]) + ". " + r["nombre"] + " - " + r["area"])
