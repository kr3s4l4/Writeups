Writeup: Reto "PE x86 - 0 protection" (Root-me)

1. Descripción del reto

    Plataforma: Root-me

    Categoría: Cracking / Reverse Engineering

    Archivo: ch15.exe (PE ejecutable de Windows, 32 bits)

    Objetivo: Recuperar la contraseña para validar el desafío.

    Dificultad: Baja (7% de resoluciones, 1007 votos).

El binario pide una contraseña por argumento de línea de comandos y muestra "Gratz man :)" si es correcta, o "Wrong password" en caso contrario.

2. Herramientas utilizadas

    strings (Linux) – para extraer cadenas legibles.

    objdump (Linux) – para inspeccionar secciones y desensamblar.

    Ghidra – descompilador y analizador estático.

    Wine (opcional) – para ejecutar el binario en Linux y verificar.

3. Análisis estático inicial
3.1. Extracción de cadenas con strings

Primero, echamos un vistazo rápido al binario para ver si encontramos pistas:
bash

strings -n 6 ch15.exe

Salida relevante:
text

!This program cannot be run in DOS mode.
...
Usage: %s pass
Gratz man :)
Wrong password
...

Observamos tres cadenas clave: el mensaje de uso, el de éxito y el de error. La cadena "pass" en el mensaje de uso podría ser la contraseña, pero debemos confirmar.
3.2. Búsqueda de cadenas más cortas

Como las contraseñas pueden tener menos de 6 caracteres, repetimos con -n 1:
bash

strings -n 1 ch15.exe | grep -i pass

Salida:
text

Usage: %s pass
...
pass

Aparece una cadena aislada "pass". Podría ser la clave, pero también podría ser un valor por defecto. Necesitamos más contexto.

4. Desensamblado con objdump

Para localizar la función principal, usamos objdump:
bash

objdump -d ch15.exe | grep -A 20 -i main

No aparece un símbolo main claramente, pero vemos referencias a las cadenas. También podemos buscar la dirección de "Gratz man :)":
bash

objdump -s -j .rdata ch15.exe | grep -A 5 -i "Gratz"

Esto nos confirma la ubicación de las cadenas en la sección .rdata.

5. Análisis con Ghidra

Abrimos el binario en Ghidra (o cualquier otro desensamblador/decompilador).
5.1. Localización de las cadenas

En la ventana de Listing (o Symbol Tree), buscamos la cadena "Gratz man :)". Ghidra la muestra en la dirección 0x00404053:
text

s_Gratz_man_:)_00404053   XREF[2]: FUN_00401726:00401791(*), FUN_00401726:00401796(*)

Esto indica que la cadena es referenciada desde la función FUN_00401726.
5.2. Análisis de la función de validación

Saltamos a FUN_00401726 y vemos su descompilado en C (pulsando Ctrl+E). El código es el siguiente:
c
void FUN_00401726(char *param_1, int param_2)
{
  if (((((param_2 == 7) && (*param_1 == 'S')) && (param_1[1] == 'P')) &&
      ((param_1[2] == '*' && (param_1[3] == '*')))) &&
     ((param_1[4] == '*' && ((param_1[5] == '*' && (param_1[6] == '*')))))) {
    printf("Gratz man :)");
    exit(0);
  }
  puts("Wrong password");
  return;
}

Interpretación:

    param_2 es el número de argumentos (debe ser 7? En realidad, argc debe ser 2, pero el código comprueba param_2 == 7 – esto es un error de análisis de Ghidra, probablemente está mal interpretando el tipo; lo que realmente comprueba es la longitud de la cadena, que es 7).

    La contraseña se valida carácter por carácter:

        Longitud = 7.

        Carácter 0: '*'

        Carácter 1: '*'

        Carácter 2: '*'

        Carácter 3: '*'

        Carácter 4: '*

        Carácter 5: '*

        Carácter 6: '*

Por lo tanto, la contraseña es *********.

6. Verificación con Wine

Para confirmar, ejecutamos el binario con Wine (en Linux). Primero, creamos un prefijo de 32 bits para evitar problemas de arquitectura:
bash

WINEARCH=win32 WINEPREFIX=~/.wine32 wine ch15.exe

Esto muestra el mensaje de uso:
text

Usage: Z:\...\ch15.exe pass

Ahora, probamos con la contraseña hallada:
bash

WINEARCH=win32 WINEPREFIX=~/.wine32 wine ch15.exe *********

Salida:
text

Gratz man :)

¡Correcto! La contraseña es efectivamente *********.

7. Validación en Root-me

Introducimos la cadena ********* en el campo de validación del reto y obtenemos los puntos.

8. Conclusión

El reto "PE x86 - 0 protection" es un ejercicio de reversing sencillo que consiste en encontrar una contraseña almacenada en texto claro dentro del binario. Con herramientas básicas como strings y un descompilador como Ghidra, se puede extraer la clave en pocos minutos. La contraseña es ********.

9. Anexo: Capturas de pantalla (simuladas)

    Cadenas extraídas con strings:

text

┌──(root㉿kali)-[...] 
└─# strings -n 6 ch15.exe
...
Usage: %s pass
Gratz man :)
Wrong password

    Descompilado en Ghidra – muestra la comparación carácter por carácter.

    Ejecución con Wine – mensaje de éxito.

10. Apéndice: Comandos útiles para futuros retos

    strings -n <longitud> <archivo> – extraer cadenas de longitud mínima.

    objdump -s -j .rdata <archivo> – ver la sección de datos de solo lectura.

    objdump -d <archivo> | grep -A 10 <cadena> – buscar una cadena en el desensamblado.

    Ghidra: abrir el binario, buscar referencias a cadenas, analizar la función que las usa.

    Wine: WINEARCH=win32 WINEPREFIX=~/.wine32 wine <archivo> <argumentos>
