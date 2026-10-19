import json
import os
from datetime import datetime

ARCHIVO = os.environ.get("SOLICITUDES_DATA", "datos/solicitudes.json")
contador = 0


class GestorSolicitudes:
    def __init__(self):
        self.estudiantes = []
        self.responsables = []
        self.solicitudes = []
        self.cargar()

    def cargar(self):
        global contador
        try:
            f = open(ARCHIVO, "r", encoding="utf-8")
            d = json.load(f)
            f.close()
            self.estudiantes = d["estudiantes"]
            self.responsables = d["responsables"]
            self.solicitudes = d["solicitudes"]
            contador = d["contador"]
        except:
            # si falla arrancamos de cero
            self.estudiantes = []
            self.responsables = [
                {"id": 1, "nombre": "Laura Gomez", "area": "Alumnado"},
                {"id": 2, "nombre": "Martin Sosa", "area": "Coordinacion"},
                {"id": 3, "nombre": "Paula Diaz", "area": "Bedelia"},
            ]
            self.solicitudes = []
            contador = 0

    def registrar_estudiante(self, legajo, nombre, email):
        error = self._validar_datos_estudiante(legajo, nombre, email)
        if error is None and self.buscar_estudiante(legajo) is not None:
            error = "ya existe un estudiante con ese legajo"
        if error is not None:
            print("Error: " + error)
            return False
        self.estudiantes.append({"legajo": legajo, "nombre": nombre.strip(), "email": email})
        self._guardar()
        print("Estudiante registrado: " + legajo + " - " + nombre.strip())
        return True

    def registrar_solicitud(self, legajo, nombre, email, tipo, descripcion, materia, urgente, canal):
        global contador
        estudiante = self.buscar_estudiante(legajo)
        error = None
        if estudiante is None:
            error = self._validar_datos_estudiante(legajo, nombre, email)
        if error is None:
            error = self._validar_solicitud(tipo, descripcion, materia, canal)
        if error is not None:
            print("Error: " + error)
            return False
        if estudiante is None:
            self.estudiantes.append({"legajo": legajo, "nombre": nombre.strip(), "email": email})
            print("(Se dio de alta al estudiante " + legajo + ")")
        contador = contador + 1
        solicitud = self._crear_solicitud(contador, legajo, tipo, descripcion, materia, canal,
                                          self._calcular_prioridad(tipo, urgente, canal))
        self.solicitudes.append(solicitud)
        self._guardar()
        print("Solicitud #" + str(contador) + " registrada con prioridad "
              + self._texto_prioridad(solicitud["prioridad"]))
        return True

    def _validar_datos_estudiante(self, legajo, nombre, email):
        if not legajo.isdigit() or len(legajo) != 5:
            return "el legajo debe tener 5 digitos"
        if "@" not in email or "." not in email.split("@")[-1]:
            return "email invalido"
        if nombre.strip() == "":
            return "el nombre no puede estar vacio"
        return None

    def _validar_solicitud(self, tipo, descripcion, materia, canal):
        if tipo not in ["certificado", "equivalencia", "cambio_comision", "reclamo_nota", "baja_materia"]:
            return "tipo de solicitud invalido"
        if len(descripcion.strip()) < 10:
            return "la descripcion debe tener al menos 10 caracteres"
        if canal not in ("web", "presencial", "email"):
            return "canal invalido"
        if materia.strip() == "" and tipo in ("equivalencia", "reclamo_nota", "baja_materia"):
            return "este tipo de solicitud requiere indicar la materia"
        return None

    def _calcular_prioridad(self, tipo, urgente, canal):
        if tipo == "reclamo_nota":
            return 3 if urgente else 2
        if tipo == "equivalencia":
            return 2
        if tipo == "certificado":
            return 2 if urgente else 1
        if tipo == "baja_materia":
            return 3
        if tipo == "cambio_comision":
            return 2 if canal == "presencial" else 1
        return 0

    def _crear_solicitud(self, id_solicitud, legajo, tipo, descripcion, materia, canal, prioridad):
        hoy = self._hoy()
        return {
            "id": id_solicitud,
            "legajo": legajo,
            "tipo": tipo,
            "descripcion": descripcion.strip(),
            "materia": materia.strip(),
            "canal": canal,
            "prioridad": prioridad,
            "estado": "pendiente",
            "responsable": None,
            "fecha": hoy,
            "historial": [hoy + " creada (pendiente)"],
        }

    def _guardar(self):
        with open(ARCHIVO, "w", encoding="utf-8") as archivo:
            json.dump({"estudiantes": self.estudiantes, "responsables": self.responsables,
                       "solicitudes": self.solicitudes, "contador": contador},
                      archivo, indent=2, ensure_ascii=False)

    def _hoy(self):
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _texto_prioridad(prioridad):
        if prioridad == 3:
            return "ALTA"
        if prioridad == 2:
            return "MEDIA"
        return "BAJA"

    def buscar_estudiante(self, legajo):
        for estudiante in self.estudiantes:
            if estudiante["legajo"] == legajo:
                return estudiante
        return None

    def buscar_solicitud(self, id_solicitud):
        for solicitud in self.solicitudes:
            if solicitud["id"] == id_solicitud:
                return solicitud
        return None

    def buscar_responsable(self, id_responsable):
        for responsable in self.responsables:
            if responsable["id"] == id_responsable:
                return responsable
        return None

    def asignar_responsable(self, id_sol, id_resp):
        sol = self.buscar_solicitud(id_sol)
        if sol is None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return False
        r = self.buscar_responsable(id_resp)
        if r is None:
            print("Error: no existe el responsable " + str(id_resp))
            return False
        if sol["estado"] == "resuelta" or sol["estado"] == "rechazada":
            print("Error: la solicitud ya esta cerrada")
            return False
        sol["responsable"] = id_resp
        hoy = self._hoy()
        sol["historial"].append(hoy + " asignada a " + r["nombre"])
        if sol["estado"] == "pendiente":
            sol["estado"] = "en_proceso"
            sol["historial"].append(hoy + " pendiente -> en_proceso")
        self._guardar()
        print("Solicitud #" + str(id_sol) + " asignada a " + r["nombre"] + " (" + r["area"] + ")")
        return True

    def cambiar_estado(self, id_sol, nuevo):
        sol = self.buscar_solicitud(id_sol)
        if sol is None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return "error"
        ant = sol["estado"]
        ok = False
        if ant == "pendiente":
            if nuevo == "en_proceso":
                if sol["responsable"] is None:
                    print("Error: no se puede pasar a en_proceso sin responsable asignado")
                    return False
                ok = True
            elif nuevo == "rechazada":
                ok = True
        elif ant == "en_proceso":
            if nuevo == "resuelta" or nuevo == "rechazada":
                ok = True
        if not ok:
            print("Error: transicion invalida " + ant + " -> " + nuevo)
            return False
        sol["estado"] = nuevo
        hoy = self._hoy()
        sol["historial"].append(hoy + " " + ant + " -> " + nuevo)
        self._guardar()
        print("Solicitud #" + str(id_sol) + ": " + ant + " -> " + nuevo)
        return True

    def buscar(self, estado, tipo, legajo, prio_min):
        l = []
        for s in self.solicitudes:
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
                resp = self.buscar_responsable(s["responsable"])["nombre"]
            print(f"{s['id']:<5}{s['fecha']:<12}{s['tipo']:<17}{pr:<11}{s['estado']:<13}{s['legajo']:<8}{resp}")
        print("Total: " + str(len(l)))
        return l

    def ver_detalle(self, id_sol):
        sol = self.buscar_solicitud(id_sol)
        if sol is None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return
        est = self.buscar_estudiante(sol["legajo"])
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
        print("Total de solicitudes: " + str(len(self.solicitudes)))
        print("Por estado:")
        for est in ["pendiente", "en_proceso", "resuelta", "rechazada"]:
            c = 0
            for s in self.solicitudes:
                if s["estado"] == est:
                    c = c + 1
            print("  " + est + ": " + str(c))
        print("Por tipo:")
        for t in ["certificado", "equivalencia", "cambio_comision", "reclamo_nota", "baja_materia"]:
            c = 0
            for s in self.solicitudes:
                if s["tipo"] == t:
                    c = c + 1
            if c > 0:
                print("  " + t + ": " + str(c))
        print("Abiertas por prioridad:")
        for p in [3, 2, 1]:
            c = 0
            for s in self.solicitudes:
                if s["prioridad"] == p and (s["estado"] == "pendiente" or s["estado"] == "en_proceso"):
                    c = c + 1
            pr = self._texto_prioridad(p)
            print("  " + pr + ": " + str(c))
        print("Carga por responsable (abiertas):")
        for r in self.responsables:
            c = 0
            for s in self.solicitudes:
                if s["responsable"] == r["id"] and (s["estado"] == "pendiente" or s["estado"] == "en_proceso"):
                    c = c + 1
            print("  " + r["nombre"] + " (" + r["area"] + "): " + str(c))
        cerradas = 0
        for s in self.solicitudes:
            if s["estado"] == "resuelta" or s["estado"] == "rechazada":
                cerradas = cerradas + 1
        if len(self.solicitudes) > 0:
            print("Porcentaje cerradas: " + str(round(cerradas * 100 / len(self.solicitudes), 1)) + "%")
        else:
            print("Porcentaje cerradas: 0%")

    def listar_responsables(self):
        for r in self.responsables:
            print(str(r["id"]) + ". " + r["nombre"] + " - " + r["area"])
