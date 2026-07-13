Writeup: Secret of the Polyglot - picoCTF
📋 Información General

    Reto: Secret of the Polyglot

    Categoría: Forensics

    Dificultad: Fácil/Media

    Herramientas utilizadas: binwalk, dd, python3, strings, xdg-open, file

📝 Descripción del Reto

El reto nos proporciona un archivo llamado flag2of2-final.pdf que, según el enunciado, contiene la bandera pero está "oculta". El nombre del reto ("Polyglot") nos da una pista importante: el archivo puede ser válido en múltiples formatos simultáneamente.
🔍 Reconocimiento Inicial
Paso 1: Identificar el tipo de archivo

Primero, verificamos qué tipo de archivo tenemos usando el comando file:
bash

file flag2of2-final.pdf

Salida:
text

flag2of2-final.pdf: PNG image data, 50 x 50, 8-bit/color RGBA, non-interlaced

Observación: A pesar de tener extensión .pdf, el archivo es en realidad una imagen PNG. Esto confirma que estamos ante un archivo políglota.
Paso 2: Escanear la estructura interna

Usamos binwalk para analizar la estructura interna del archivo:
bash

binwalk flag2of2-final.pdf

Salida:
text

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 50 x 50, 8-bit/color RGBA, non-interlaced
914           0x392           PDF document, version: "1.4"
1149          0x47D           Zlib compressed data, default compression

Análisis: El archivo contiene tres partes:

    Offset 0: Imagen PNG (50x50 píxeles)

    Offset 914: Documento PDF (versión 1.4)

    Offset 1149: Datos comprimidos con Zlib

🛠️ Extracción de la Primera Parte (PNG)
Paso 3: Extraer la imagen PNG

Basándonos en el análisis de binwalk, la imagen PNG ocupa los primeros 914 bytes (desde el offset 0 hasta el 913). Extraemos esta parte:
bash

dd if=flag2of2-final.pdf of=flag_correcta.png bs=1 count=914

Salida:
text

914+0 records in
914+0 records out
914 bytes copied, 0.00117473 s, 778 kB/s

Paso 4: Verificar la imagen extraída
bash

file flag_correcta.png

Salida:
text

flag_correcta.png: PNG image data, 50 x 50, 8-bit/color RGBA, non-interlaced

Paso 5: Visualizar la imagen
bash

xdg-open flag_correcta.png

Resultado: La imagen muestra la primera parte de la bandera:

https://flag_correcta.png

Contenido visible en la imagen:
text

picoCTF{*********

🗜️ Extracción de la Segunda Parte (Zlib) esto seria mas tecnico pero realmente se muestra directamente en el pdf que nos ofrecen.
Paso 6: Extraer los datos comprimidos

Según binwalk, los datos comprimidos comienzan en el offset 1149. Extraemos estos datos:
bash

dd if=flag2of2-final.pdf of=47D.zlib bs=1 skip=1149

Salida:
text

2213+0 records in
2213+0 records out
2213 bytes (2.2 kB) copied, 0.00283556 s, 780 kB/s

Paso 7: Intentar descomprimir los datos Zlib
bash

python3 -c "
import zlib
with open('47D.zlib', 'rb') as f:
    data = f.read()
    decompressed = zlib.decompress(data)
    with open('parte2.pdf', 'wb') as out:
        out.write(decompressed)
"

Observación: Al ejecutar binwalk -e, se generaron dos archivos en la carpeta _flag2of2-final.pdf.extracted/:
bash

cd _flag2of2-final.pdf.extracted/
ls -la

Salida:
text

47D        # Archivo de texto ASCII
47D.zlib   # Datos comprimidos Zlib

Paso 8: Identificar dónde está realmente la bandera
bash

file 47D
file 47D.zlib

Salida:
text

47D: ASCII text
47D.zlib: zlib compressed data

¡Importante! La bandera no está en 47D.zlib (el archivo comprimido), sino en 47D, que es el archivo descomprimido que binwalk generó automáticamente durante el proceso de extracción.
Paso 10: Ver el contenido completo del archivo 47D
bash

cat 47D

Salida:
text

q 0.1 0 0 0.1 0 0 cm
10 0 0 10 0 0 cm BT
/R7 16 Tf
1 0 0 1 50 250 Tm
(*************************})Tj

Análisis: El archivo 47D es un PDF en texto plano que contiene la segunda parte de la bandera, visible después del comando Tj (show text).
🚫 Problemas y Soluciones Durante el Proceso
Problema 1: binwalk no extrae correctamente

Error:
text

WARNING: One or more files failed to extract: either no utility was found or it's unimplemented

Solución: A pesar del warning, binwalk sí generó los archivos 47D y 47D.zlib. El archivo 47D contenía la bandera ya descomprimida.
Problema 2: La imagen extraída no se veía correctamente

Solución: Ajustamos el count a 914 bytes (el tamaño exacto de la imagen PNG) y no 1149 como en intentos anteriores.
Problema 3: flag.png tenía 0 bytes

Solución: Extraje manualmente la imagen con dd usando el offset y tamaño correctos, eliminando la dependencia de binwalk para esta extracción.
Problema 4: Confusión entre 47D y 47D.zlib

Solución: El archivo 47D es el resultado de binwalk después de descomprimir 47D.zlib. La bandera estaba en 47D, no en el archivo comprimido.

🎯 Bandera Final
Paso 11: Combinar las partes

Parte 1 (de la imagen PNG):
text

picoCTF{********

Parte 2 (del archivo 47D):
text

*******************}

📊 Resumen de Estructura del Archivo
Offset		Tamaño		Contenido		Parte de la Bandera
0 - 913		914 bytes	Imagen PNG		picoCTF{******
914 - 1148	235 bytes	PDF (versión 1.4)	No contiene bandera
1149 - final	2213 bytes	Datos Zlib comprimidos	******************}
Flujo de Extracción de la Segunda Parte
text

flag2of2-final.pdf (offset 1149)
    ↓ dd skip=1149
47D.zlib (datos comprimidos)
    ↓ binwalk -e (descompresión automática)
47D (PDF en texto plano)
    ↓ strings
(**********************})Tj  ← Segunda parte de la bandera

🧠 Lecciones Aprendidas

    Políglotas: Un archivo puede ser válido en múltiples formatos simultáneamente. La extensión no siempre indica el tipo real de archivo.

    Extracción manual vs automática: Aunque binwalk -e dio un warning, aún generó archivos útiles. Es importante revisar siempre la carpeta de extracción.

    Diferencia entre archivos comprimidos y descomprimidos: 47D.zlib es el archivo comprimido, mientras que 47D es el resultado descomprimido que contiene la bandera.

    Importancia de los bytes exactos: Usar el count correcto (914) fue crucial para extraer correctamente la imagen PNG.

    Herramientas complementarias: strings es útil para extraer texto legible de archivos binarios o comprimidos.

    Revisar todos los archivos extraídos: La bandera estaba en un archivo que binwalk generó automáticamente, pero que inicialmente pasé por alto.
