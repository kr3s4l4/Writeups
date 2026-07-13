Writeup: Useless - picoCTF 2024
📊 Información del Reto

    Nombre: Useless

    Plataforma: picoCTF

    Categoría: General Skills

    Dificultad: Medium (100 pts)

    Autor: Loic Shema

    Descripción: There's an interesting script in the user's home directory

🔍 1. Enumeración Inicial
Conexión al servidor
bash

ssh picoplayer@saturn.picoctf.net -p 57148

Al iniciar sesión, enumeramos el directorio home:
bash

picoplayer@challenge:~$ ls
useless

Encontramos un script llamado useless. Verificamos su contenido:
bash

picoplayer@challenge:~$ cat useless
#!/bin/bash
# Basic mathematical operations via command-line arguments

if [ $# != 3 ]
then
  echo "Read the code first"
else
        if [[ "$1" == "add" ]]
        then 
          sum=$(( $2 + $3 ))
          echo "The Sum is: $sum"  

        elif [[ "$1" == "sub" ]]
        then 
          sub=$(( $2 - $3 ))
          echo "The Substract is: $sub" 

        elif [[ "$1" == "div" ]]
        then 
          div=$(( $2 / $3 ))
          echo "The quotient is: $div" 

        elif [[ "$1" == "mul" ]]
        then
          mul=$(( $2 * $3 ))
          echo "The product is: $mul" 

        else
          echo "Read the manual"
         
        fi
fi

Análisis del Script

    Es una calculadora básica con 4 operaciones: add, sub, div, mul

    Mensajes de error: "Read the code first" y "Read the manual"

    No hay funcionalidad oculta aparente en el código

🚨 2. Intentos de Explotación (Inyección de Comandos)

Siguiendo la metodología de CTF, intentamos varias técnicas de inyección de comandos aprovechando que el script usa $(( )) para evaluar expresiones aritméticas:
Intento 1: Búsqueda masiva de archivos flag
bash

./useless add "$(find / flag* 2>/dev/null)" 5

Resultado: Argument list too long - El comando retornó demasiados resultados.
Intento 2: Lectura de directorios restringidos
bash

./useless add "$(ls -la /root)" 5

Resultado: Permission denied + The Sum is: 5 - Sin permisos para acceder.
Intento 3: Enumeración de permisos sudo
bash

./useless add "$(sudo -l)" 5

Resultado: sudo: command not found - Sudo no instalado en el contenedor.
Intento 4: Variable de entorno FLAG
bash

./useless add $FLAG 5

Resultado: Read the code first - La variable estaba vacía (solo pasó 2 argumentos).
bash

./useless add "$(echo $FLAG)" 5

Resultado: The Sum is: 5 - Variable FLAG vacía.
Intento 5: Lectura de archivos locales
bash

./useless add "$(>/flag.txt)" 5

Resultado: Permission denied para /flag.txt
bash

./useless add "$(<flag.txt)" 5

Resultado: No such file or directory en directorio actual
bash

./useless add "$(</root)" 5

Resultado: Permission denied para /root
Intento 6: Búsqueda controlada de flags
bash

./useless add "$(find / -name "flag*" -type f 2>/dev/null | head -20)" 5

Resultado: Error de sintaxis - El comando retornó múltiples líneas que rompieron la evaluación aritmética:
text

/usr/lib/ruby/3.0.0/rubygems/commands/sources_command.rb:          @flags = [:url, :type]
/usr/lib/ruby/3.0.0/rubygems/commands/sources_command.rb:          @flags = [:url, :type]
/usr/lib/ruby/3.0.0/rubygems/commands/sources_command.rb:          @flags = [:url, :type]

💡 3. Interpretación de Pistas

Analizando los mensajes del script:

    "Read the code first" → Ya leímos el código, no hay nada oculto

    "Read the manual" → ¡Esta es la pista clave!

En sistemas Unix/Linux, los comandos suelen tener páginas de manual accesibles con el comando man. Aunque useless es un script personalizado, podría tener una página de manual instalada en el sistema.
🎯 4. Solución

Ejecutamos el comando man sobre el script:
bash

picoplayer@challenge:~$ man useless

Resultado:
text

useless
     useless, — This is a simple calculator script

SYNOPSIS
     useless, [add sub mul div] number1 number2

DESCRIPTION
     Use the useless, macro to make simple calulations like addition,
     subtraction, multiplication and division.

Examples
     ./useless add 1 2
       This will add 1 and 2 and return 3

     ./useless mul 2 3
       This will return 6 as a product of 2 and 3

     ./useless div 6 3
       This will return 2 as a quotient of 6 and 3

     ./useless sub 6 5
       This will return 1 as a remainder of substraction of 5 from 6

Authors
     This script was designed and developed by Cylab Africa

     picoCTF{******************************}


📚 5. Lecciones Aprendidas

    Las pistas pueden ser muy literales: "Read the manual" significaba literalmente leer la página de manual del sistema

    No todo requiere explotación compleja: Aunque intentamos inyección de comandos y enumeración del sistema, la solución era más simple

    Exploración de documentación: En CTFs, la documentación del sistema (man, info, help) a veces contiene información valiosa

    Persistencia metódica: Los intentos fallidos de inyección nos ayudaron a descartar vectores de ataque y concentrarnos en la pista correcta
