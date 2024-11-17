import random

def generate_h(filename):
    num_h = random.randint(4, 6)
    _h = list(range(1, num_h + 1))
    
    with open(filename, 'w') as file:
        file.write("#H\n")
        for h in _h:
            file.write(f"{h}\n")

def generate_conjuntos(h_filename, conjuntos_filename):
    with open(h_filename, 'r') as file:
        lines = file.readlines()
    
    ids = [int(line.strip()) for line in lines[1:]]
    
    max_num_sets = random.randint(len(ids), len(ids) + len(ids)//2)
    
    sets = set()
    for id in ids:
        while True:
            set_size = random.randint(2, len(ids) - 1)
            new_set = set(random.sample(ids, set_size))
            new_set.add(id)
            if len(new_set) < len(ids):
                sets.add(tuple(sorted(new_set)))
                break
    
    while len(sets) < max_num_sets:
        set_size = random.randint(2, len(ids) - 1)
        new_set = tuple(sorted(random.sample(ids, set_size)))
        if new_set not in sets and len(new_set) < len(ids):
            sets.add(new_set)
    
    with open(conjuntos_filename, 'w') as file:
        file.write("#Conjuntos\n")
        for conjunto in sets:
            file.write("-".join(map(str, conjunto)) + "\n")

generate_h("H.txt")
generate_conjuntos("H.txt", "Conjuntos.txt")





