# Writeup: 13
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Reto ROT13 (picoCTF)

Descripción del reto


Se nos proporciona el siguiente texto cifrado:

text


cvpbPGS{abg_gbb_onq_bs_n_ceboyrz}


El nombre del reto (13) sugiere que se trata de ROT13, un cifrado por desplazamiento de 13 posiciones en el alfabeto, que es reversible (aplicarlo dos veces devuelve el texto original).

¿Qué es ROT13?


ROT13 es un cifrado César con desplazamiento 13. Es ampliamente utilizado en entornos digitales para ofuscar texto sin necesidad de claves, ya que al ser simétrico, aplicar ROT13 dos veces restaura el mensaje original. Funciona únicamente sobre letras mayúsculas y minúsculas; números, símbolos y espacios permanecen sin cambios.

Proceso de resolución


Para descifrar el texto, se aplica ROT13 a cada letra. Por ejemplo:


```
    c (letra 2) → p (letra 15): desplazamiento +13 (o -13)

    v (letra 21) → i (letra 8): 21+13=34 → 34-26=8

    etc.

```

El resultado esperado es la bandera en formato picoCTF{...}.

Script utilizado


Se creó un script interactivo en Python que permite aplicar ROT13 a cualquier texto. El código es el siguiente:

python


Rot13.py


def rot13(texto):

```
    resultado = ""
    for char in texto:
        if char.isalpha():
            mayus = char.isupper()
            base = ord('A') if mayus else ord('a')
            # ROT13: desplazamiento 13
            nuevo = (ord(char) - base + 13) % 26
            resultado += chr(base + nuevo)
        else:
            resultado += char
    return resultado

```

def main():

```
    texto = ""
    while True:
        print("\n--- MENÚ ROT13 ---")
        print("1. Ingresar texto")
        print("2. Aplicar ROT13 al texto actual")
        print("3. Salir")
        opcion = input("Elige una opción (1/2/3): ")

        if opcion == "1":
            texto = input("Introduce el texto: ")
            print("Texto guardado.")
        elif opcion == "2":
            if texto == "":
                print("No hay texto ingresado. Primero usa la opción 1.")
            else:
                resultado = rot13(texto)
                print("\nResultado ROT13:")
                print(resultado)
        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

```

if __name__ == "__main__":

```
    main()


```

---------------------------------------------------------------------------------------


### Explicación del script


```
    La función rot13 itera sobre cada carácter del texto.

    Si es letra, determina si es mayúscula o minúscula y obtiene su código ASCII base (A o a).

    Calcula la nueva posición: (código - base + 13) % 26 y convierte de vuelta a carácter.

    Los caracteres no alfabéticos se mantienen igual.

    El menú principal permite ingresar un texto, aplicarle ROT13 y mostrar el resultado, repitiendo hasta que el usuario decida salir.

```

Ejecución del reto


Al ejecutar el script y seguir los pasos:

text


## --- menú rot13 ---

1. Ingresar texto
2. Aplicar ROT13 al texto actual
3. Salir
Elige una opción (1/2/3): 1

Introduce el texto: cvpbPGS{abg_gbb_onq_bs_n_ceboyrz}

Texto guardado.


## --- menú rot13 ---

1. Ingresar texto
2. Aplicar ROT13 al texto actual
3. Salir
Elige una opción (1/2/3): 2


Resultado ROT13:

picoCTF{****************}



Conclusión


El reto demostró el uso de ROT13, un cifrado simple pero útil en contextos de ofuscación.

El script proporcionado automatiza el proceso y puede ser reutilizado para cualquier texto

cifrado con este método.

