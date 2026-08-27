Writeup Técnico: ELF C++ - 0 protection (Root-Me)

1. Descripción del reto

El binario proporcionado es un ejecutable ELF de 32 bits compilado en C++ sin protección alguna. Su objetivo es validar una contraseña introducida como argumento en la línea de comandos. La respuesta esperada no es visible mediante un simple volcado de cadenas, lo que indica la presencia de ofuscación de datos.

2. Análisis inicial

Al ejecutar el binario sin argumentos, se muestra el mensaje de uso:
text

usage : ./ch25.bin password

Al proporcionar una cadena incorrecta, se obtiene:
text

Password incorrect.

Estos mensajes, junto con otros como Bravo, tu peux valider..., aparecen en la salida de strings, pero la contraseña en texto claro no se encuentra en el binario. Se deduce que la contraseña está ofuscada y se descifra durante la ejecución.

3. Análisis estático con Ghidra

El binario se abre en Ghidra para su desensamblado y descompilación. La función main presenta la siguiente estructura (simplificada):
c

undefined4 main(int param_1, undefined4 *param_2) {
    // ...
    if (param_1 < 2) {
        // Muestra "usage : ./ch25.bin password"
    } else {
        // Construcción de dos strings desde direcciones fijas
        std::string::string(local_14, &DAT_08048dc4, &local_1d);
        std::string::string(local_18, &DAT_08048dcc, &local_1e);
        plouf(local_1c, local_18, local_14);
        bVar2 = std::operator==(local_1c, (char *)param_2[1]);
        if (bVar2) {
            // Mensaje de éxito
        } else {
            // Password incorrecta
        }
    }
}

Se observa que dos cadenas se construyen a partir de las direcciones 0x08048dc4 y 0x08048dcc. Estas se pasan a la función plouf, cuyo resultado se compara con el argumento proporcionado. Esto sugiere que plouf realiza una transformación sobre los datos para obtener la contraseña.

4. Estudio de la función plouf

La función plouf se encuentra en la dirección 0x0804898d (etiqueta _Z5ploufSsSs). Su descompilación es la siguiente:
c

string * plouf(string *param_1, uint param_2, uint param_3) {
    byte bVar1;
    byte *pbVar2;
    // ...
    local_20 = 0;
    while( true ) {
        pcVar3 = (char *)std::string::operator[](param_2);
        if (*pcVar3 == '\0') break;
        pbVar2 = (byte *)std::string::operator[](param_2);
        bVar1 = *pbVar2;
        std::string::length();
        pbVar2 = (byte *)std::string::operator[](param_3);
        std::string::operator+=(param_1, *pbVar2 ^ bVar1);
        local_20 = local_20 + 1;
    }
    return param_1;
}

La línea clave es:
c

std::string::operator+=(param_1, *pbVar2 ^ bVar1);

El operador ^ en C++ corresponde a la operación XOR (OR exclusivo). Por tanto, la función itera sobre la cadena param_2 (la primera cadena, que se construye desde 0x08048dcc) y para cada byte, lo combina mediante XOR con el byte correspondiente de param_3 (la segunda cadena, desde 0x08048dc4). El índice en param_3 se calcula como i % longitud(param_3), es decir, se repite cíclicamente.

En el ensamblador, esta operación se materializa en la instrucción xor. En particular, en la dirección 0x08048a13 se encuentra:
assembly

8048a13:       31 f0                   xor    %esi,%eax

Esto confirma que la ofuscación consiste en un XOR simple entre dos bloques de datos.

5. Extracción de los datos ofuscados

Las dos cadenas mencionadas se almacenan en la sección .rodata del binario. Sus contenidos se extraen directamente desde las direcciones indicadas.
5.1. Clave (desde 0x08048dc4)

Los bytes presentes en esta dirección son:
text

18 d6 15 ca fa 77 00

Se trata de una clave de 6 bytes (sin contar el terminador nulo), que será utilizada de forma repetitiva.
5.2. Datos ofuscados (desde 0x08048dcc)

En esta dirección se encuentra un bloque de 48 bytes antes del terminador nulo:
text

50 b3 67 af a5 0e 77 a3 4a a2 9b 01 7d 89 61 a5
a5 02 76 b2 70 b8 89 03 79 b8 71 95 9b 28 74 bf
61 be 96 12 47 95 3e e1 a5 04 6c a3 73 ac 89 00

Estos son los datos que serán transformados mediante XOR con la clave.

6. Operación XOR

El XOR es una operación binaria que toma dos bits y devuelve 1 si son diferentes, 0 si son iguales. A nivel de bytes, la operación se aplica bit a bit. En este caso, la transformación es:
text

resultado[i] = datos[i] XOR clave[i % 6]

Donde i recorre desde 0 hasta 47 (longitud de los datos menos 1). La clave se repite cada 6 bytes.

A continuación se muestra un ejemplo con los primeros bytes:
i	datos (hex)	clave (hex)	XOR (hex)	carácter
0	50		18		48		'H'
1	b3		d6		65		'e'
2	67		15		72		'r'
3	af		ca		65		'e'
4	a5		fa		5f		'_'
5	0e		77		79		'y'
6	77		18		6f		'o'
...	...		...		...		...

La secuencia completa de resultados da lugar a una cadena ASCII inteligible.

7. Recuperación mediante script

Para automatizar la operación, se puede emplear un script en Python que lea los bytes extraídos y aplique el XOR:
python

datos = bytes.fromhex(
    "50 b3 67 af a5 0e 77 a3 4a a2 9b 01 7d 89 61 a5 "
    "a5 02 76 b2 70 b8 89 03 79 b8 71 95 9b 28 74 bf "
    "61 be 96 12 47 95 3e e1 a5 04 6c a3 73 ac 89"
)
clave = bytes.fromhex("18 d6 15 ca fa 77")

resultado = bytes(datos[i] ^ clave[i % len(clave)] for i in range(len(datos)))
print(resultado.decode())

La ejecución de este script devuelve una cadena, que es la contraseña buscada. Dicha cadena se ha omitido por razones obvias, pero se corresponde con la que se valida en el siguiente paso.

8. Validación

Se comprueba la contraseña obtenida con el binario original. La contraseña, que por razones de confidencialidad se representa como *****************************, es aceptada por el programa, que responde con el mensaje de éxito:
text

Bravo, tu peux valider en utilisant ce mot de passe...
Congratz. You can validate with this password...

9. Conclusiones

El reto se resuelve mediante un análisis estático que revela que la contraseña se genera a partir de una operación XOR entre dos bloques de datos almacenados en la sección .rodata. El XOR se aplica en la función plouf, tanto a nivel de código fuente (operador ^) como a nivel de ensamblador (instrucción xor). Extraídos los bytes, la recuperación es inmediata.

Este tipo de ofuscación es muy común en retos de cracking sin protecciones, y demuestra que el simple volcado de cadenas no es suficiente cuando los datos están ofuscados. Con herramientas de análisis estático como Ghidra y un poco de lógica, se puede revertir la ofuscación sin necesidad de ejecutar el binario.
