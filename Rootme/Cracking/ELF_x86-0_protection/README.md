Writeup Detallado: Reto "ELF x86 - 0 protection" (Root-Me)

Autor: [Tu nombre]
Fecha: 2026-08-24
Archivo: ch1.bin
Puntos: 5
Categoría: Cracking / Ingeniería Inversa
1. Descripción del reto

Se nos proporciona un binario ELF de 32 bits, compilado en C, sin protecciones (no PIE, no NX, no canaries). El objetivo es encontrar la contraseña que hace que el programa muestre el mensaje de éxito.
2. Reconocimiento inicial
2.1. Identificar el tipo de archivo
bash

file ch1.bin

Salida:
text

ch1.bin: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=..., not stripped

    ELF 32-bit: binario ejecutable de 32 bits.

    not stripped: conserva símbolos (nombres de funciones), lo que facilita el análisis.

2.2. Buscar cadenas legibles con strings

Usamos strings -n 6 para mostrar cadenas de al menos 6 caracteres y así filtrar ruido:
bash

strings -n 6 ch1.bin

Salida (fragmentos relevantes):
text

/lib/ld-linux.so.2
__gmon_start__
libc.so.6
_IO_stdin_used
realloc
getchar
__errno_location
malloc
stderr
fprintf
strcmp
strerror
__libc_start_main
GLIBC_2.0
%s : "%s"
Allocating memory
Reallocating memory
***********
############################################################
##        Bienvennue dans ce challenge de cracking        ##
############################################################
Veuillez entrer le mot de passe : 
Bien joue, vous pouvez valider l'epreuve avec le pass : %s!
Dommage, essaye encore une fois.
GCC: (GNU) 4.1.2 (Gentoo 4.1.2 p1.0.2)
...

La cadena *********** aparece de forma clara entre las cadenas legibles, lo que sugiere que podría ser la contraseña. Además, vemos nombres de funciones como realloc, getchar, malloc, strcmp, printf, puts y getString, que nos darán pistas sobre el funcionamiento interno.
3. Análisis estático con objdump
3.1. Desensamblado completo

Exportamos el desensamblado completo a un archivo de texto para buscar fácilmente la función main y las instrucciones relevantes:
bash

objdump -d -M intel ch1.bin > ch1.asm

    -d : desensambla las secciones ejecutables.

    -M intel : usa sintaxis Intel (más legible).

3.2. Localizar la función main

Buscamos la etiqueta <main> en el archivo:
bash

grep -n "^[0-9a-f]* <main>:" ch1.asm

Salida:
text

233:0804869d <main>:

Abrimos el archivo en la línea 233 (o usamos sed -n '233,300p' ch1.asm) y vemos el desensamblado de main:
assembly

0804869d <main>:
 804869d:       8d 4c 24 04             lea    ecx,[esp+0x4]
 80486a1:       83 e4 f0                and    esp,0xfffffff0
 80486a4:       ff 71 fc                push   DWORD PTR [ecx-0x4]
 80486a7:       55                      push   ebp
 80486a8:       89 e5                   mov    ebp,esp
 80486aa:       51                      push   ecx
 80486ab:       83 ec 24                sub    esp,0x24
 80486ae:       c7 45 f8 41 88 04 08    mov    DWORD PTR [ebp-0x8],0x8048841
 80486b5:       c7 04 24 4c 88 04 08    mov    DWORD PTR [esp],0x804884c
 80486bc:       e8 07 fe ff ff          call   80484c8 <puts@plt>
 80486c1:       c7 04 24 8c 88 04 08    mov    DWORD PTR [esp],0x804888c
 80486c8:       e8 fb fd ff ff          call   80484c8 <puts@plt>
 80486cd:       c7 04 24 cc 88 04 08    mov    DWORD PTR [esp],0x80488cc
 80486d4:       e8 ef fd ff ff          call   80484c8 <puts@plt>
 80486d9:       c7 04 24 0c 89 04 08    mov    DWORD PTR [esp],0x804890c
 80486e0:       e8 b3 fd ff ff          call   8048498 <printf@plt>
 80486e5:       8b 45 f4                mov    eax,DWORD PTR [ebp-0xc]
 80486e8:       89 04 24                mov    DWORD PTR [esp],eax
 80486eb:       e8 0e ff ff ff          call   80485fe <getString>
 80486f0:       89 45 f4                mov    DWORD PTR [ebp-0xc],eax
 80486f3:       8b 45 f8                mov    eax,DWORD PTR [ebp-0x8]
 80486f6:       89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 80486fa:       8b 45 f4                mov    eax,DWORD PTR [ebp-0xc]
 80486fd:       89 04 24                mov    DWORD PTR [esp],eax
 8048700:       e8 d3 fd ff ff          call   80484d8 <strcmp@plt>
 8048705:       85 c0                   test   eax,eax
 8048707:       75 15                   jne    804871e <main+0x81>
 8048709:       8b 45 f8                mov    eax,DWORD PTR [ebp-0x8]
 804870c:       89 44 24 04             mov    DWORD PTR [esp+0x4],eax
 8048710:       c7 04 24 30 89 04 08    mov    DWORD PTR [esp],0x8048930
 8048717:       e8 7c fd ff ff          call   8048498 <printf@plt>
 804871c:       eb 0c                   jmp    804872a <main+0x8d>
 804871e:       c7 04 24 70 89 04 08    mov    DWORD PTR [esp],0x8048970
 8048725:       e8 9e fd ff ff          call   80484c8 <puts@plt>
 804872a:       b8 00 00 00 00          mov    eax,0x0
 804872f:       83 c4 24                add    esp,0x24

3.3. Identificación de instrucciones clave

    Almacenamiento de la cadena correcta:
    En 0x80486ae se mueve 0x8048841 a [ebp-0x8]. Esta dirección contiene la contraseña.

    Lectura de entrada:
    En 0x80486eb se llama a getString, una función definida en el binario que lee la entrada del usuario y devuelve un puntero a la cadena (almacenado en [ebp-0xc]).

    Comparación:
    En 0x8048700 se llama a strcmp, con la entrada del usuario como primer argumento y la cadena de 0x8048841 como segundo.

    Salto condicional:
    Después de strcmp, test eax,eax y jne 804871e. Si strcmp devuelve 0 (iguales), no se salta y se ejecuta el bloque de éxito; en caso contrario, se salta al bloque de error.

4. Análisis con Ghidra (paso a paso)
4.1. Abrir el binario en Ghidra

    Iniciamos Ghidra y creamos un nuevo proyecto (File → New Project).

    Importamos el binario ch1.bin (File → Import File).

    Ghidra nos pedirá que analicemos el binario. Aceptamos las opciones por defecto y ejecutamos el análisis (Analysis → Auto Analyze).

4.2. Localizar la función main

En la ventana Symbol Tree (izquierda), desplegamos Functions y hacemos doble clic sobre main. También podemos buscarlo con la lupa.
4.3. Examinar el desensamblado y el decompilado

En el Listing vemos el mismo código que en objdump. Además, si tenemos abierta la ventana de Decompile, Ghidra muestra una versión en pseudocódigo C:
c

undefined4 main(void)
{
  char *pcVar1;
  char *password;
  
  password = "***********";
  puts("############################################################");
  puts("##        Bienvennue dans ce challenge de cracking        ##");
  puts("############################################################");
  printf("Veuillez entrer le mot de passe : ");
  pcVar1 = getString();
  if (strcmp(pcVar1, password) == 0) {
    printf("Bien joue, vous pouvez valider l'epreuve avec le pass : %s!\n", password);
  }
  else {
    puts("Dommage, essaye encore une fois.");
  }
  return 0;
}

Esto confirma inmediatamente que la contraseña es "***********".
4.4. Ir a la dirección exacta de la cadena

Para ver la cadena en el Listing:

    Pulsamos la tecla G (Go to) y escribimos 0x08048841.

    Pulsamos Enter. La vista se desplaza a esa dirección.

Veremos algo como:
text

                             s_***********_08048841                     XREF[3]:     main:080486ae(*), 
                                                                                          main:080486f6(*), 
                                                                                          main:0804870c(*)  
        08048841 2a 2a 2a        ds         "***********"
                 2a 2a 2a 
                 2a 2a 00

Ghidra ha interpretado los bytes como una cadena ASCII. Si solo se muestran bytes hexadecimales, hacemos clic derecho y seleccionamos Data → String → char.
4.5. Usar la ventana Defined Strings

Otra forma rápida: ir a Window → Defined Strings, buscar en la columna de dirección 08048841, hacer doble clic y Ghidra nos llevará directamente a la cadena.
5. Análisis dinámico con ltrace

Para confirmar el comportamiento en tiempo real, usamos ltrace, que rastrea las llamadas a funciones de biblioteca:
bash

ltrace ./ch1.bin

Introducimos *********** cuando se pide la contraseña. Salida (fragmento relevante):
text

printf("Veuillez entrer le mot de passe "...) = 34
malloc(2)                                                              = 0x9f525f0
getchar(2, 0xf7fc7c60, 0xffe51588, 0xf7d84b55)                         = 42   // '*' en ASCII
realloc(0x9f525f0, 2)                                                  = 0x9f525f0
getchar(0x9f525f0, 2, 0xffe51588, 0xf7d84b55)                         = 42
realloc(0x9f525f0, 3)                                                  = 0x9f525f0
getchar(0x9f525f0, 3, 0xffe51588, 0xf7d84b55)                         = 42
...
strcmp("***********", "***********")                                   = 0
printf("Bien joue, vous pouvez valider l"...Bien joue, vous pouvez valider l'epreuve avec le pass : ***********!
)                          = 67

Observamos que el programa:

    Usa malloc y realloc para construir la cadena de entrada dinámicamente.

    Lee carácter a carácter con getchar.

    Llama a strcmp y, al devolver 0, muestra el mensaje de éxito.

6. Solución

La contraseña es:
text

***********

Al ejecutar el binario e introducirla, obtenemos:
bash

Bien joue, vous pouvez valider l'epreuve avec le pass : ***********!

El reto se da por superado.
7. Resumen de comandos y herramientas utilizadas
Comando / Herramienta	Propósito
file ch1.bin	Identificar tipo de archivo y arquitectura.
strings -n 6 ch1.bin	Extraer cadenas legibles de al menos 6 caracteres.
objdump -d -M intel ch1.bin > ch1.asm	Desensamblar y guardar en un archivo de texto.
grep -n "<main>:" ch1.asm	Localizar la función main en el desensamblado.
Ghidra	Análisis estático avanzado: descompilación, gráficos de flujo, búsqueda de cadenas.
ltrace ./ch1.bin	Rastrear llamadas a bibliotecas en tiempo real.
8. Explicación de la función getString

Aunque no es necesario para resolver el reto, entender cómo funciona la entrada es interesante. La función getString (dirección 0x80485fe) utiliza:

    malloc(1) para reservar un byte inicial (terminador nulo).

    Un bucle que llama a getchar para leer un carácter.

    realloc para aumentar el tamaño del buffer en 1 cada vez.

    Almacena el carácter leído y añade el \0 al final.

    Termina al leer \n (salto de línea) o EOF.

Esto es equivalente a un scanf dinámico sin límite de longitud, lo que permite entradas de cualquier tamaño.
9. Conclusión

El reto está diseñado para ser muy accesible y enseña técnicas fundamentales de cracking:

    Análisis estático con strings, objdump y desensambladores (Ghidra).

    Análisis dinámico con ltrace para ver la comparación en tiempo real.

    Identificación de la lógica de comparación (strcmp, saltos condicionales).

    Extracción de cadenas desde direcciones de memoria del binario.
