# Writeup: interencdec
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Interencdec (picoCTF)

Descripción del reto


Se nos proporciona la siguiente cadena:

text


YidkM0JxZGtwQlRYdHFhR3g2YUhsZmF6TnFlVGwzWVROclh6ZzJhMnd6TW1zeWZRPT0nCg==


El nombre del reto ("interencdec") sugiere que se han aplicado múltiples codificaciones (intermediate encodings). Además, la presencia de == al final indica que la cadena está en Base64.

Paso 1: Decodificación Base64 (primer nivel)


Ejecutamos en terminal:

bash


echo "YidkM0JxZGtwQlRYdHFhR3g2YUhsZmF6TnFlVGwzWVROclh6ZzJhMnd6TW1zeWZRPT0nCg==" | base64 -d


Obtenemos:

text


b'd3BqdkpBTXtqaGx6aHlfazNqeTl3YTNrXzg2a2wzMmsyfQ==\n'


Se trata de una representación de bytes de Python, pero el contenido real es otra cadena Base64: d3BqdkpBTXtqaGx6aHlfazNqeTl3YTNrXzg2a2wzMmsyfQ==.

Paso 2: Decodificación Base64 (segundo nivel)


Extraemos la segunda cadena y la decodificamos:

bash


echo "d3BqdkpBTXtqaGx6aHlfazNqeTl3YTNrXzg2a2wzMmsyfQ==" | base64 -d


Resultado:

text


wpjvJAM{jhlzhy_k3jy9wa3k_86kl32k2}


Ahora tenemos un texto que parece una bandera, pero el formato no coincide con picoCTF{...}. Las letras están desplazadas, lo que indica un cifrado César.

Paso 3: Identificar el cifrado César


Observamos que la estructura wpjvJAM{...} tiene la misma longitud que picoCTF{...}. Comparando:


```
    w → p (desplazamiento de 7 hacia atrás)

    p → i (desplazamiento de 7 hacia atrás)

    j → c (desplazamiento de 7 hacia atrás)

    v → o (desplazamiento de 7 hacia atrás)

```

Confirmamos que se trata de un César con desplazamiento 7 (o 19 hacia adelante). Para descifrar, restamos 7 a cada letra (conservando mayúsculas/minúsculas y dejando números y símbolos sin cambios).

Paso 4: Script para descifrar César


Utilizamos el siguiente script en Python que permite descifrar con un desplazamiento específico o probar todos:

python


caesar_decrypt.py


def caesar_decrypt(texto, desplazamiento):

```
    resultado = ""
    for char in texto:
        if char.isalpha():
            mayus = char.isupper()
            base = ord('A') if mayus else ord('a')
            # Desplazamiento negativo para descifrar
            nuevo = (ord(char) - base - desplazamiento) % 26
            resultado += chr(base + nuevo)
        else:
            resultado += char
    return resultado

```

def main():

```
    opcion = input("¿Quieres (1) introducir un desplazamiento o (2) probar todos? (1/2): ")
    texto = input("Introduce el texto cifrado: ")
    
    if opcion == "1":
        try:
            shift = int(input("Desplazamiento (número entero): "))
            print("\nResultado:")
            print(caesar_decrypt(texto, shift))
        except ValueError:
            print("Desplazamiento inválido.")
    elif opcion == "2":
        print("\nProbando todos los desplazamientos (0 a 25):")
        for shift in range(26):
            dec = caesar_decrypt(texto, shift)
            print(f"Desplazamiento {shift:2d}: {dec}")
    else:
        print("Opción no válida.")

```

if __name__ == "__main__":

```
    main()


```

------------------------------------------------------------------------------------------


Paso 5: Aplicar el descifrado


Ejecutamos el script, seleccionamos la opción 1, introducimos el texto wpjvJAM{jhlzhy_k3jy9wa3k_86kl32k2} y el desplazamiento 7:

bash


python3 caesar_decrypt.py


Salida:

text


Resultado:

picoCTF{*************}



Resumen


El reto consistió en una doble codificación Base64 seguida de un cifrado César con desplazamiento 7. La resolución implicó:


```
    Decodificar Base64 dos veces.

    Identificar el patrón de la bandera y aplicar el descifrado César.

    Obtener la bandera en el formato correcto.

```

El script de Python facilitó el descifrado y también permitió probar todas las combinaciones en caso de no conocer el desplazamiento.

