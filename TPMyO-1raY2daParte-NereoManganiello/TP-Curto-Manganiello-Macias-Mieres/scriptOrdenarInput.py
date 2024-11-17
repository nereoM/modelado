# Leer y procesar el archivo
with open('inputp4.txt', 'r') as file:
    lines = file.readlines()

# Procesar las líneas y saltar las que están vacías o comienzan con '#'
files = []
for line in lines:
    # Ignorar líneas vacías o que comiencen con '#'
    if line.strip() and not line.startswith('#'):
        name, size = line.split()
        files.append((name, int(size)))

# Ordenar la lista de archivos por tamaño
files_sorted = sorted(files, key=lambda x: x[1])

# Reescribir el archivo con los datos ordenados
with open('inputp4.txt', 'w') as file:
    # Escribir el encabezado original (líneas que comienzan con '#')
    for line in lines:
        if line.startswith('#'):
            file.write(line)
    # Escribir los archivos ordenados
    for name, size in files_sorted:
        file.write(f"{name} {size}\n")


