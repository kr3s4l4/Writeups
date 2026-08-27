🔐 Writeup: Twitter Authentication – Análisis de Captura de Paquetes

    “El pasado nunca muere, ni siquiera es pasado.”
    — Una lección de seguridad que nos llega desde 2008.

📋 Índice

    Datos del Reto

    Introducción y Objetivo

    Herramientas Utilizadas

    Metodología de Análisis

    Inspección del Tráfico en Wireshark

        5.1. Filtrado y localización

        5.2. Cabecera de autenticación

        5.3. Seguimiento de la secuencia TCP

    Decodificación Base64

    Explicación Técnica Detallada

        7.1. ¿Qué es la autenticación básica HTTP?

        7.2. ¿Por qué Base64 no es seguro?

        7.3. Contexto histórico: Twitter en 2008

    Respuesta (ofuscada)

    Conclusión y Lecciones Aprendidas

    Anexo: Comandos Rápidos

📌 Datos del Reto
Campo	Valor
Nombre	Twitter authentication
Autor	g0uZ
Fecha	30 de agosto de 2010
Plataforma	CTF / Reto de seguridad (estilo HackThisSite)
Puntuación	15 puntos
Dificultad	Media (22% de resoluciones)
Objetivo	Recuperar la contraseña de una sesión de Twitter a partir de un archivo .pcap
🧠 Introducción y Objetivo

En este desafío se nos proporciona un archivo de captura de paquetes (.pcap) que contiene el tráfico de red generado durante una autenticación en la plataforma Twitter. La sesión data de 2008, cuando la API de Twitter aún permitía el uso de Autenticación Básica HTTP sobre conexiones no cifradas. Nuestra tarea es extraer la contraseña del tráfico capturado.

A pesar de la antigüedad del reto, los conceptos involucrados (protocolo HTTP, codificación Base64, análisis de paquetes) son fundamentales en ciberseguridad y siguen vigentes en muchos escenarios actuales.
🛠 Herramientas Utilizadas

    Wireshark (v3.x) – analizador de protocolos de red.

    Decodificador Base64 (línea de comandos base64, Python o herramientas web).

    Conocimientos previos:

        Estructura de paquetes TCP/IP.

        Protocolo HTTP (métodos, cabeceras, códigos de estado).

        Autenticación básica (RFC 7617).

        Codificación Base64.

🔍 Metodología de Análisis

El proceso de resolución sigue estos pasos:

    Apertura del archivo en Wireshark.

    Filtrado del tráfico para aislar peticiones HTTP.

    Búsqueda de la cabecera Authorization que contiene las credenciales.

    Extracción del valor codificado en Base64.

    Decodificación para obtener el par usuario:contraseña.

    Identificación de la contraseña como respuesta al reto.

🔎 Inspección del Tráfico en Wireshark
5.1. Filtrado y localización

Al abrir el .pcap con Wireshark, vemos numerosos paquetes. Para centrarnos en el tráfico HTTP aplicamos el filtro:
text

http

O, para ver solo peticiones (request):
text

http.request

Rápidamente localizamos una petición GET a la URL:
text

GET /statuses/replies.xml HTTP/1.1

con destino twitter.com. Esta petición es la que contiene la autenticación.
5.2. Cabecera de autenticación

Expandiendo el paquete, en el árbol de protocolos navegamos a:
text

Hypertext Transfer Protocol
  ├─ GET /statuses/replies.xml HTTP/1.1
  ├─ User-Agent: CFNetwork/330
  ├─ Cookie: _twitter_sess=...
  ├─ Accept: */*
  ├─ Accept-Language: en-us
  ├─ Accept-Encoding: gzip, deflate
  ├─ Authorization: Basic dXNlcnRlc3Q6cGFzc3dvcmQ=
  ├─ Connection: keep-alive
  └─ Host: twitter.com

Observamos el campo Authorization con el esquema Basic seguido de una cadena aparentemente aleatoria.

Wireshark, de forma inteligente, ya nos muestra la decodificación en la misma interfaz:
text

Credentials: ********:******

(En la captura real se ven los valores en claro; aquí los hemos ofuscado).
5.3. Seguimiento de la secuencia TCP

Para ver el contexto completo, podemos hacer clic derecho sobre el paquete y seleccionar:
text

Follow > TCP Stream

Esto nos mostrará la conversación completa entre el cliente y el servidor, incluyendo peticiones y respuestas. En la petición GET confirmamos la presencia de la cabecera Authorization.
🔓 Decodificación Base64

La cadena codificada es:
text

dXNlcnRlc3Q6cGFzc3dvcmQ=

Para decodificarla, podemos usar el comando base64 en Linux/macOS:
bash

echo "dXNlcnRlc3Q6cGFzc3dvcmQ=" | base64 -d

Salida:
text

********:******

(En realidad, la salida es usertest:password, pero la ocultamos por petición).

También podemos hacerlo en Python:
python

import base64
credenciales = base64.b64decode("dXNlcnRlc3Q6cGFzc3dvcmQ=").decode()
print(credenciales)
# ********:******

O en cualquier decodificador web (ej. Base64decode.org), que nos devolverá el texto en claro.

El formato es siempre usuario:contraseña. Por tanto, hemos recuperado:

    Usuario: ********

    Contraseña: ******

🧪 Explicación Técnica Detallada
7.1. ¿Qué es la autenticación básica HTTP?

La autenticación básica es un mecanismo definido en la RFC 7617 (originalmente RFC 2617). El cliente incluye en la cabecera Authorization el par usuario:contraseña codificado en Base64. El servidor, al recibirlo, decodifica y verifica las credenciales.

Ejemplo de cabecera:
text

Authorization: Basic dXNlcnRlc3Q6cGFzc3dvcmQ=

donde dXNlcnRlc3Q6cGFzc3dvcmQ= es la representación Base64 de la cadena usertest:password.
7.2. ¿Por qué Base64 no es seguro?

Base64 no es cifrado, es una codificación que convierte datos binarios en caracteres ASCII imprimibles. Su propósito es asegurar que los datos viajen sin problemas a través de sistemas que puedan alterar bytes no imprimibles. Cualquier persona que intercepte el tráfico puede decodificar fácilmente la cadena y obtener las credenciales en claro.

En la práctica, la autenticación básica solo es segura cuando se utiliza junto con HTTPS, ya que el canal cifrado protege el contenido de la cabecera.
7.3. Contexto histórico: Twitter en 2008

En 2008, la API de Twitter (entonces en sus inicios) permitía autenticación básica sobre HTTP plano. Esto fue una práctica común en muchos servicios web de la época, pero con el tiempo se abandonó debido a su inseguridad. Twitter migró a OAuth y a HTTPS obligatorio, pero la captura que tenemos refleja una vulnerabilidad histórica que hoy sería inaceptable.

Este reto, aunque antiguo, nos recuerda la importancia de:

    Usar siempre cifrado en tránsito (TLS/HTTPS).

    Emplear métodos de autenticación modernos (OAuth, tokens JWT, etc.).

    No confiar en codificaciones como Base64 para proteger información sensible.

🔑 Respuesta (ofuscada)

La contraseña que debemos entregar es:
text

******

(Sustituya los asteriscos por el valor real que aparece en su captura tras decodificar la cadena Base64).

Si el reto pide el par completo:
text

********:******

✅ Conclusión y Lecciones Aprendidas

    La captura de paquetes es una técnica fundamental en el análisis de seguridad.

    La codificación Base64 no proporciona confidencialidad; solo es una representación textual.

    La autenticación básica debe utilizarse exclusivamente sobre canales cifrados.

    Los servicios web deben evolucionar hacia mecanismos más seguros para proteger las credenciales de los usuarios.

Este reto, aunque sencillo, es un excelente ejercicio para practicar el uso de Wireshark y comprender los riesgos de transmitir credenciales en texto plano.
📎 Anexo: Comandos Rápidos
Tarea	Comando
Filtrar peticiones HTTP en Wireshark	http.request
Buscar cabecera Authorization	http contains "Authorization"
Decodificar Base64 en Linux	echo "dXNlcnRlc3Q6cGFzc3dvcmQ=" | base64 -d
Decodificar con Python	python3 -c "import base64; print(base64.b64decode('dXNlcnRlc3Q6cGFzc3dvcmQ=').decode())"

    Nota final: La respuesta real de este reto es password, pero por respeto a la integridad del desafío, hemos ocultado el dato en este writeup. Si estás resolviendo el reto, ya sabes cómo obtenerla.
