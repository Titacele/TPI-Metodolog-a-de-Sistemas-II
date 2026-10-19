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
        # validar legajo
        if not legajo.isdigit() or len(legajo) != 5:
            print("Error: el legajo debe tener 5 digitos")
            return False
        # validar email
        if "@" not in email or "." not in email.split("@")[-1]:
            print("Error: email invalido")
            return False
        if nombre.strip() == "":
            print("Error: el nombre no puede estar vacio")
            return False
        for e in self.estudiantes:
            if e["legajo"] == legajo:
                print("Error: ya existe un estudiante con ese legajo")
                return False
        self.estudiantes.append({"legajo": legajo, "nombre": nombre.strip(), "email": email})
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"estudiantes": self.estudiantes, "responsables": self.responsables,
                   "solicitudes": self.solicitudes, "contador": contador}, f, indent=2, ensure_ascii=False)
        f.close()
        print("Estudiante registrado: " + legajo + " - " + nombre.strip())
        return True

    def registrar_solicitud(self, legajo, nombre, email, tipo, descripcion, materia, urgente, canal):
        global contador
        # buscar estudiante, si no existe lo damos de alta
        est = None
        for e in self.estudiantes:
            if e["legajo"] == legajo:
                est = e
        if est == None:
            if not legajo.isdigit() or len(legajo) != 5:
                print("Error: el legajo debe tener 5 digitos")
                return False
            if "@" not in email or "." not in email.split("@")[-1]:
                print("Error: email invalido")
                return False
            if nombre.strip() == "":
                print("Error: el nombre no puede estar vacio")
                return False
            est = {"legajo": legajo, "nombre": nombre.strip(), "email": email}
            self.estudiantes.append(est)
            print("(Se dio de alta al estudiante " + legajo + ")")
        # validar tipo
        if tipo not in ["certificado", "equivalencia", "cambio_comision", "reclamo_nota", "baja_materia"]:
            print("Error: tipo de solicitud invalido")
            return False
        if len(descripcion.strip()) < 10:
            print("Error: la descripcion debe tener al menos 10 caracteres")
            return False
        if canal != "web" and canal != "presencial" and canal != "email":
            print("Error: canal invalido")
            return False
        # calcular prioridad
        p = 0
        if tipo == "reclamo_nota":
            if urgente:
                p = 3
            else:
                p = 2
        elif tipo == "equivalencia":
            p = 2
        elif tipo == "certificado":
            if urgente:
                p = 2
            else:
                p = 1
        elif tipo == "baja_materia":
            p = 3
        elif tipo == "cambio_comision":
            if canal == "presencial":
                p = 2
            else:
                p = 1
        if materia.strip() == "" and (tipo == "equivalencia" or tipo == "reclamo_nota" or tipo == "baja_materia"):
            print("Error: este tipo de solicitud requiere indicar la materia")
            return False
        contador = contador + 1
        hoy = datetime.now().strftime("%Y-%m-%d")
        s = {
            "id": contador,
            "legajo": legajo,
            "tipo": tipo,
            "descripcion": descripcion.strip(),
            "materia": materia.strip(),
            "canal": canal,
            "prioridad": p,
            "estado": "pendiente",
            "responsable": None,
            "fecha": hoy,
            "historial": [hoy + " creada (pendiente)"],
        }
        self.solicitudes.append(s)
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"estudiantes": self.estudiantes, "responsables": self.responsables,
                   "solicitudes": self.solicitudes, "contador": contador}, f, indent=2, ensure_ascii=False)
        f.close()
        if p == 3:
            pr = "ALTA"
        elif p == 2:
            pr = "MEDIA"
        else:
            pr = "BAJA"
        print("Solicitud #" + str(contador) + " registrada con prioridad " + pr)
        return True

    def asignar_responsable(self, id_sol, id_resp):
        sol = None
        for x in self.solicitudes:
            if x["id"] == id_sol:
                sol = x
        if sol == None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return False
        r = None
        for x in self.responsables:
            if x["id"] == id_resp:
                r = x
        if r == None:
            print("Error: no existe el responsable " + str(id_resp))
            return False
        if sol["estado"] == "resuelta" or sol["estado"] == "rechazada":
            print("Error: la solicitud ya esta cerrada")
            return False
        sol["responsable"] = id_resp
        hoy = datetime.now().strftime("%Y-%m-%d")
        sol["historial"].append(hoy + " asignada a " + r["nombre"])
        if sol["estado"] == "pendiente":
            sol["estado"] = "en_proceso"
            sol["historial"].append(hoy + " pendiente -> en_proceso")
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"estudiantes": self.estudiantes, "responsables": self.responsables,
                   "solicitudes": self.solicitudes, "contador": contador}, f, indent=2, ensure_ascii=False)
        f.close()
        print("Solicitud #" + str(id_sol) + " asignada a " + r["nombre"] + " (" + r["area"] + ")")
        return True

    def cambiar_estado(self, id_sol, nuevo):
        sol = None
        for x in self.solicitudes:
            if x["id"] == id_sol:
                sol = x
        if sol == None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return "error"
        ant = sol["estado"]
        ok = False
        if ant == "pendiente":
            if nuevo == "en_proceso":
                if sol["responsable"] == None:
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
        hoy = datetime.now().strftime("%Y-%m-%d")
        sol["historial"].append(hoy + " " + ant + " -> " + nuevo)
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump({"estudiantes": self.estudiantes, "responsables": self.responsables,
                   "solicitudes": self.solicitudes, "contador": contador}, f, indent=2, ensure_ascii=False)
        f.close()
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
            if s["prioridad"] == 3:
                pr = "ALTA"
            elif s["prioridad"] == 2:
                pr = "MEDIA"
            else:
                pr = "BAJA"
            resp = "-"
            if s["responsable"] != None:
                for r in self.responsables:
                    if r["id"] == s["responsable"]:
                        resp = r["nombre"]
            print(f"{s['id']:<5}{s['fecha']:<12}{s['tipo']:<17}{pr:<11}{s['estado']:<13}{s['legajo']:<8}{resp}")
        print("Total: " + str(len(l)))
        return l

    def ver_detalle(self, id_sol):
        sol = None
        for x in self.solicitudes:
            if x["id"] == id_sol:
                sol = x
        if sol == None:
            print("Error: no existe la solicitud #" + str(id_sol))
            return
        est = None
        for e in self.estudiantes:
            if e["legajo"] == sol["legajo"]:
                est = e
        print("Solicitud #" + str(sol["id"]) + " - " + sol["tipo"])
        print("  Estudiante: " + est["nombre"] + " (" + est["legajo"] + ", " + est["email"] + ")")
        if sol["materia"] != "":
            print("  Materia: " + sol["materia"])
        print("  Descripcion: " + sol["descripcion"])
        if sol["prioridad"] == 3:
            pr = "ALTA"
        elif sol["prioridad"] == 2:
            pr = "MEDIA"
        else:
            pr = "BAJA"
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
            if p == 3:
                pr = "ALTA"
            elif p == 2:
                pr = "MEDIA"
            else:
                pr = "BAJA"
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

    # def calcular_prioridad_vieja(self, tipo):
    #     if tipo == "reclamo_nota":
    #         return 3
    #     return 1

    def listar_responsables(self):
        for r in self.responsables:
            print(str(r["id"]) + ". " + r["nombre"] + " - " + r["area"])
