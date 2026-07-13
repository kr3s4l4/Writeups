MultiCode - Writeup
Información General

    Categoría: General Skills

    Dificultad: Easy

    Puntos: 200

    Evento: picoCTF 2026

    Autor: Yahaya Meddy

Descripción del Reto

    We intercepted a suspiciously encoded message, but it's clearly hiding a flag. No encryption, just multiple layers of obfuscation. Can you peel back the layers and reveal the truth?

Archivo Proporcionado

    message.txt - Archivo con el mensaje codificado

Proceso de Resolución
Paso 1: Inspección Inicial

Primero, examinamos el contenido del archivo:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/easy/MultiCode]
└─# cat message.txt 
NjM3NjcwNjI1MDQ3NTMyNTM3NDI2MTcyNjY2NzcyNzE1ZjcyNjE3MDMwNzE3NjYxNzQ1ZjMxNzEzNzM1NmY3MjM2MzMyNTM3NDQ=

El mensaje parece estar en Base64, identificable por:

    Caracteres alfanuméricos

    Termina con = (padding)

    Longitud múltiplo de 4

Paso 2: Primera Decodificación - Base64

Decodificamos la primera capa:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/easy/MultiCode]
└─# cat message.txt | base64 -d
637670625047532537426172666772715f72617030717661745f317137356f723633253744

Resultado: 637670625047532537426172666772715f72617030717661745f317137356f723633253744
Paso 3: Identificación - Hexadecimal

Observamos que la salida contiene solo dígitos y letras a-f, lo que indica codificación hexadecimal. La presencia de 253744 sugiere que algunos caracteres están URL-encoded.
Paso 4: Segunda Decodificación - Hexadecimal

Decodificamos el hexadecimal a texto ASCII:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/easy/MultiCode]
└─# cat message.txt | base64 -d | xxd -r -p
cvpbPGS%7Barfgrq_rap0qvat_1q75or63%7D

Resultado: cvpbPGS%7Barfgrq_rap0qvat_1q75or63%7D
Paso 5: Identificación - URL Encoding

Observamos:

    %7B → { (llave de apertura)

    %7D → } (llave de cierre)

    El formato parece una bandera de picoCTF: cvpbPGS{...}

Paso 6: Tercera Decodificación - URL Encoding

Decodificamos los caracteres URL-encoded:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/easy/MultiCode]
└─# cat message.txt | base64 -d | xxd -r -p | sed 's/%7B/{/g; s/%7D/}/g'
cvpbPGS{arfgrq_rap0qvat_1q75or63}

Resultado: cvpbPGS{arfgrq_rap0qvat_1q75or63}
Paso 7: Identificación - ROT13

Observamos:

    cvpbPGS es ROT13 de picoCTF (patrón conocido en CTFs)

    El contenido parece estar cifrado con ROT13

Paso 8: Cuarta Decodificación - ROT13

Aplicamos ROT13 al texto:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/easy/MultiCode]
└─# cat message.txt | base64 -d | xxd -r -p | sed 's/%7B/{/g; s/%7D/}/g' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
picoCTF{*******************************}

Resultado Final: picoCTF{nested_enc0ding_1d75be63} ✅
Resumen de Capas de Codificación
Capa	Codificación	Herramienta	Resultado Parcial
1	Base64		base64 -d	63767062504753253742...
2	Hexadecimal	xxd -r -p	cvpbPGS%7Barfgrq_...
3	URL Encoding	sed		cvpbPGS{arfgrq_rap0qvat_...}
4	ROT13		tr		picoCTF{******************************}
Comando Unificado (One-Liner)

Para obtener la bandera en un solo comando:
bash

cat message.txt | base64 -d | xxd -r -p | sed 's/%7B/{/g; s/%7D/}/g' | tr 'A-Za-z' 'N-ZA-Mn-za-m'

Herramientas Utilizadas

    base64 - Decodificación Base64

    xxd - Conversión hexadecimal a texto

    sed - Reemplazo de caracteres URL-encoded

    tr - Transformación ROT13

Lecciones Aprendidas

    Identificar codificaciones comunes:

        Base64: caracteres alfanuméricos + =

        Hexadecimal: solo 0-9 y A-F

        URL Encoding: %XX donde XX es hexadecimal

        ROT13: cifrado César con desplazamiento 13

    Patrones reconocibles:

        cvpbPGS → picoCTF en ROT13 (muy común en picoCTF)

        Formato de bandera: picoCTF{...}

    Enfoque metodológico:

        Decodificar capa por capa

        Identificar cada formato antes de decodificar

        Verificar resultados parciales

Referencias

    Base64

    Hexadecimal

    URL Encoding

    ROT13
