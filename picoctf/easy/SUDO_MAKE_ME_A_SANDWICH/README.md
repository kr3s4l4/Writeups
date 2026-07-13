PicoCTF - Sudo Make Me A Sandwich
📋 Información General
Campo	Valor
Reto	Sudo Make Me A Sandwich
Categoría	Linux / Privilege Escalation
Dificultad	Fácil
Puntos	100
Flag	picoCTF{ju57_5ud0_17_f8185e1e}
📝 Descripción del Reto

En este reto, nos conectamos a un servidor remoto donde tenemos una sesión SSH como el usuario ctf-player. Nuestro objetivo es escalar privilegios y obtener acceso como root para leer la flag.
🔍 Reconocimiento Inicial
Conexión SSH

Primero, nos conectamos al servidor usando las credenciales proporcionadas:
bash

ssh -p 63168 ctf-player@green-hill.picoctf.net

Credenciales:

    Usuario: ctf-player

    Contraseña: (proporcionada en el reto)

https://i.imgur.com/placeholder.png
Verificación de Permisos Sudo

Al entrar al sistema, verificamos qué comandos podemos ejecutar con privilegios de superusuario:
bash

ctf-player@challenge:~$ sudo -l

Resultado:
text

Matching Defaults entries for ctf-player on challenge:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User ctf-player may run the following commands on challenge:
    (ALL) NOPASSWD: /bin/emacs

https://i.imgur.com/placeholder.png
Análisis de la Configuración

El resultado es muy interesante:

    Podemos ejecutar /bin/emacs como cualquier usuario (ALL)

    No se requiere contraseña (NOPASSWD)

    El binario está en una ruta segura (/bin/emacs)

🚀 Explotación
Vector de Ataque

Emacs es un editor de texto extremadamente poderoso que incluye funcionalidades para ejecutar shells, terminales y comandos del sistema. Al ejecutarlo como root, podemos abrir un shell dentro de emacs que heredará los privilegios de root.
Ejecución del Exploit

Ejecutamos emacs como root en modo terminal:
bash

sudo /bin/emacs -Q -nw --eval '(term "/bin/sh")'

Explicación de las opciones:

    -Q: Inicia emacs sin archivos de inicialización (limpio)

    -nw: Modo "no-window" - fuerza la interfaz en terminal

    --eval '(term "/bin/sh")': Evalúa código Elisp que abre un terminal con /bin/sh

https://i.imgur.com/placeholder.png
Obteniendo Shell Root

Dentro de emacs, tenemos un terminal interactivo. Verificamos nuestros privilegios:
bash

# whoami
root

¡Somos root! 🎉
📂 Encontrando la Flag

Ahora que somos root, buscamos la flag:
bash

# ls
flag.txt

Encontramos el archivo flag.txt en el directorio actual:
bash

# cat flag.txt
picoCTF{*********************************}

https://i.imgur.com/placeholder.png
🔧 Explicación Técnica
¿Por qué funciona?

    Privilegios de sudo: El archivo /etc/sudoers está configurado para permitir que ctf-player ejecute /bin/emacs como cualquier usuario sin contraseña.

    Funcionalidad de emacs: Emacs tiene comandos internos para ejecutar procesos del sistema:

        term: Ejecuta un terminal completo

        shell: Ejecuta una shell de Unix

        eshell: Ejecuta una shell implementada en Elisp

    Herencia de privilegios: Cuando emacs se ejecuta como root (via sudo), cualquier proceso hijo que emacs inicie (como el shell) hereda los mismos privilegios.

Medidas de Mitigación

Para prevenir este tipo de escalación:

    Restringir binarios: No permitir que usuarios ejecuten editores o herramientas que puedan spawnear shells

    Usar sudo -e: Para editar archivos, usar la opción de edición segura de sudo

    Políticas de AppArmor/SELinux: Restringir lo que emacs puede hacer incluso si se ejecuta como root

    Principio de mínimo privilegio: Solo dar acceso a comandos específicos que son realmente necesarios
