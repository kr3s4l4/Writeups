🔍 ETHERNET - frame (Root-Me) – Writeup

Autor del writeup: [Tu nombre]
Dificultad: Nivel 1 (Fácil)
Objetivo: Encontrar los datos presuntamente confidenciales en una trama Ethernet.

📌 Descripción del reto

Se nos proporciona un volcado hexadecimal de una trama Ethernet. Nuestra tarea es extraer la información oculta, que se encuentra en las capas superiores del paquete.

🛠️ Herramientas utilizadas

    Wireshark (o tshark) – para visualizar la estructura de la trama.

    xxd – para convertir el volcado hexadecimal a binario.

    strings – para extraer cadenas legibles.

    base64 – para decodificar la autenticación HTTP.

    text2pcap (opcional) – para convertir el hex a formato pcap.

📄 Paso 1: Inspección del volcado

El archivo proporcionado contiene una línea de bytes en hexadecimal (sin offsets ni marcas de tiempo):
text

00 05 73 a0 00 00 e0 69 95 d8 5a 13 86 dd 60 00
00 00 00 9b 06 40 26 07 53 00 00 60 2a bc 00 00
00 00 ba de c0 de 20 01 41 d0 00 02 42 33 00 00
00 00 00 00 00 04 96 74 00 50 bc ea 7d b8 00 c1
d7 03 80 18 00 e1 cf a0 00 00 01 01 08 0a 09 3e
69 b9 17 a1 7e d3 47 45 54 20 2f 20 48 54 54 50
2f 31 2e 31 0d 0a 41 75 74 68 6f 72 69 7a 61 74
69 6f 6e 3a 20 42 61 73 69 63 20 59 32 39 75 5a
6d 6b 36 5a 47 56 75 64 47 6c 68 62 41 3d 3d 0d
0a 55 73 65 72 2d 41 67 65 6e 74 3a 20 49 6e 73
61 6e 65 42 72 6f 77 73 65 72 0d 0a 48 6f 73 74
3a 20 77 77 77 2e 6d 79 69 70 76 36 2e 6f 72 67
0d 0a 41 63 63 65 70 74 3a 20 2a 2f 2a 0d 0a 0d
0a

🔬 Análisis de cabeceras

Podemos identificar manualmente las capas de red:
Capa	Tamaño (bytes)	Contenido destacado
Ethernet	14	MAC destino: 00:05:73:a0:00:00
MAC origen: e0:69:95:d8:5a:13
EtherType: 0x86dd → IPv6
IPv6	40	Origen: 2607:5300:0060:2abc:0000:0000:bade:c0de
Destino: 2001:41d0:0002:4233:0000:0000:0000:0004
Protocolo: 0x06 (TCP)
TCP	32 (variable)	Puerto origen: 0x9674 (38516)
Puerto destino: 0x0050 (80 – HTTP)
Offset de datos: 0x80 → 32 bytes de cabecera
Payload	Resto	Petición HTTP (texto ASCII)

🧩 Paso 2: Extracción del payload HTTP

Podemos extraer el texto legible usando la combinación de xxd y strings:
bash

# Convertir el hex a binario
cat ch12.txt | tr -d ' ' | xxd -r -p > ch12.bin

# Buscar cadenas ASCII
strings ch12.bin

Salida:
text

GET / HTTP/1.1
Authorization: Basic Y29u******************hbA==
User-Agent: InsaneBrowser
Host: www.myipv6.org
Accept: */*

🔑 Paso 3: Decodificar autenticación Basic

El campo Authorization: Basic Y29u********************hbA== contiene credenciales codificadas en Base64.

Decodificamos:
bash

echo Y29u***********hbA== | base64 -d

Resultado:
text

********************

La cadena tiene el formato usuario:contraseña.

    Usuario: **********

    Contraseña: **********

📘 Explicación detallada (didáctica)
¿Qué es una trama Ethernet?

Una trama Ethernet es la unidad de datos que viaja por una red de área local (LAN). Contiene direcciones MAC de origen y destino, un campo de tipo (EtherType) y los datos de las capas superiores.
Estructura de este paquete

    Ethernet (14 B)

        6 B MAC destino

        6 B MAC origen

        2 B EtherType (0x86dd → IPv6)

    IPv6 (40 B)
    Cabecera fija de 40 bytes que incluye direcciones de 128 bits, longitud del payload, protocolo siguiente (TCP), etc.

    TCP (32 B)
    La cabecera TCP tiene un tamaño variable. En este caso, el campo Data Offset (bits 4–7 del byte 13 de la cabecera TCP) vale 0x80 que, desplazado 4 bits a la derecha, da 0x08; multiplicado por 4 = 32 bytes. Por eso la cabecera TCP ocupa 32 bytes exactos.

    Payload HTTP
    Tras la cabecera TCP encontramos texto ASCII correspondiente a una petición HTTP GET. Este texto contiene la cabecera Authorization, que es el objetivo del reto.

¿Por qué Authorization: Basic ...?

HTTP Basic Authentication envía el usuario y la contraseña en un solo campo codificado en Base64. Aunque Base64 no es cifrado, es una forma de codificar texto binario en caracteres imprimibles. Al decodificar obtenemos las credenciales en texto plano.
¿Cómo identificar la trama manualmente?

    Los primeros 14 bytes son Ethernet.

    El byte 13 y 14 (86 dd) indican IPv6.

    A continuación, 40 bytes de IPv6.

    Después, la cabecera TCP. El byte 13 de TCP (el que está a 14+40+12 = 66 bytes del inicio) contiene 0x80, lo que nos dice que la cabecera TCP mide 32 bytes.

    Lo que queda es el payload (HTTP). Buscamos secuencias ASCII como GET, HTTP, Authorization.

Este método es la base del análisis de protocolos de red y es fundamental para entender cómo funciona la comunicación en capas.

🧪 Alternativa con Wireshark

Para visualizar el paquete de forma gráfica, podemos convertirlo a formato pcap y abrirlo con Wireshark:
bash

# Usando text2pcap con opción -D (datos sin offsets)
text2pcap -D ch12.txt ch12.pcap
wireshark ch12.pcap

En Wireshark, podemos usar "Follow TCP Stream" para ver el diálogo HTTP completo, incluyendo las cabeceras.

✅ Conclusión

El reto ETHERNET - frame es una excelente introducción al análisis de paquetes de red. Hemos aprendido a:

    Identificar y saltar cabeceras de red (Ethernet, IPv6, TCP).

    Extraer el payload de una comunicación HTTP.

    Reconocer y decodificar autenticación Basic en Base64.

La flag es ***************, que corresponde a las credenciales del usuario.

📎 Anexo: Comandos usados
Comando							Propósito
cat ch12.txt | tr -d ' ' | xxd -r -p > ch12.bin		Convertir hex a binario
strings ch12.bin					Extraer texto ASCII
echo Y29uZmk6ZGVudGlhbA== | base64 -d			Decodificar Base64
text2pcap -D ch12.txt ch12.pcap				Convertir a pcap para Wireshark
