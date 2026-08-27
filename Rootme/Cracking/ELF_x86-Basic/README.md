🧩 Reto Root‑me – ELF x86 - Basic

Autor: g0uZ
Dificultad: 1/5
Puntos: 5
Objetivo: Encontrar la contraseña de validación a partir del binario proporcionado.
📁 Preparación

Disponemos del binario ch2.bin. Se trata de un ejecutable ELF para arquitectura x86, sin protección aparente (no está ofuscado ni empaquetado). Comenzamos el análisis con las herramientas clásicas de Linux.
🔍 1. Inspección rápida con strings

Ejecutamos strings con longitud mínima de 6 caracteres para filtrar ruido y observar cadenas legibles:
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Cracking/ELF_x86-Basic]
└─# strings -n 6 ch2.bin

Entre la abundante salida (procedente de la librería estándar y del propio programa), destacan estas líneas:
text

...
***************
############################################################
##        Bienvennue dans ce challenge de cracking        ##
############################################################
username: 
password: 
***************
Bien joue, vous pouvez valider l'epreuve avec le mot de passe : %s !
Bad password
Bad username
...

Ya tenemos tres candidatas:

    ***********

    ***********

    username / password (indicadores)

Con esto podemos intuir que el programa pide credenciales y, si son correctas, muestra la contraseña de validación. Pero aún no sabemos qué combinación funciona.
🧬 2. Análisis estático con objdump

Extraemos el código ensamblador de la función main para entender la lógica de comparación:
bash

objdump -d -M intel ch2.bin | grep -A 50 "<main>:"

Fragmento relevante:
asm

08048309 <main>:
  ...
  804831a:       c7 45 f4 19 6b 0a 08    mov    DWORD PTR [ebp-0xc],0x80a6b19
  8048321:       c7 45 f0 1e 6b 0a 08    mov    DWORD PTR [ebp-0x10],0x80a6b1e
  ...
  8048358:       8b 45 f8                mov    eax,DWORD PTR [ebp-0x8]
  804835b:       89 04 24                mov    DWORD PTR [esp],eax
  804835e:       e8 07 ff ff ff          call   804826a <getString>
  8048363:       89 45 f8                mov    DWORD PTR [ebp-0x8],eax
  8048366:       8b 45 f4                mov    eax,DWORD PTR [ebp-0xc]
  8048369:       89 44 24 04             mov    DWORD PTR [esp+0x4],eax
  804836d:       8b 45 f8                mov    eax,DWORD PTR [ebp-0x8]
  8048370:       89 04 24                mov    DWORD PTR [esp],eax
  8048373:       e8 78 7f 00 00          call   80502f0 <strcmp>
  8048378:       85 c0                   test   eax,eax
  804837a:       75 54                   jne    80483d0 <main+0xc7>     ; salta si no coincide
  ...
  804839d:       8b 45 f8                mov    eax,DWORD PTR [ebp-0x8]
  80483a0:       89 04 24                mov    DWORD PTR [esp],eax
  80483a3:       e8 48 7f 00 00          call   80502f0 <strcmp>
  80483a8:       85 c0                   test   eax,eax
  80483aa:       75 16                   jne    80483c2 <main+0xb9>     ; salta si no coincide
  ...
  80483ac:       c7 44 24 04 00 6c 0a    mov    DWORD PTR [esp+0x4],0x80a6c00
  80483b3:       08

Observamos:

    La primera comparación (dirección 0x8048373) enfrenta la entrada del usuario con la cadena almacenada en 0x80a6b19.

    Si falla, salta a Bad username.

    Si acierta, pide una segunda entrada y la compara (dirección 0x80483a3) con la cadena de 0x80a6b1e.

    Si ambas coinciden, se imprime el mensaje de éxito utilizando la cadena de 0x80a6c00.

🧠 3. Decompilación con Ghidra

Cargamos el binario en Ghidra y localizamos la función main. La decompilación resultante es cristalina:
c

undefined4 main(void)
{
  char *pcVar1;
  int iVar2;
  undefined4 local_10;
  
  puts("############################################################");
  puts("##        Bienvennue dans ce challenge de cracking        ##");
  puts("############################################################\n");
  printf("username: ");
  pcVar1 = (char *)getString(local_10);
  iVar2 = strcmp(pcVar1,"**************");   // usuario correcto
  if (iVar2 == 0) {
    printf("password: ");
    pcVar1 = (char *)getString(pcVar1);
    iVar2 = strcmp(pcVar1,"**************"); // contraseña de acceso
    if (iVar2 == 0) {
      printf("Bien joue, vous pouvez valider l'epreuve avec le mot de passe : %s !\n",
             "**************");              // contraseña de validación
    }
    else {
      puts("Bad password");
    }
  }
  else {
    puts("Bad username");
  }
  return 0;
}

Confirmación:

    El usuario correcto es **************.

    La contraseña de acceso (la que pide el programa) es **************.

    La contraseña de validación (la que se muestra al final y hay que introducir en la web) es **************.

🖥️ 4. Ejecución y verificación final

Probamos el binario con las credenciales halladas:
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Cracking/ELF_x86-Basic]
└─# ./ch2.bin
############################################################
##        Bienvennue dans ce challenge de cracking        ##
############################################################

username: **************
password: **************
Bien joue, vous pouvez valider l'epreuve avec le mot de passe : ************** !

El programa confirma el éxito y muestra la contraseña de validación.
📝 Conclusión
Campo	Valor encontrado
Usuario (username)	**************
Contraseña de acceso	**************
Contraseña de validación	**************

La contraseña que debemos introducir en la plataforma Root‑me para obtener los puntos es:
**************
🧰 Herramientas utilizadas

    strings – para extraer cadenas legibles.

    objdump – para inspeccionar el ensamblador.

    Ghidra – para obtener una decompilación clara.

    Ejecución directa – para validar el resultado.

💡 Lección aprendida

En retos de cracking básico, el simple uso de strings suele ser suficiente para encontrar pistas, pero es fundamental combinar herramientas de análisis estático (desensamblador y decompilador) para comprender la lógica del programa y confirmar las credenciales. La ejecución final da la certeza definitiva.
