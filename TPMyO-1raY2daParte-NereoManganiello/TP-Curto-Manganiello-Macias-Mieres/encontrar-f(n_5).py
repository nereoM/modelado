import os
from configparser import ConfigParser
import TPparte5


def cargar_configuracion(archivo_cfg):
    """
    Lee las configuraciones desde el archivo .cfg.
    """
    config = ConfigParser()
    config.read(archivo_cfg)

    in_path = config.get('DEFAULT', 'inPath')
    out_path = config.get('DEFAULT', 'outPath')
    threshold = int(config.get('DEFAULT', 'threshold'))

    # Verificar existencia de los directorios
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"La ruta de entrada no existe: {in_path}")
    if not os.path.exists(out_path):
        os.makedirs(out_path)  # Crear si no existe

    return in_path, out_path, threshold


def generar_archivo_input(base_file, num_lineas, output_file, capacidad_disco):
    """
    Genera un archivo de entrada tomando exactamente `num_lineas` líneas de datos relevantes
    del archivo base, y escribe un encabezado con la capacidad del disco y la cantidad de archivos.
    """
    if not os.path.exists(base_file):
        raise FileNotFoundError(f"El archivo base no existe: {base_file}")

    with open(base_file, 'r') as base, open(output_file, 'w') as out:
        # Leer todas las líneas del archivo base
        all_lines = [line.strip() for line in base if line.strip()]  # Eliminar líneas vacías

        # Filtrar solo las líneas de datos (ignorar encabezados y metadatos)
        datos_lineas = [
            line for line in all_lines
            if not line.startswith("#") and not line.isdigit()
        ]

        # Validar si hay suficientes líneas de datos
        if num_lineas > len(datos_lineas):
            raise ValueError(f"El archivo base tiene menos de {num_lineas} líneas de datos.")

        # Escribir encabezados en el archivo de salida
        out.write("# disk capacity in TB\n")
        out.write(f"{capacidad_disco}\n")  # Capacidad del disco
        out.write("# cantidad de archivos\n")
        out.write(f"{num_lineas}\n")  # Número correcto de archivos

        # Escribir las primeras `num_lineas` líneas de datos relevantes
        for i in range(num_lineas):
            out.write(datos_lineas[i] + "\n")

    print(f"Archivo generado correctamente: {output_file}")



def ejecutar_solver(input_file, threshold):
    """
    Ejecuta el solver en el archivo de entrada dado y verifica si encuentra un óptimo.
    """
    optimo = TPparte5.main(input_file, threshold)
    return optimo


def busqueda_binaria(in_path, out_path, threshold, archivo_base):
    base_file = os.path.join(in_path, archivo_base)

    with open(base_file, 'r') as base:
        # Contar las líneas de datos y extraer solo las que no son comentarios
        datos_lineas = [line.strip() for line in base if line.strip() and not line.startswith("#")]

        if len(datos_lineas) < 2:
            raise ValueError("El archivo no contiene suficientes datos para procesar la cantidad de archivos y la capacidad del disco.")

        # Obtener la cantidad de archivos y la capacidad del disco
        try:
            capacidad_disco = int(datos_lineas[0])
        except ValueError:
            raise ValueError("No se pudo convertir la capacidad del disco a un entero.")

        max_n = len(datos_lineas) - 1  # Ajustar para excluir la línea de capacidad del disco

    low, high = 1, max_n
    resultado = None

    while low <= high:
        mid = (low + high) // 2
        archivo_mid = os.path.join(out_path, f"f{mid:04d}.in")
        archivo_mid_next = os.path.join(out_path, f"f{mid + 1:04d}.in")

        # Generar los archivos para `mid` y `mid + 1`
        generar_archivo_input(base_file, mid, archivo_mid, capacidad_disco)
        generar_archivo_input(base_file, mid + 1, archivo_mid_next, capacidad_disco)

        # Verificar si el solver encuentra un óptimo para `f(mid)`
        sol_mid = ejecutar_solver(archivo_mid, threshold)
        sol_mid_next = ejecutar_solver(archivo_mid_next, threshold)

        # Si encontramos una solución óptima para `f(mid)` pero NO para `f(mid+1)`
        if sol_mid and not sol_mid_next:
            resultado = mid
            break
        elif sol_mid:
            # Si aún se encuentra solución óptima para mid, continuar buscando hacia arriba
            low = mid + 1
        else:
            # Si no se encuentra solución óptima para mid, continuar buscando hacia abajo
            high = mid - 1

    return resultado


def main():
    # Leer configuración
    archivo_cfg = os.path.abspath("archivo.cfg")
    in_path, out_path, threshold = cargar_configuracion(archivo_cfg)

    # Archivo base
    archivo_base = "f2048.in"

    # Ejecutar búsqueda binaria para encontrar n_1
    n_5 = busqueda_binaria(in_path, out_path, threshold, archivo_base)

    print(f"n_5 encontrado: {n_5}")


if __name__ == "__main__":
    main()