"""
from pyscipopt import Model, quicksum

def generar_familia_h(tamanios_archivos, capacidad_disco):
    Genera la familia H de subconjuntos de archivos que caben en un disco utilizando PySCIPOpt.

    :param tamanios_archivos: Lista con los tamaños de los archivos.
    :param capacidad_disco: Capacidad máxima del disco (Z).
    :return: Lista de subconjuntos H donde cada subconjunto es una lista de índices de archivos.

    n = len(tamanios_archivos)  # Número de archivos
    soluciones = []  # Lista para almacenar las soluciones

    while True:
        # Crear un modelo nuevo
        model = Model("Generar_Familia_H_v4")

        # Variables binarias: x[i] = 1 si el archivo i está en el subconjunto, 0 de lo contrario
        x = {}
        for i in range(n):
            x[i] = model.addVar(vtype="BINARY", name=f"x_{i}")

        # Restricción: La suma de los tamaños de los archivos seleccionados no puede superar la capacidad del disco
        model.addCons(quicksum(tamanios_archivos[i] * x[i] for i in range(n)) <= capacidad_disco)

        # Agregar restricciones adicionales para excluir soluciones ya encontradas
        for solucion in soluciones:
            model.addCons(quicksum(x[i] for i in solucion) <= len(solucion) - 1)

        # Optimizar el modelo
        model.optimize()
        status = model.getStatus()

        # Si no hay más soluciones óptimas, salir del bucle
        if status != "optimal":
            break

        # Obtener la solución actual
        solucion_actual = []
        for i in range(n):
            if model.getVal(x[i]) > 0.5:  # Si la variable está activada
                solucion_actual.append(i)

        # Agregar la solución actual a la lista de soluciones
        soluciones.append(solucion_actual)

    return soluciones
"""

from pyscipopt import Model, quicksum

def generar_familia_h(tamanios_archivos, capacidad_disco):
    model = Model("Generar Familias H")
    n = len(tamanios_archivos)

    # Variables binarias: x[i] = 1 si el archivo i está en la familia
    x = {i: model.addVar(vtype="B", name=f"x_{i}") for i in range(n)}

    # Restricción de capacidad
    model.addCons(quicksum(tamanios_archivos[i] * x[i] for i in range(n)) <= capacidad_disco)

    # Maximizar el número de archivos seleccionados
    model.setObjective(quicksum(x[i] for i in range(n)), "maximize")

    # Optimizar
    model.optimize()

    # Verificar estado de la solución
    if model.getStatus() == "optimal":
        # Extraer la solución óptima
        solucion = [i for i in range(n) if model.getVal(x[i]) > 0.5]
        print("Familia H encontrada:", solucion)
        return solucion
    else:
        print("No se encontraron familias H factibles.")
        return []


