from gestor import GestorSolicitudes

TIPOS = ["certificado", "equivalencia", "cambio_comision", "reclamo_nota", "baja_materia"]


def menu():
    print("")
    print("==== SISTEMA DE SOLICITUDES ACADEMICAS ====")
    print("1. Registrar estudiante")
    print("2. Registrar solicitud")
    print("3. Asignar responsable")
    print("4. Cambiar estado")
    print("5. Buscar / filtrar solicitudes")
    print("6. Ver detalle de solicitud")
    print("7. Reporte")
    print("0. Salir")


def main():
    g = GestorSolicitudes()
    while True:
        menu()
        op = input("Opcion: ").strip()
        if op == "1":
            legajo = input("Legajo: ").strip()
            nombre = input("Nombre: ")
            email = input("Email: ").strip()
            g.registrar_estudiante(legajo, nombre, email)
        elif op == "2":
            legajo = input("Legajo: ").strip()
            nombre = ""
            email = ""
            if g.buscar_estudiante(legajo) is None:
                print("Estudiante nuevo, complete sus datos")
                nombre = input("Nombre: ")
                email = input("Email: ").strip()
            print("Tipos: " + ", ".join(TIPOS))
            tipo = input("Tipo: ").strip()
            descripcion = input("Descripcion: ")
            materia = input("Materia (opcional): ")
            u = input("Urgente (s/n): ").strip().lower()
            urgente = False
            if u == "s":
                urgente = True
            canal = input("Canal (web/presencial/email): ").strip()
            g.registrar_solicitud(legajo, nombre, email, tipo, descripcion, materia, urgente, canal)
        elif op == "3":
            try:
                id_sol = int(input("ID solicitud: "))
            except:
                print("Error: ID invalido")
                continue
            g.listar_responsables()
            try:
                id_resp = int(input("ID responsable: "))
            except:
                print("Error: ID invalido")
                continue
            g.asignar_responsable(id_sol, id_resp)
        elif op == "4":
            try:
                id_sol = int(input("ID solicitud: "))
            except:
                print("Error: ID invalido")
                continue
            nuevo = input("Nuevo estado (en_proceso/resuelta/rechazada): ").strip()
            g.cambiar_estado(id_sol, nuevo)
        elif op == "5":
            estado = input("Estado (enter = todos): ").strip()
            tipo = input("Tipo (enter = todos): ").strip()
            legajo = input("Legajo (enter = todos): ").strip()
            pm = input("Prioridad minima 1-3 (enter = todas): ").strip()
            if pm == "":
                pm = 0
            else:
                try:
                    pm = int(pm)
                except:
                    print("Error: prioridad invalida")
                    continue
            g.buscar(estado, tipo, legajo, pm)
        elif op == "6":
            try:
                id_sol = int(input("ID solicitud: "))
            except:
                print("Error: ID invalido")
                continue
            g.ver_detalle(id_sol)
        elif op == "7":
            g.reporte()
        elif op == "0":
            print("Hasta luego")
            break
        else:
            print("Opcion invalida")


main()
