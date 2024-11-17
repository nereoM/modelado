from pyscipopt import Model, quicksum

import random

def leer_archivo_input(nombre_archivo):
    tamanios_archivos = []
    capacidad_disco = 0

    with open(nombre_archivo, 'r') as f:
        for linea in f:
            if linea.startswith("# Capacidad del disco:"):
                capacidad_disco = int(linea.split(":")[1].strip().split()[0])
            elif not linea.startswith("#") and linea.strip():
                _, tamanio = linea.split()
                tamanios_archivos.append(int(tamanio))

    return tamanios_archivos, capacidad_disco


def generar_archivo_output(nombre_archivo_output, discos_usados, asignacion_archivos, tamanios_archivos):

    with open(nombre_archivo_output, 'w') as f:
        f.write(f"Discos usados: {len(discos_usados)}\n\n")

        for j in discos_usados:
            archivos = asignacion_archivos[j]
            tamanio_total = sum(tamanios_archivos[i] for i in archivos)
            f.write(f"Disco {j + 1}: {tamanio_total} MB\n")

            for i in archivos:
                f.write(f"  Archivo {i}: {tamanios_archivos[i]} MB\n")

            f.write("\n")


def minimizar_discos(tamanios_archivos, capacidad_disco, max_tamanios_por_disco):
    model = Model("MinimizarDiscos")

    n = len(tamanios_archivos)
    tamanios_posibles = list(set(tamanios_archivos))
    max_discos = n

    x = {}
    y = {}
    z = {}

    for i in range(n):
        for j in range(max_discos):
            x[i, j] = model.addVar(vtype="BINARY", name=f"x({i},{j})")

    for j in range(max_discos):
        y[j] = model.addVar(vtype="BINARY", name=f"y({j})")

    for j in range(max_discos):
        for t in tamanios_posibles:
            z[t, j] = model.addVar(vtype="BINARY", name=f"z({t},{j})")

    # restricciones:

    for i in range(n):
        model.addCons(quicksum(x[i, j] for j in range(max_discos)) == 1, f"Archivo_{i}_unico_disco")

    for j in range(max_discos):
        model.addCons(quicksum(x[i, j] * tamanios_archivos[i] for i in range(n)) <= capacidad_disco * y[j], f"Capacidad_disco_{j}")

    for j in range(max_discos):
        model.addCons(quicksum(z[t, j] for t in tamanios_posibles) <= max_tamanios_por_disco, f"MaxTamanios_disco_{j}")

    for j in range(max_discos):
        for t in tamanios_posibles:
            model.addCons(quicksum(x[i, j] for i in range(n) if tamanios_archivos[i] == t) >= z[t, j], f"RelacionArchivoTamano_{t}_{j}")

    for i in range(n):
        for j in range(max_discos):
            model.addCons(x[i, j] <= y[j], f"ArchivoUsaDisco_{i}_{j}")

    model.setObjective(quicksum(y[j] for j in range(max_discos)), "minimize")

    # utilizamos estos 2 parametros para limitar la búsqueda del óptimo a 1 hora,
    # y utilizamos el gap para que encuentre una solución factible rápido y pueda seguir buscando el óptimo
    # si el tiempo lo permite.
    model.setParam("limits/time", 1800)
    model.setParam("limits/gap", 0.05)

    model.optimize()

    discos_usados = [j for j in range(max_discos) if model.getVal(y[j]) == 1]
    asignacion_archivos = {j: [i for i in range(n) if model.getVal(x[i, j]) == 1] for j in discos_usados}

    print("Discos usados:", len(discos_usados))
    for j in discos_usados:
        archivos = asignacion_archivos[j]
        tamanio_total = sum(tamanios_archivos[i] for i in archivos)
        print(f"Disco {j + 1}: {tamanio_total} MB")
        for i in archivos:
            print(f"  Archivo {i}: {tamanios_archivos[i]} MB")

    generar_archivo_output("outputp4.txt", discos_usados, asignacion_archivos, tamanios_archivos)

num_archivos = 50  # Número de archivos a generar
capacidad_disco = 50000  # Capacidad en MB (por ejemplo)
tamanios_archivos, capacidad_disco = leer_archivo_input("inputp4.txt")
print("Tamaños de archivos:", tamanios_archivos)
print("Capacidad del disco:", capacidad_disco)

minimizar_discos(tamanios_archivos, capacidad_disco, 7)