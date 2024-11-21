from pyscipopt import Model, SCIP_PARAMSETTING, SCIP_STATUS
import random
import math

def leer_y_generar_conjuntos(archivo_H):
    
    with open(archivo_H, "r") as f:
        lines = f.read().strip().split("\n")
    
    # Leer capacidad del disco en TB y convertir a MB
    capacidad_tb = float(lines[1].strip())  # Capacidad en TB
    capacidad = capacidad_tb * 1024 * 1024  # Convertir a MB

    # Leer archivos y sus tamaños a partir de la línea 5
    archivos = lines[5:]  # Saltar las líneas de encabezado

    H = {}
    for line in archivos:
        parts = line.strip().split()
        if len(parts) == 2:  # Asegurarse de que la línea tenga dos elementos
            file_id, size = parts
            H[file_id] = int(size)
    
    # Generar conjuntos aleatorios
    conjuntos = generar_conjuntos(H, capacidad)
    print(len(H))

    return H, conjuntos, capacidad

def generar_conjuntos(H, capacidad_maxima):
    elementos = list(H.keys())
    conjuntos = []


    # Asegurarse de que cada elemento esté en al menos un conjunto
    elementos_no_asignados = set(elementos)
    while elementos_no_asignados:
        conjunto = []
        peso_total = 0

        while peso_total < capacidad_maxima:
            # Filtrar los elementos que todavía puedan caber
            elementos_validos = [
                e for e in elementos_no_asignados if H[e] + peso_total <= capacidad_maxima
            ]
            if not elementos_validos:
                break  # Salir del bucle si no hay elementos válidos

            elemento = random.choice(elementos_validos)
            peso = H[elemento]

            conjunto.append(elemento)
            peso_total += peso
            elementos_no_asignados.remove(elemento)

        conjuntos.append(conjunto)

    # Generar exactamente la mitad del número de archivos como conjuntos adicionales
    num_conjuntos_adicionales = math.ceil(len(elementos) / 2)

    for _ in range(num_conjuntos_adicionales):
        conjunto = []
        peso_total = 0
        intentos = 0

        while peso_total < capacidad_maxima and intentos < 100:  # Límite de intentos
            # Filtrar elementos que puedan caber
            elementos_validos = [
                e for e in elementos if H[e] + peso_total <= capacidad_maxima and e not in conjunto
            ]
            if not elementos_validos:
                break  # Salir del bucle si no hay elementos válidos

            elemento = random.choice(elementos_validos)
            peso = H[elemento]

            conjunto.append(elemento)
            peso_total += peso
            
            intentos += 1

        if conjunto:  # Solo agregar conjuntos no vacíos
            conjuntos.append(conjunto)

    return conjuntos

def resolver_modelo_relajado(H, conjuntos, threshold):
    model = Model("Cobertura_Minima")
    model.setPresolve(SCIP_PARAMSETTING.OFF)
    model.setHeuristics(SCIP_PARAMSETTING.OFF)
    model.disablePropagation()

    # Variables para los conjuntos
    x = {j: model.addVar(name=f"x_{j}", vtype="C", lb=0.0, ub=1.0) for j in range(len(conjuntos))}

    # Tamaños únicos
    tamanios = set(H.values())

    # Variables auxiliares: y[j, t] indica si el conjunto j incluye un archivo de tamaño t
    y = {(j, t): model.addVar(name=f"y_{j}_{t}", vtype="C", lb=0.0, ub=1.0) for j in range(len(conjuntos)) for t in tamanios}

    # Objetivo: Minimizar la cantidad de conjuntos seleccionados
    model.setObjective(
        sum(x[j] for j in range(len(conjuntos))), sense="minimize"
    )

    # Restricciones de cobertura
    restricciones = {
        archivo: model.addCons(
            sum(x[j] for j in range(len(conjuntos)) if archivo in conjuntos[j]) >= 1
        )
        for archivo in H
    }

    # Restricción para asociar tamaños con conjuntos
    for j in range(len(conjuntos)):
        for t in tamanios:
            model.addCons(
                y[j, t] >= max((1 if archivo in conjuntos[j] and H[archivo] == t else 0 for archivo in H), default=0)
            )

    # Restricción: no más de 7 tamaños distintos por conjunto
    for j in range(len(conjuntos)):
        model.addCons(
            sum(y[j, t] for t in tamanios) <= 7
        )

    tiempo_limite = threshold * 60
    model.setParam("limits/time", tiempo_limite)
    model.optimize()

    # Verificar el estado del modelo
    estado = model.getStatus()
    if estado == "optimal":
        # Obtener los resultados solo si el modelo es óptimo
        solucion_relajada = {j: model.getVal(x[j]) for j in range(len(conjuntos))}
        valor_objetivo = model.getObjVal()
        return model, restricciones, solucion_relajada, valor_objetivo
    elif estado == "infeasible":
        print("El modelo es infactible.")
        return False
    elif estado == "unbounded":
        print("El modelo no está acotado.")
        return False
    else:
        print(f"Estado desconocido del modelo: {estado}")
        return False


# Obtener la solución dual
def obtener_solucion_dual(model, restricciones):
    return {archivo: model.getDualsolLinear(restriccion) for archivo, restriccion in restricciones.items()}

def resolver_maxima_importancia(H, solucion_dual, capacidad, threshold):
    # Crear modelo
    model = Model("Maxima_Importancia")

    # Variables binarias de selección
    z = {archivo: model.addVar(vtype="B", name=f"z_{archivo}") for archivo in H}

    # Restricción de capacidad
    model.addCons(
        sum(z[archivo] * H[archivo] for archivo in H) <= capacidad
    )

    # Función objetivo
    model.setObjective(
        sum(z[archivo] * solucion_dual[archivo] for archivo in H), sense="maximize"
    )
    
    tiempo_limite = threshold * 60
    model.setParam("limits/time", tiempo_limite)
    # Optimizar el modelo
    model.optimize()

    # Verificar el estado del modelo
    estado = model.getStatus()
    if estado == "optimal":
        # Obtener los resultados solo si el modelo es óptimo
        seleccionados = [archivo for archivo in H if model.getVal(z[archivo]) > 0.5]
        valor_max_importancia = model.getObjVal()
        return seleccionados, valor_max_importancia
    elif estado == "infeasible":
        print("El modelo es infactible.")
        return False
    elif estado == "unbounded":
        print("El modelo no está acotado.")
        return False
    else:
        print(f"Estado desconocido del modelo: {estado}")
        return False

def resolver_modelo_entero(H, conjuntos, threshold):
    model = Model("Cobertura_Minima_Entera")

    # Variables para los conjuntos
    x = {j: model.addVar(name=f"x_{j}", vtype="B") for j in range(len(conjuntos))}

    # Tamaños únicos
    tamanios = set(H.values())

    # Variables auxiliares: y[j, t]
    y = {(j, t): model.addVar(name=f"y_{j}_{t}", vtype="B") for j in range(len(conjuntos)) for t in tamanios}

    # Restricciones de cobertura
    for archivo in H:
        model.addCons(
            sum(x[j] for j in range(len(conjuntos)) if archivo in conjuntos[j]) >= 1
        )

    # Restricción para asociar tamaños con conjuntos
    for j in range(len(conjuntos)):
        for t in tamanios:
            model.addCons(
                y[j, t] >= max((1 if archivo in conjuntos[j] and H[archivo] == t else 0 for archivo in H), default=0)
            )

    # Restricción: no más de 7 tamaños distintos por conjunto
    for j in range(len(conjuntos)):
        model.addCons(
            sum(y[j, t] for t in tamanios) <= 7
        )

    # Objetivo: Minimizar la cantidad de conjuntos seleccionados
    model.setObjective(
        sum(x[j] for j in range(len(conjuntos))), sense="minimize"
    )

    # Configuración de SCIP
    tiempo_limite = threshold * 60
    model.setParam("limits/time", tiempo_limite)
    model.setPresolve(SCIP_PARAMSETTING.OFF)
    model.setHeuristics(SCIP_PARAMSETTING.OFF)
    model.disablePropagation()

    # Intentar optimizar
    model.optimize()

    # Verificar el estado del modelo
    estado = model.getStatus()
    print(f"Estado del modelo: {estado}")

    if estado == "optimal":
        solucion_entera = {j: model.getVal(x[j]) for j in range(len(conjuntos))}
        return solucion_entera
    elif estado == "infeasible":
        print("El modelo es infactible.")
        return False
    elif estado == "unbounded":
        print("El modelo no está acotado.")
        return False
    else:
        print(f"Estado desconocido del modelo: {estado}")
        model.writeProblem("problema.lp")  # Exportar el modelo para análisis
        return False

def main(archivo_H, threshold):
    print("Leyendo datos...\n")
    H, conjuntos, capacidad = leer_y_generar_conjuntos(archivo_H)
    print("Datos leídos correctamente.")

    iteracion = 1
    while True:
        print(f"--- Iteración {iteracion} ---\n")

        # Resolver el modelo relajado
        resultado_relajado = resolver_modelo_relajado(H, conjuntos, threshold)
        if not resultado_relajado:
            print("No se pudo resolver el modelo relajado en la primera iteración. Terminando búsqueda...")
            return False

        modelo, restricciones, solucion_relajada, valor_objetivo = resultado_relajado

        # Obtener solución dual
        solucion_dual = obtener_solucion_dual(modelo, restricciones)

        # Resolver problema de máxima importancia
        resultado_importancia = resolver_maxima_importancia(H, solucion_dual, capacidad, threshold)
        if not resultado_importancia:
            print("No se pudo resolver el modelo de máxima importancia. Terminando...")
            return False

        seleccionados, valor_max_importancia = resultado_importancia

        # Verificar si se debe agregar un nuevo conjunto
        if valor_max_importancia <= 1:
            print("El valor máximo de importancia es bajo. No se agregan más conjuntos.")
            break  # Salir del bucle si no hay más conjuntos para agregar

        conjuntos.append(seleccionados)
        iteracion += 1

    # Resolver el modelo entero
    print("Resolviendo el problema de cobertura mínima con solución entera...\n")
    resultado_entero = resolver_modelo_entero(H, conjuntos, threshold)

    if not resultado_entero:
        print("No se pudo resolver el modelo entero. Terminando búsqueda...")
        return False

    #solucion_entera = resultado_entero
    print("Se encontró una solución óptima.")
    return True


#archivo_H = "H.txt"

#solucion_final = main(archivo_H, 7)
