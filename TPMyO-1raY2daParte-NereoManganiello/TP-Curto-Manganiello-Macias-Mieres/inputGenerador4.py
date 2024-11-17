import random

def generar_archivo_input(nombre_archivo, num_archivos, tamanios_posibles, capacidad_disco):
    with open(nombre_archivo, 'w') as f:
        f.write(f"# Capacidad del disco: {capacidad_disco} MB\n")
        f.write(f"# Número de archivos: {num_archivos}\n\n")

        for i in range(num_archivos):
            identificador = f"archivo_{i + 1}"
            tamanio = random.choice(tamanios_posibles)
            f.write(f"{identificador} {tamanio}\n")

tamanios_posibles = random.sample(range(100, 20000), k=15)  # Entre 10 y 20 tamaños posibles
generar_archivo_input('inputp4.txt', 200, tamanios_posibles, 100000)