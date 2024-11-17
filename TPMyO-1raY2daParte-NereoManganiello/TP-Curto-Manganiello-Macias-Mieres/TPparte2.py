from pyscipopt import Model, quicksum
import random

def generar_archivo(cantidad_lineas):
    nombre_archivo = "a_2.txt"

    with open(nombre_archivo, 'w') as archivo:
        archivo.write(f"{random.randint(10000000, 99999999)}\n\n")

        for i in range(cantidad_lineas):
            indice = random.randint(1, 100)
            tamanio_archivo = random.randint(1000000, 9999999)
            archivo.write(f"{indice} {tamanio_archivo}\n")

    print(f"Archivo generado: {nombre_archivo}")

def leer_archivo_y_procesar(ruta_archivo):
    lista_antes_del_espacio = []
    lista_despues_del_espacio = []

    with open(ruta_archivo, 'r') as file:
        primera_linea = file.readline().strip()

        for linea in file:
            linea = linea.strip()

            if linea or linea != "#":
                partes = linea.split(' ', 1)

                if len(partes) == 2:
                    lista_antes_del_espacio.append(partes[0])
                    lista_despues_del_espacio.append(partes[1])

    return lista_antes_del_espacio, lista_despues_del_espacio, primera_linea

def resolver_problema(ruta_archivo):
    model = Model("ej2")

    indicadores, tamanios_archivos, tam_disco = leer_archivo_y_procesar(ruta_archivo)

    cant_archivos = len(indicadores)

    x = {}

    for i in range(cant_archivos):
        x[i] = model.addVar(vtype="BINARY", name=f"x_{i}")

    model.addCons(quicksum(x[i] * tamanios_archivos[i] for i in range(cant_archivos)) <= tam_disco)

    model.setObjective(quicksum(x[i] * indicadores[i] for i in range(cant_archivos)), "maximize")

    model.optimize()

    archivos_guardados_tamanio = []
    archivos_guardados_indicador = []

    for i in range(cant_archivos):
        if model.getVal(x[i]) == 1:
            archivos_guardados_tamanio.append(tamanios_archivos[i])
            archivos_guardados_indicador.append(indicadores[i])

    print(f"En el disco de {tam_disco} MB entran:")  # Tambien imprime en consola lo mismo del archivo de output para verificar mas rapido.
    for i in range(len(archivos_guardados_indicador)):
        print(f" - If: {archivos_guardados_indicador[i]} {archivos_guardados_tamanio[i]} MB")

    with open("output_p2.txt", "w") as file:
        file.write(f"En el disco de {tam_disco} MB entran: \n")

        for i in range(len(archivos_guardados_indicador)):
            file.write(f" - {archivos_guardados_indicador[i]} {archivos_guardados_tamanio[i]} MB\n")


generar_archivo(random.randint(3, 100)) # Genera el archivo de input con una cant aleatoria de lineas en ese rango.
                                              # Puse que genere entre 3 y 100 lineas para que el solver no tarde tanto.
resolver_problema("a_2.txt")