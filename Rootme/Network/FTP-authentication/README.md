Writeup: Reto "FTP - Authentication" (Análisis de Captura)

Autor: [Tu nombre / Alias]
Fecha: Agosto 2026
Dificultad: 1/5 (Muy Fácil)
Categoría: Forense / Análisis de Protocolos

1. Introducción y objetivo

El reto nos proporciona un archivo de captura de paquetes (.pcap) correspondiente a una sesión de transferencia de archivos mediante el protocolo FTP (File Transfer Protocol).

El enunciado indica que se ha producido un "intercambio de archivos autenticado" y nos pide recuperar la contraseña utilizada por el usuario.

El objetivo es demostrar que, al viajar en texto plano, las credenciales FTP pueden ser interceptadas y extraídas fácilmente con un analizador de tráfico, evidenciando una grave vulnerabilidad de seguridad en este protocolo heredado.

2. Herramientas empleadas

Para la resolución se ha utilizado:

    Wireshark (versión 4.x) – para el análisis visual e interactivo de la captura.

    tshark (CLI de Wireshark) – para la extracción automática de datos desde terminal.

(Opcionalmente, herramientas como tcpdump, ngrep o incluso strings sobre el binario podrían haber funcionado).

3. Metodología de análisis

He seguido un flujo de trabajo estructurado y eficiente:

    Apertura del PCAP en Wireshark.

    Filtrado inicial para aislar únicamente el tráfico FTP (puerto 21).

    Inspección de la conversación y localización del intercambio de credenciales.

    Extracción manual de la contraseña desde el payload del paquete.

    Verificación mediante el código de respuesta del servidor.

4. Análisis detallado de los paquetes

Al aplicar el filtro ftp en Wireshark (o tcp.port == 21), observamos la siguiente secuencia de intercambio (extraída directamente de la tabla del reto):
Nº	Tiempo	Origen	Destino	Protocolo	Info relevante
4	0.060630	10.20.144.151	10.20.144.150	FTP	Response: 220-QTCP at fran.csg.stercomm.com.
6	0.275760	10.20.144.151	10.20.144.150	FTP	Response: 220 Connection will close if idle...
8	4.216600	10.20.144.150	10.20.144.151	FTP	Request: USER cdts3500
9	4.217350	10.20.144.151	10.20.144.150	FTP	Response: 331 Enter password.
11	7.639420	10.20.144.150	10.20.144.151	FTP	Request: PASS ************** ⬅️ ¡Aquí está!
13	8.184000	10.20.144.151	10.20.144.150	FTP	Response: 230 CDTS3500 logged on.

4.1. Fase de bienvenida (Handshake)

Los paquetes 4 y 6 corresponden al mensaje de bienvenida del servidor (código 220). El servidor se identifica como fran.csg.stercomm.com y notifica que la conexión se cerrará tras 5 minutos de inactividad. Esta fase confirma que el servicio FTP está operativo y listo para recibir comandos.

4.2. Envío del nombre de usuario (USER)

En el paquete 8, el cliente (desde la IP 10.20.144.150) envía el comando:
text

USER cdts3500

El servidor responde en el paquete 9 con el código 331 Enter password., indicando que el usuario es válido y solicitando la contraseña. Ya tenemos el nombre de usuario: cdts3500.

4.3. Envío de la contraseña (PASS) — ¡Punto crítico!

En el paquete 11 encontramos la clave del reto:
text

PASS ***************

Aquí viaja la contraseña en texto plano, sin ningún tipo de cifrado, ofuscación o hash. Es la vulnerabilidad inherente al FTP estándar.

4.4. Confirmación de autenticación

El paquete 13 confirma el éxito de la operación. El servidor responde con el código 230 y el mensaje:
text

230 CDTS3500 logged on.

Este código valida que tanto el usuario como la contraseña son correctos. Si la contraseña hubiera sido errónea, el servidor habría respondido con un 530 Login incorrect.

5. Extracción automatizada de la contraseña (modo terminal)

Aunque en este caso la contraseña es visible a simple vista, en retos con tráfico masivo es útil saber extraerla con tshark:
bash

tshark -r captura.pcap -Y "ftp.request.command == PASS" -T fields -e ftp.request.arg

Salida esperada:
text

******************

6. Conclusión y lecciones aprendidas

Contraseña recuperada: cdts3500
(Que coincide exactamente con el nombre de usuario, lo cual es una pésima práctica de seguridad).
Reflexión sobre la seguridad:

Este reto evidencia un problema de seguridad crítico y muy común en entornos heredados:

    FTP transmite credenciales en texto plano. Cualquier atacante con acceso a la red (o con un simple tcpdump) puede capturar y leer nombres de usuario y contraseñas.

    Reutilización de credenciales: En este caso, el usuario y la contraseña son idénticos (cdts3500), lo que agrava aún más la vulnerabilidad.

    Mitigación: Para entornos productivos, es obligatorio migrar a SFTP (SSH File Transfer Protocol) o FTPS (FTP over SSL/TLS), que cifran todo el tráfico, incluyendo las credenciales y los datos transferidos.

7. Flag / Respuesta final
text

********************

8. Anexo I: Filtros útiles para Wireshark (Guía de referencia)

Dominar los filtros de visualización y captura es lo que separa a un analista novato de uno eficiente. En este reto apenas hemos necesitado mirar 6 paquetes, pero en capturas reales con miles o millones de paquetes, aplicar el filtro correcto es la clave.

Aquí tienes mi recopilación personal de filtros "salvavidas" organizados por casos de uso. Te servirán para el 90% de los retos de forensia o CTF:

8.1. Filtros específicos para FTP (aplicados en este reto)

Filtro en Wireshark							Explicación y uso práctico

ftp									Muestra todo el tráfico FTP (comandos + respuestas). Es el filtro de entrada para aislar la conversación.
ftp.request.command == "USER"						Aísla los paquetes que contienen el nombre de usuario. Ideal para identificar rápidamente quién intenta autenticarse.
ftp.request.command == "PASS"						El filtro estrella. Muestra únicamente los paquetes que contienen la contraseña. En este reto, con esto ya tenías la flag.
ftp.response.code == 230						Filtra respuestas exitosas (230). Si ves esto, sabes que justo antes viajaron las credenciales correctas.
ftp.response.code == 331						Filtra la petición de contraseña. Sirve para verificar que el usuario existía antes de enviar el PASS.
ftp.request.command == "USER" or ftp.request.command == "PASS"		Muestra ambos comandos de autenticación a la vez, viendo usuario y contraseña en una sola vista.

8.2. Filtros para encontrar flags en texto plano

Filtro				Explicación

frame contains "flag"		Busca la cadena literal "flag" en todo el paquete (cabeceras + payload). Es el primer filtro que pruebo cuando no sé por dónde empezar.
frame contains "ctf"		Similar al anterior, pero buscando "ctf".
tcp.payload contains "{"	Busca llaves { en el payload TCP. Muy útil si las flags tienen formato flag{...} o CTF{...}.
http contains "password"	Busca la palabra "password" dentro del tráfico HTTP. Ideal para capturar credenciales enviadas por formularios web (método POST).

8.3. Filtros para tráfico HTTP / Web

Filtro					Explicación

http					Muestra todo el tráfico HTTP.
http.request.method == "GET"		Filtra solo las peticiones GET (descarga de recursos).
http.request.method == "POST"		Filtra los envíos de formularios. Dentro de estos paquetes suelen viajar las credenciales de login en aplicaciones web.
http.request.uri contains "admin"	Busca peticiones a rutas que contengan "admin", revelando posibles paneles de control ocultos.
http.response.code == 200		Muestra respuestas exitosas (pueden contener datos sensibles o la flag en el HTML).
http.host == "ejemplo.com"		Filtra el tráfico hacia un dominio específico, útil para acotar ruido.

8.4. Filtros para DNS (detección de C2 o exfiltración)

Filtro				Explicación

dns				Muestra todas las consultas y respuestas DNS.
dns.qry.name contains "hack"	Busca dominios sospechosos en las consultas (ej: malware.com).
dns.flags.response == 0		Muestra solo las consultas (no las respuestas). Útil para ver qué dominios está preguntando la víctima.
dns.resp.len > 100		Filtra respuestas DNS con longitud anormalmente grande (posible túnel de datos o exfiltración mediante DNS).

8.5. Reconstrucción de conversaciones completas

Filtro / Acción				Explicación

tcp.stream eq 0				Aísla el flujo TCP número 0. Cada conversación TCP recibe un índice. Cambia el número para ver otras conversaciones.
udp.stream eq 0				Similar para UDP.
Acción: Follow → TCP Stream		Haz clic derecho sobre cualquier paquete → Follow → TCP Stream. Esto te abre una ventana con todo el intercambio de datos en texto plano (o en formato crudo). En este reto, si hubieras seguido el flujo TCP, habrías visto el USER cdts3500 y el PASS cdts3500 juntos en una sola vista.

8.6. Análisis de conexiones y escaneos de puertos

Filtro						Explicación

tcp.flags.syn == 1 and tcp.flags.ack == 0	Filtra los paquetes SYN puros (inicios de conexión). Útil para contar cuántos puertos está escaneando un atacante.
tcp.flags.reset == 1				Filtra paquetes RST (reinicio de conexión). Muchos RST pueden indicar un escaneo de puertos cerrados.
icmp						Muestra tráfico ICMP (ping). Útil para detectar túneles ICMP o simplemente actividad de red básica.

8.7. Filtros por dirección IP y puerto

Filtro					Explicación

ip.src == 10.20.144.150			Muestra paquetes originados desde esa IP.
ip.dst == 10.20.144.151			Muestra paquetes destinados a esa IP.
tcp.port == 443				Filtra por puerto (en este caso, HTTPS).
tcp.port == 21 or tcp.port == 20	Filtra tanto el puerto de control (21) como el de datos (20) de FTP activo.

8.8. Filtros combinados con operadores lógicos

Wireshark admite and (&&), or (||) y not (!). Aquí tienes combinaciones avanzadas muy poderosas:

Filtro combinado							Explicación

ftp && (ip.src == 10.20.144.150)					Tráfico FTP enviado por el cliente.
http && !(http.request.method == "GET")					Tráfico HTTP que no sea GET (para cazar POST, PUT, DELETE).
tcp.port == 80 || tcp.port == 443					Todo el tráfico web (HTTP + HTTPS).
dns && not (dns.qry.name contains "google")				Muestra consultas DNS que no van a Google, perfecto para detectar dominios maliciosos o exfiltración.
tcp.flags.syn == 1 and tcp.flags.ack == 0 and tcp.port == 22		Busca intentos de conexión SSH (puerto 22) entrantes.

9. Anexo II: Métodos alternativos de extracción (sin Wireshark)

Por si te encuentras en un entorno sin interfaz gráfica, aquí tienes 3 formas más de obtener la contraseña directamente desde el archivo .pcap:

1. Con strings y grep:
bash

strings captura.pcap | grep -i "PASS"

2. Con tcpdump:
bash

tcpdump -r captura.pcap -A | grep -i "PASS"

3. Con ngrep:
bash

ngrep -I captura.pcap "PASS" port 21

Todas ellas devolverán la línea con PASS cdts3500.
