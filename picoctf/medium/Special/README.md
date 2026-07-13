Writeup: PicoCTF - Special
📋 Información del Reto

    Nombre: Special

    Plataforma: PicoCTF

    Categoría: Medium

    Descripción: Shell restrictivo con transformación de comandos

🔍 Análisis Inicial
Conexión al servidor
bash

ssh -p 60471 ctf-player@saturn.picoctf.net

Al conectarnos, nos encontramos con un shell que se comporta de manera extraña. Cualquier comando que introducimos es transformado antes de ejecutarse:
bash

Special$ ls
Is 
sh: 1: Is: not found

Special$ cat
Cat 
sh: 1: Cat: not found

Special$ whoami
Whom 
sh: 1: Whom: not found

Observación: El shell modifica la capitalización y aparentemente aplica alguna transformación a los comandos, actuando como un "corrector ortográfico" malicioso.
🛠️ Intentos de Escape
1. Técnicas básicas de evasión (FALLIDAS)

Probamos las técnicas habituales para shells restrictivos:
bash

# Usar comillas
Special$ 'ls'
Also 
sh: 1: Also: not found

# Usar rutas absolutas
Special$ /bin/ls
Absolutely not paths like that, please!

# Usar wildcards
Special$ *
blargh: not found

Descubrimiento: El wildcard * revela la existencia de un archivo/directorio llamado blargh.
2. Investigación del sistema (PARCIAL)

Al explorar variables de entorno, encontramos una pista interesante:
bash

Special$ echo $shell
Why go back to an inferior shell?

Pista: El sistema nos "advierte" que no intentemos volver a un shell normal, confirmando que estamos en un entorno modificado intencionalmente.
3. Intento de leer "blargh" (FALLIDO INICIALMENTE)

Intentamos leer el archivo blargh con varios métodos:
bash

Special$ cat blargh
Cat large 
sh: 1: Cat: not found

Problema clave: La transformación también afecta al nombre del archivo blargh → large

Intentamos con redirección:
bash

Special$ <blargh
# Sin salida, pero sin error

Y con bucles:
bash

Special$ while read line; do echo $line; done < blargh
Grew i < blarghwhile read line do echo line done < large 
sh: 1: cannot open large: No such file

💡 El Descubrimiento Crucial
Escape con comillas simples

Probando diferentes tipos de escaping, descubrimos que las comillas simples no son transformadas:
bash

Special$ 'blargh'
sh: 1: blargh: not found    # ¡No lo transformó a "large"!

Ejecución de comandos con $()

Combinando esto con sustitución de comandos, logramos ejecutar comandos reales:
bash

Special$ $('cat' 'blargh')
cat: blargh: Is a directory    # ¡blargh es un directorio!

¡Éxito parcial! Descubrimos que blargh es un directorio, no un archivo.
🚀 Explotación Exitosa
Paso 1: Listar el directorio blargh
bash

Special$ $('ls' 'blargh')
cat: blargh: Is a directory
sh: 1: flag.txt: not found

El error "flag.txt: not found" nos muestra que el shell intentó ejecutar flag.txt como comando, revelando que existe un archivo flag.txt dentro del directorio blargh.
Paso 2: Leer la flag
bash

Special$ $('cat' 'blargh/flag.txt')
sh: 1: picoCTF{*******************************}: not found

El shell intenta ejecutar el contenido de la flag como comando, ¡mostrándonos la flag en el mensaje de error!

📚 Explicación Técnica
¿Qué estaba pasando?

El shell implementaba un "corrector ortográfico" malicioso que transformaba los comandos usando un cifrado de sustitución simple:
Comando real	Transformado
ls	Is
cat	Cat
whoami	Whom
pwd	Pod
blargh	large
grep	Grew
awk	Ask
¿Por qué funcionaron las comillas simples?

Las comillas simples (') en bash preservan el valor literal de cada carácter, evitando que el script de transformación las modifique.
¿Por qué $()?

La sintaxis $(comando) ejecuta el comando en una subshell y sustituye su salida. Al combinar $() con comillas simples ($('cat' 'blargh/flag.txt')), logramos:

    Proteger los comandos de la transformación

    Ejecutar comandos reales del sistema

    Obtener la salida deseada

🔑 Lecciones Aprendidas

    Siempre probar diferentes tipos de quoting: simples, dobles, backslash

    Los wildcards (*) pueden revelar archivos ocultos

    Los mensajes de error a veces contienen información valiosa

    La sustitución de comandos ($()) puede bypassear restricciones

    Las pistas del sistema (como "Why go back to an inferior shell?") son intencionales
