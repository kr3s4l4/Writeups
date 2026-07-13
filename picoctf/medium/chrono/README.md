Writeup: Chrono - PicoCTF
🎯 Descripción

    How to automate tasks to run at intervals on linux servers?

Pista: "Automatizar tareas a intervalos" → Cron jobs.
🔍 ¿Por qué mirar cron?

La descripción habla de "tareas a intervalos". En Linux, esto se hace con cron, el programador de tareas del sistema.

En un caso real, las tareas cron se definen en varios sitios y se usan para automatizar backups, limpieza de logs, actualizaciones, etc. Por ejemplo:
bash

# /etc/crontab - Ejemplo de un caso real
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
  0 5 *   *   *   root  /usr/local/bin/backup.sh    # Backup diario a las 5 AM
 30 4 *   *   0   root  /usr/local/bin/update.sh    # Actualizaciones los domingos a las 4:30

O en directorios como:

    /etc/cron.daily/ → Scripts que se ejecutan cada día

    /etc/cron.hourly/ → Scripts que se ejecutan cada hora

    /etc/cron.weekly/ → Scripts semanales

📋 Paso 1: Conexión SSH
bash

ssh picoplayer@saturn.picoctf.net -p 60717
# Contraseña: emrdK96SGH

📋 Paso 2: Leer el crontab del sistema

Como la pista habla de tareas automatizadas, revisamos el archivo principal de configuración:
bash

cat /etc/crontab

Salida:
text

# picoCTF{****************************}

La flag está escrita directamente como un comentario dentro del archivo.

📚 Lección aprendida

Este reto enseña que /etc/crontab es un archivo clave en Linux donde se configuran tareas automatizadas, las cuales podriamos vulnerar para escalar privilegios por ejemplo. En un CTF o en un entorno real, siempre vale la pena revisarlo, ya que puede contener información sensible, rutas de scripts ejecutados como root, o directamente la flag como en este caso.
