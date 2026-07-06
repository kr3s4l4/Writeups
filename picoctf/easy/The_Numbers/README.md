# Writeup: The_Numbers
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Extracción de texto de imagen y descifrado A1Z26

1. Contexto del desafío

Se disponía de una imagen que contenía una cadena de caracteres, probablemente una flag con formato PICOCTF{...}. El objetivo era extraer el texto de la imagen para obtener la flag.

2. Primer intento: OCR con Tesseract

Se utilizó la herramienta estándar Tesseract OCR mediante el comando:

bash


tesseract imagen.jpg resultado -l spa


Sin embargo, la salida fue vacía o con muy pocos caracteres. La razón era que la imagen tenía un fondo sucio, con manchas, bajo contraste y posiblemente ruido, lo que dificultaba la detección de texto por parte del OCR.

3. Alternativas consideradas

Para mejorar el OCR se podrían haber aplicado técnicas de preprocesamiento de imagen, como:


```
    Convertir a escala de grises.

    Aumentar el contraste.

    Binarizar (threshold) para separar texto de fondo.

    Usar herramientas como ImageMagick o OCRmyPDF que aplican estos filtros automáticamente.

```

Ejemplo de preprocesamiento con ImageMagick:

bash


convert imagen.jpg -colorspace gray -contrast-stretch 2% -threshold 50% imagen_procesada.png

tesseract imagen_procesada.png stdout -l spa


Sin embargo, al tratarse de un texto relativamente corto (una flag), se decidió tipar manualmente los caracteres visibles para no perder tiempo.

4. Extracción manual y observación

Al observar la imagen, se distinguía claramente una secuencia de números y algunos símbolos. Se tipeó lo siguiente:

text


16 9 3 15 3 20 6 {20 8 5 14 21 13 2 5 18 19 13 1 19 15 14 }


Inmediatamente se notó que los números estaban en su mayoría en el rango 1–26, lo que sugería un cifrado A1Z26 (cada letra se reemplaza por su posición en el alfabeto: A=1, B=2, ..., Z=26). Las llaves { y } eran literales, probablemente parte de la flag.

5. El cifrado A1Z26

El cifrado A1Z26 es una forma simple de codificación donde:


```
    A → 1

    B → 2

    ...

    Z → 26

```

Se utiliza a menudo en acertijos y CTF para ocultar texto. Para decodificar, simplemente se convierte cada número en su letra correspondiente.


Decodificación manual:


```
    16 → P

    9 → I

    3 → C

    15 → O

    3 → C

    20 → T

    6 → F

    Luego {

    20 → T

    8 → H

    5 → E

    14 → N

    21 → U

    13 → M

    2 → B

    5 → E

    18 → R

    19 → S

    13 → M

    1 → A

    19 → S

    15 → O

    14 → N

    }

```

Concatenando se obtiene: PICOCTF{THENUMBERSMASON}

6. Script en Python para automatizar cifrados

Para facilitar la codificación/decodificación de estos cifrados y otros comunes, se elaboró un script en Python. Incluye:


```
    A1Z26: codifica letras a números (separados por espacios) y decodifica números a letras.

    Cifrado César: desplazamiento fijo de letras.

    Base64: codificación/decodificación estándar.

```

El script se puede usar en modo interactivo o mediante línea de comandos.

Código del script: cipher_tool.py

python


cipher_tool.py


```bash
#!/usr/bin/env python3
```

"""

Herramienta de cifrado simple que incluye:

- A1Z26: letras <-> números (A=1, B=2, ...)
- Cifrado César (desplazamiento fijo)
- Base64
"""


import argparse

import sys

import base64

import re


def a1z26_encode(text):

```
    """Convierte letras a números separados por espacios.
    Los caracteres no alfabéticos se conservan."""
    result = []
    for ch in text:
        if ch.isalpha():
            num = ord(ch.upper()) - ord('A') + 1
            result.append(str(num))
        else:
            result.append(ch)
    return ' '.join(result)  # los números se separan por espacios, otros caracteres quedan solos

```

def a1z26_decode(text):

```
    """Convierte números (1-26) en letras.
    Los números pueden estar separados por espacios; otros caracteres se conservan."""
    # Reemplazar cada número independiente (1-2 dígitos) por su letra
    def replace(match):
        num = int(match.group(0))
        return chr(num + ord('A') - 1) if 1 <= num <= 26 else match.group(0)
    # Patrón: números de 1 o 2 dígitos que no formen parte de una palabra más grande
    # Usamos \b para límites de palabra
    return re.sub(r'\b(\d{1,2})\b', replace, text)

```

def caesar_encode(text, shift):

```
    """Cifrado César: desplaza letras mayúsculas y minúsculas."""
    result = []
    for ch in text:
        if ch.isalpha():
            start = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - start + shift) % 26 + start))
        else:
            result.append(ch)
    return ''.join(result)

```

def caesar_decode(text, shift):

```
    return caesar_encode(text, -shift)

```

def base64_encode(text):

```
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

```

def base64_decode(text):

```
    try:
        return base64.b64decode(text.encode('utf-8')).decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

```

def main():

```
    parser = argparse.ArgumentParser(description="Herramienta de cifrado con A1Z26, César y Base64.")
    parser.add_argument('-t', '--text', help="Texto a procesar (si no se proporciona, se lee de stdin).")
    parser.add_argument('-m', '--mode', choices=['encode', 'decode'], default='encode',
                        help="Modo: codificar o decodificar (por defecto: encode).")
    parser.add_argument('-c', '--cipher', choices=['a1z26', 'caesar', 'base64'], default='a1z26',
                        help="Tipo de cifrado (por defecto: a1z26).")
    parser.add_argument('-s', '--shift', type=int, default=3,
                        help="Desplazamiento para César (por defecto: 3).")
    parser.add_argument('-i', '--interactive', action='store_true',
                        help="Modo interactivo con menú.")
    args = parser.parse_args()

    if args.interactive:
        while True:
            print("\n--- Herramienta de cifrado ---")
            print("1. A1Z26 (letras <-> números)")
            print("2. Cifrado César")
            print("3. Base64")
            print("4. Salir")
            choice = input("Elige una opción: ").strip()
            if choice == '4':
                break
            if choice not in ('1','2','3'):
                print("Opción inválida.")
                continue

            mode = input("Modo (encode/decode): ").strip().lower()
            if mode not in ('encode','decode'):
                print("Modo inválido.")
                continue

            text = input("Introduce el texto (o 'file:ruta' para leer de archivo): ").strip()
            if text.startswith('file:'):
                try:
                    with open(text[5:], 'r') as f:
                        text = f.read().strip()
                except Exception as e:
                    print(f"Error al leer archivo: {e}")
                    continue

            if choice == '1':
                if mode == 'encode':
                    result = a1z26_encode(text)
                else:
                    result = a1z26_decode(text)
            elif choice == '2':
                try:
                    shift = int(input("Desplazamiento (entero): ").strip())
                except ValueError:
                    shift = 3
                if mode == 'encode':
                    result = caesar_encode(text, shift)
                else:
                    result = caesar_decode(text, shift)
            else:  # base64
                if mode == 'encode':
                    result = base64_encode(text)
                else:
                    result = base64_decode(text)

            print("\nResultado:")
            print(result)
            input("Presiona Enter para continuar...")
    else:
        if args.text:
            text = args.text
        else:
            if not sys.stdin.isatty():
                text = sys.stdin.read().strip()
            else:
                print("No se proporcionó texto. Usa -t o pipe desde stdin, o -i para modo interactivo.")
                sys.exit(1)

        if args.cipher == 'a1z26':
            if args.mode == 'encode':
                output = a1z26_encode(text)
            else:
                output = a1z26_decode(text)
        elif args.cipher == 'caesar':
            if args.mode == 'encode':
                output = caesar_encode(text, args.shift)
            else:
                output = caesar_decode(text, args.shift)
        elif args.cipher == 'base64':
            if args.mode == 'encode':
                output = base64_encode(text)
            else:
                output = base64_decode(text)

        print(output)

```

if __name__ == '__main__':

```
    main()



```

--------------------------------------------------------------------------------------


Uso del script para decodificar la flag


Para decodificar la cadena de números obtenida de la imagen:

bash


python cipher_tool.py -t "16 9 3 15 3 20 6 {20 8 5 14 21 13 2 5 18 19 13 1 19 15 14 }" -m decode -c a1z26


Salida:

text


## P i c o c t f { * * * * * * * * }


tambien puedes usar el modo interactivo

python cipher_tool.py -i


El resultado incluye espacios entre letras, pero la flag es PICOCTF{THENUMBERSMASON} (sin espacios). El script decodifica cada número y mantiene los símbolos, por lo que solo hay que eliminar los espacios intermedios para obtener la flag limpia.

7. Conclusión

Aunque el OCR falló debido a la calidad de la imagen, la observación manual permitió extraer los datos. El reconocimiento del patrón A1Z26 llevó a la flag correcta. Este tipo de cifrado es común en desafíos de CTF, y tener una herramienta automatizada facilita tanto la codificación como la decodificación. El script desarrollado puede ampliarse fácilmente para incluir otros cifrados como ROT13, Atbash, etc., y resulta útil para futuros retos.


**Nota**: Si se hubiera deseado depurar la imagen, se podrían haber utilizado herramientas como ImageMagick para mejorar el contraste y eliminar ruido, o directamente OCRmyPDF que integra preprocesamiento avanzado, pero en este caso el texto era corto y visible, por lo que se optó por la transcripción manual.



He mejorado el script para que funcione en diferentes casos, con varios tipos de separadores 

cipher_tool_mejorado.py


A1Z26 con separadores personalizados


```
    Espacios (por defecto):
    bash

    python cipher_tool_mejorado.py -t "P I C" -m encode -c a1z26
    # 16 9 3
    python cipher_tool_mejorado.py -t "16 9 3" -m decode -c a1z26
    # PIC

    Comas:
    bash

    python cipher_tool_mejorado.py -t "16,9,3" -m decode -c a1z26 --sep ","
    # PIC

    Números seguidos (sin separador):
    bash

    python cipher_tool_mejorado.py -t "160903" -m decode -c a1z26 --sep none
    # PIC

    Expresión regular personalizada (ejemplo: números entre paréntesis):
    bash

    python cipher_tool_mejorado.py -t "(16)(9)(3)" -m decode -c a1z26 --sep "regex:\((\d+)\)"
    # PIC

```

César y Base64 igual que antes.

Modo interactivo

bash


python cipher_tool_mejorado.py -i

