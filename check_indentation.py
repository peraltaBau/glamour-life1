def check_indentation(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("Revisando indentación...")
    for i, line in enumerate(lines, 1):
        if i >= 430 and i <= 440:  # Revisa alrededor de la línea 435
            print(f"Línea {i}: {repr(line)}")
    
    # Buscar líneas problemáticas
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('image_filename = "default_product.jpg"'):
            print(f"\n⚠️  Línea problemática encontrada en línea {i}:")
            print(f"Contenido: {repr(line)}")
            print(f"Indentación: {len(line) - len(line.lstrip())} espacios")
            
            # Mostrar contexto
            start = max(0, i-3)
            end = min(len(lines), i+2)
            print(f"\nContexto (líneas {start}-{end}):")
            for j in range(start, end):
                marker = ">>>" if j == i-1 else "   "
                print(f"{marker} {j+1}: {lines[j].rstrip()}")

if __name__ == "__main__":
    check_indentation("app.py")
