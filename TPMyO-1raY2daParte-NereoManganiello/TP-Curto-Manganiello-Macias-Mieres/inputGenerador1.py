import random

def generar_archivo_input(nombre_archivo, num_archivos, tamanios_posibles, capacidad_disco):
    with open(nombre_archivo, 'w') as f:
        f.write(f"# Capacidad del disco: {capacidad_disco} MB\n")
        f.write(f"# Numero de archivos: {num_archivos}\n\n")

        for i in range(num_archivos):
            identificador = f"archivo_{i + 1}"
            tamanio = random.choice(tamanios_posibles)
            f.write(f"{identificador} {tamanio}\n")

tamanios_posibles = [random.randint(1000, 3000) for _ in range(100)]
generar_archivo_input('a_1.txt', 50, tamanios_posibles, 10000)
