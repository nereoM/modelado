
from pyscipopt import Model, quicksum

# Leer la familia H desde un archivo generado
def leerFamiliaH(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    H = [list(map(int, line.strip().split())) for line in lines if not line.startswith('#')]
    return H

# Leer el conjunto C desde un archivo
def leerConjuntosC(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    C = [set(map(int, line.strip().split('-'))) for line in lines if not line.startswith('#')]
    return C

"""
# Modelo relajado utilizando H y C
def modeloRelajado(C, H):
    model = Model()

    # Variables relajadas
    x = {}
    for i in range(len(H)):
        x[i] = model.addVar(name=f"x_{i}", vtype="C", lb=0, ub=1)

    # Función objetivo: minimizar la suma de las variables
    model.setObjective(quicksum(x[i] for i in range(len(H))), "minimize")

    # Restricciones: cubrir cada conjunto en C
    for c in C:
        model.addCons(quicksum(x[i] for i in range(len(H)) if set(H[i]).issubset(c)) >= 1)

    # Resolver el modelo
    model.optimize()

    # Inicializar solution para evitar el error de variable no definida
    solution = {}

    # Verificar si el modelo tiene una solución óptima o factible
    if model.getStatus() in ['optimal', 'feasible']:
        solution = {i: model.getVal(x[i]) for i in range(len(H))}
    else:
        print("El modelo no es factible o no tiene una solución óptima.")

    return solution

# Leer los archivos de entrada
hPath = 'H.txt'  # Archivo generado con la familia H
cPath = 'Conjuntos.txt'  # Archivo con los conjuntos C

H = leerFamiliaH(hPath)
C = leerConjuntosC(cPath)

# Resolver el modelo relajado
solution = modeloRelajado(C, H)

# Imprimir las soluciones relajadas
print("Solución relajada:")
for i, val in solution.items():
    print(f"x_{i} = {val:.3f}")
"""

from pyscipopt import Model, quicksum

# Leer la familia H desde un archivo generado
def leerFamiliaH(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    H = [list(map(int, line.strip().split())) for line in lines if not line.startswith('#')]
    return H

# Función para leer los conjuntos C
def leerConjuntosC(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    C = []
    for line in lines:
        line = line.strip()  # Eliminar espacios en blanco extra
        if line and not line.startswith('#'):  # Ignorar comentarios
            # Dividir por el guion
            elements = line.split('-')
            # Convertir cada elemento a int y agregarlo a C
            C.extend([int(item) for item in elements if item.isdigit()])  # Solo agregar números válidos

    return C


def modeloPrimal(C, H):
    # Crear el modelo
    model = Model("PrimalRelaxado")

    # Variables: uno por cada archivo, x_c = 1 si el archivo c es seleccionado en un conjunto H
    x = {}
    for i, c in enumerate(C):
        x[i] = model.addVar(vtype="C", name=f"x_{i}")

    # Restricciones: cada archivo debe estar en al menos uno de los conjuntos de la familia H
    for h in H:  # H es una lista de conjuntos de archivos
        model.addCons(sum(x[i] for i in h) >= 1, name=f"constraint_h_{H.index(h)}")

    # Objetivo: minimizar el número de conjuntos seleccionados
    model.setObjective(sum(x[i] for i in range(len(C))), sense="minimize")

    # Resolver el modelo primal relajado
    model.setParam("lp/solvefreq", 1)  # Forzar solución LP en cada nodo
    model.setParam("lp/cleanuprows", True)
    model.setPresolve(0)

    model.optimize()

    # Verificar si el modelo fue resuelto de manera óptima
    if model.getStatus() == "optimal":
        print("Solución Primal:")
        for i in range(len(C)):
            print(f"x_{i} = {model.getVal(x[i])}")

        # Obtener las soluciones duales (multiplicadores de Lagrange) para las restricciones activas
        print("\nSoluciones Dual:")
        for cons in model.getConss():
            if cons.isActive():
                try:
                    dual_value = model.getDualsolLinear(cons)  # Obtener el valor dual
                    print(f"Dual de la restricción {cons.getName()} = {dual_value}")
                except Exception as e:
                    print(f"Error al obtener el valor dual para la restricción {cons.getName()}: {e}")



def modelo_simple():
    # Crear el modelo
    model = Model("EjemploDual")

    # Variables continuas
    x1 = model.addVar(vtype="C", name="x1")
    x2 = model.addVar(vtype="C", name="x2")

    # Restricciones
    cons1 = model.addCons(2 * x1 + x2 >= 1, name="cons1")
    cons2 = model.addCons(x1 + x2 <= 2, name="cons2")

    # Función objetivo
    model.setObjective(x1 + 2 * x2, sense="minimize")

    # Configuración para asegurarse de que las soluciones duales estén disponibles
    model.setParam("lp/solvefreq", 1)  # Resolver el problema LP en cada nodo
    model.setParam("presolving/maxrounds", 0)  # Desactivar presolución

    # Resolver el modelo
    model.optimize()

    # Verificar si se resolvió de manera óptima
    if model.getStatus() == "optimal":
        print("Solución Primal:")
        print(f"x1 = {model.getVal(x1)}")
        print(f"x2 = {model.getVal(x2)}")

        # Soluciones duales
        print("\nSoluciones Duales:")
        for i, cons in enumerate(model.getConss()):
            try:
                dual_value = model.getDualsolLinear(cons)  # Obtener el valor dual
                print(f"Dual de la restricción {i} ({str(cons)}) = {dual_value}")
            except Exception as e:
                print(f"Error al obtener el dual de la restricción {i} ({str(cons)}): {e}")

#modelo_simple()



# Leer los archivos de entrada
hPath = 'H.txt'  # Archivo generado con la familia H
cPath = 'Conjuntos.txt'  # Archivo con los conjuntos C

H = leerFamiliaH(hPath)
C = leerConjuntosC(cPath)

# Resolver el modelo relajado
modeloPrimal(C, H)
"""
# Imprimir las soluciones relajadas
print("Solución relajada:")
for i, val in enumerate(solution):
    print(f"x_{i} = {val:.3f}")
"""
# Para obtener la solución dual, puedes usar model.getDuals()

