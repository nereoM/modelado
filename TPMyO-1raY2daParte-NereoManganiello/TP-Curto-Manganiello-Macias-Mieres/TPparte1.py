import random
import string
from pyscipopt import Model, quicksum
import TPparte5seccion1

def generar_archivo_output(nombre_archivo_output, discos_usados, asignacion_archivos, tamanios_archivos):

    with open(nombre_archivo_output, 'w') as f:
        f.write(f"Para la configuracion del archivo {"a_1.txt"}, {len(discos_usados)} discos son suficientes.")
        f.write(f"Discos usados: {len(discos_usados)}\n\n")

        for j in discos_usados:
            archivos = asignacion_archivos[j]
            tamanio_total = sum(tamanios_archivos[i] for i in archivos)
            f.write(f"Disco {j + 1}: {tamanio_total} MB\n")

            for i in archivos:
                f.write(f"  Archivo {i}: {tamanios_archivos[i]} MB\n")

            f.write("\n")


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


def resolver_problema(ruta_archivo):

    model = Model("ej1")

    tam_archivos, tam_discos = leer_archivo_input(ruta_archivo)

    cant_archivos = len(tam_archivos)

    # Supongo que al principio tengo 1 disco por archivo
    cant_discos = len(tam_archivos)

    x = {}
    y = {}

    for j in range(cant_discos):
        y[j] = model.addVar(vtype="BINARY", name=f"y_{j}")
        for i in range(cant_archivos):
            x[i, j] = model.addVar(vtype="BINARY", name=f"x_{i}_{j}")

    for i in range(cant_archivos):
        model.addCons(quicksum(x[i, j] for j in range(int(cant_discos))) == 1)

    for j in range(cant_discos):
        cont = 0
        model.addCons(quicksum(int(tam_archivos[i]) * x[i, j] for i in range(cant_archivos)) <= tam_discos * y[j])

    model.setObjective(quicksum(y[j] for j in range(cant_discos)), "minimize")

    # utilizamos estos 2 parametros para limitar la búsqueda del óptimo a 1 hora,
    # y utilizamos el gap para que encuentre una solución factible rápido y pueda seguir buscando el óptimo
    # si el tiempo lo permite.
    model.setParam("limits/time", 1800)
    model.setParam("limits/gap", 0.05)

    model.optimize()

    discos_usados = [j for j in range(int(cant_discos)) if model.getVal(y[j]) == 1]


    print(f"Para la configuración del archivo {"a_1.txt"}, {len(discos_usados)} discos son suficientes.")

    asignacion_archivos = {j: [i for i in range(len(tam_archivos)) if model.getVal(x[i, j]) == 1] for j in discos_usados}

    print("Discos usados:", len(discos_usados))
    for j in discos_usados:
        archivos = asignacion_archivos[j]
        tamanio_total = sum(int(tam_archivos[i]) for i in archivos)
        print(f"Disco {j + 1}: {tamanio_total} MB")
        for i in archivos:
            print(f"  Archivo {i}: {tam_archivos[i]} MB")

    generar_archivo_output("output_p1.txt", discos_usados, asignacion_archivos, tam_archivos)


resolver_problema('a_1.txt')

# Ejemplo de uso
tamanios_archivos, capacidad_disco = leer_archivo_input("a_1.txt")
familia_h = TPparte5seccion1.generar_familia_h(tamanios_archivos, capacidad_disco)

# Imprimir la familia H generada
print("Familia H generada:")
for subconjunto in familia_h:
    print(subconjunto)



