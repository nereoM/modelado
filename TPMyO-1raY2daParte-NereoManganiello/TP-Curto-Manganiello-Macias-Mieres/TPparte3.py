from pyscipopt import Model, quicksum


def leerH(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    h = [int(line.strip()) for line in lines if not line.startswith('#')]

    return h

def leerConjuntos(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    conjuntos = [set(map(int, line.strip().split('-'))) for line in lines if not line.startswith('#')]

    return conjuntos

def minimizarConjuntos(C, H):
    model = Model()

    # Variables
    x = {}
    for i in range(len(H)):
        x[i] = model.addVar(name=f"x_{i}", vtype="B")

    # Funci�n objetivo
    model.setObjective(quicksum(x[i] for i in range(len(H))), "minimize")

    # Restricciones
    for c in C:
        model.addCons(quicksum(x[i] for i in range(len(H)) if c in H[i]) >= 1)

    model.optimize()

    solution = [i for i in range(len(H)) if model.getVal(x[i]) == 1]

    return solution

hPath = 'H.txt'
h = leerH(hPath)
print("H:", h)

cPath = 'Conjuntos.txt'
c = leerConjuntos(cPath)
print("Conjuntos:", c)

solution = minimizarConjuntos(h, c)
print("Subconjuntos seleccionados:", solution)
