"""Escenarios de caracterizacion (golden master).

Cada escenario es una lista de "corridas". Cada corrida es la secuencia de lineas
que un usuario tipearia en la consola. Varias corridas sobre el mismo archivo de
datos permiten verificar la persistencia entre ejecuciones.

Todos los datos son sinteticos (no corresponden a personas reales).
"""

FLUJO_COMPLETO = [[
    # alta de estudiantes
    "1", "10001", "Ana Perez", "ana.perez@mail.com",
    "1", "10002", "Bruno Diaz", "bruno.diaz@mail.com",
    # solicitudes de cada tipo
    "2", "10001", "reclamo_nota", "La nota del parcial 2 no coincide con la devolucion", "Programacion III", "s", "web",
    "2", "10002", "certificado", "Necesito certificado de alumno regular para trabajo", "", "n", "email",
    "2", "10003", "Carla Ruiz", "carla.ruiz@mail.com", "equivalencia", "Solicito equivalencia de materia aprobada en otra carrera", "Bases de Datos I", "n", "presencial",
    "2", "10001", "cambio_comision", "Pido cambio a la comision de la tarde por trabajo", "", "n", "presencial",
    "2", "10002", "baja_materia", "Solicito la baja de la materia por superposicion horaria", "Legislacion", "n", "web",
    "2", "10002", "cambio_comision", "Pido cambio de comision por superposicion horaria", "", "s", "web",
    # asignaciones y cambios de estado
    "3", "1", "2",
    "3", "3", "1",
    "4", "3", "resuelta",
    "4", "2", "rechazada",
    "3", "5", "3",
    # busquedas
    "5", "", "", "", "",
    "5", "en_proceso", "", "", "",
    "5", "", "cambio_comision", "", "",
    "5", "", "", "10002", "2",
    "5", "resuelta", "baja_materia", "", "",
    # detalle y reporte
    "6", "1",
    "6", "3",
    "7",
    "0",
]]

VALIDACIONES = [[
    "1", "123", "Nombre Corto", "x@mail.com",          # legajo invalido
    "1", "20001", "Diego Luna", "diego-mail.com",       # email sin @
    "1", "20001", "Diego Luna", "diego@mailcom",        # dominio sin punto
    "1", "20001", "   ", "diego@mail.com",              # nombre vacio
    "1", "20001", "Diego Luna", "diego@mail.com",       # ok
    "1", "20001", "Otro Nombre", "otro@mail.com",       # duplicado
    "2", "20001", "inscripcion", "Quiero inscribirme a una materia", "", "n", "web",   # tipo invalido
    "2", "20001", "certificado", "corta", "", "n", "web",                               # descripcion corta
    "2", "20001", "equivalencia", "Equivalencia de materia de otra facultad", "", "n", "web",  # falta materia
    "2", "20001", "certificado", "Certificado de examen rendido el lunes", "", "n", "fax",     # canal invalido
    "2", "20001", "certificado", "Certificado de examen rendido el lunes", "", "n", "web",     # ok -> #1
    "3", "abc",                                          # id no numerico
    "3", "99", "1",                                      # solicitud inexistente
    "3", "1", "9",                                       # responsable inexistente
    "3", "1", "x",                                       # id responsable no numerico
    "4", "1", "resuelta",                                # pendiente -> resuelta invalida
    "4", "1", "en_proceso",                              # sin responsable
    "4", "99", "resuelta",                               # inexistente
    "4", "z",                                            # id no numerico
    "4", "1", "rechazada",                               # ok
    "4", "1", "en_proceso",                              # cerrada -> invalida
    "3", "1", "2",                                       # asignar a cerrada
    "5", "", "", "", "alta",                             # prioridad no numerica
    "5", "pendiente", "", "", "",                        # sin resultados
    "6", "42",                                           # detalle inexistente
    "6", "q",                                            # detalle id invalido
    "9",                                                 # opcion invalida
    "0",
]]

PERSISTENCIA = [
    [
        "1", "30001", "Elena Mora", "elena.mora@mail.com",
        "2", "30001", "reclamo_nota", "Reclamo por nota del trabajo practico final", "Metodologia de Sistemas II", "n", "web",
        "2", "30001", "certificado", "Certificado de materias aprobadas para beca", "", "s", "email",
        "3", "2", "1",
        "0",
    ],
    [
        # segunda ejecucion: debe recordar estudiantes, solicitudes y el contador de ids
        "2", "30001", "baja_materia", "Baja de materia por motivos laborales", "Programacion IV", "n", "presencial",
        "4", "2", "resuelta",
        "5", "", "", "", "",
        "7",
        "0",
    ],
]

SISTEMA_VACIO = [[
    "5", "", "", "", "",
    "7",
    "0",
]]

ESCENARIOS = {
    "flujo_completo": FLUJO_COMPLETO,
    "validaciones": VALIDACIONES,
    "persistencia": PERSISTENCIA,
    "sistema_vacio": SISTEMA_VACIO,
}
