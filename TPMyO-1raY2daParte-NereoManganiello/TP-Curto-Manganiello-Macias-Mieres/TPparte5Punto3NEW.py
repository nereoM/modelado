from pyscipopt import Model, SCIP_PARAMSETTING

# Función para leer los archivos y procesar los conjuntos
def leer_archivos(archivo_H, archivo_conjuntos):
    with open(archivo_H, "r") as f:
        H = list(map(int, f.read().strip().split("\n")[1:]))

    with open(archivo_conjuntos, "r") as f:
        conjuntos = [list(map(int, linea.split("-"))) for linea in f.read().strip().split("\n")[1:]]

    return H, conjuntos

# Resolver el modelo relajado con pyscipopt
def resolver_modelo_relajado(H, conjuntos):
    # Crear el modelo
    model = Model("Cobertura_Minima")

    # Configuración para desactivar presolve, heurísticas y propagación
    model.setPresolve(SCIP_PARAMSETTING.OFF)
    model.setHeuristics(SCIP_PARAMSETTING.OFF)
    model.disablePropagation()

    # Variables: x_j indica si el conjunto j está en la solución relajada
    x = {}
    for j in range(len(conjuntos)):
        x[j] = model.addVar(name=f"x_{j}", vtype="C", lb=0.0, ub=1.0)  # Variable continua

    # Función objetivo: minimizar el número de conjuntos seleccionados
    model.setObjective(
        sum(x[j] for j in range(len(conjuntos))), sense="minimize"
    )

    # Restricciones: cada archivo debe estar cubierto por al menos un conjunto
    restricciones = {}
    for archivo in H:
        restriccion = model.addCons(
            sum(x[j] for j in range(len(conjuntos)) if archivo in conjuntos[j]) >= 1
        )
        restricciones[f"cover_{archivo}"] = restriccion

    # Resolver el modelo
    model.optimize()

    # Obtener resultados relajados
    solucion_relajada = {j: model.getVal(x[j]) for j in range(len(conjuntos))}
    valor_objetivo = model.getObjVal()

    return model, restricciones, solucion_relajada, valor_objetivo

# Obtener la solución dual
def obtener_solucion_dual(model, restricciones):
    duales = {}
    for nombre, restriccion in restricciones.items():
        valor_dual = model.getDualsolLinear(restriccion)
        duales[nombre] = valor_dual  # Asociar el nombre de la restricción con el valor dual
    return duales

# Archivos de entrada
archivo_H = "H.txt"
archivo_conjuntos = "Conjuntos.txt"

# Leer los datos
H, conjuntos = leer_archivos(archivo_H, archivo_conjuntos)

# Resolver el modelo relajado
modelo, restricciones, solucion_relajada, valor_objetivo = resolver_modelo_relajado(H, conjuntos)

# Obtener la solución dual
solucion_dual = obtener_solucion_dual(modelo, restricciones)

# Imprimir resultados
print("Solución relajada:")
for j, valor in solucion_relajada.items():
    print(f"Conjunto {j + 1}: {valor}")

print("\nValor objetivo (relajado):", valor_objetivo)

print("\nSolución dual:")
for restriccion, valor in solucion_dual.items():
    print(f"{restriccion}: {valor}")
