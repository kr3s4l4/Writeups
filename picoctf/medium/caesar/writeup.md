# Writeup: caesar
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup: Cifrado César – PicoCTF

Título: Cruzar el Rubicón (con matemática modular)

1. Descripción del reto

Se proporciona un archivo data.enc cuyo contenido es:

text


picoCTF{hwtxxnslymjwzgnhtswlvhsgdv}


La flag está dentro de las llaves y ha sido cifrada con un cifrado César (desplazamiento de letras). El objetivo es recuperar el texto original.

2. Extracción del texto cifrado

Extraemos la cadena interior sin las llaves:

bash


cat data.enc | grep -oP '(?<={)[^}]+(?=})'


Resultado:

hwtxxnslymjwzgnhtswlvhsgdv

3. Principio del cifrado César y equivalencia modular

El cifrado César reemplaza cada letra por otra situada un número fijo k de posiciones más adelante en el alfabeto (desplazamiento a la derecha).

Para cifrar: C = (P + k) mod 26

Para descifrar: P = (C - k) mod 26


Una propiedad **importante**: restar k es equivalente a sumar 26 - k.

Es decir, descifrar con desplazamiento k es lo mismo que cifrar con desplazamiento 26 - k.

Por lo tanto, todo el proceso se puede ver como una rotación, sin más que elegir el valor adecuado.

4. Descifrado del texto
4.1 Método sistemático (probar todos los desplazamientos)


Podemos descifrar probando todos los posibles k de 1 a 25, restando k a cada letra.


Usamos Python para ello:

python


cifrado = "hwtxxnslymjwzgnhtswlvhsgdv"


for k in range(1, 26):

```
    desc = ''.join(chr((ord(c) - ord('a') - k) % 26 + ord('a')) for c in cifrado)
    print(f"Desplazamiento {k:2d}: {desc}")

```

Entre las salidas observamos:

text


Desplazamiento  5: *************************


Esta cadena contiene la frase inglesa "*************" (************), una clara referencia a Julio César. El resto ******** completa la flag.

4.2 Usando tr con el concepto de equivalencia


Podemos descifrar directamente mediante tr aplicando un desplazamiento +21 (ya que 26 - 5 = 21):

bash


echo "hwtxxnslymjwzgnhtswlvhsgdv" | tr 'a-z' 'vwxyzabcdefghijklmnopqrstu'


Salida:

text


***************************


Observación: tr aplica una sustitución directa. El alfabeto destino vwxyzabcdefghijklmnopqrstu es el alfabeto original rotado 21 posiciones a la izquierda, lo que equivale a restar 5 posiciones (descifrar).

4.3 Verificación del desplazamiento original


Si tomamos la primera letra del texto claro c (índice 2) y la primera del cifrado h (índice 7), la diferencia es +5.

El cifrado aplicado originalmente fue desplazar 5 posiciones a la derecha. Por lo tanto, para descifrar restamos 5 (o sumamos 21 modularmente).

5. Flag

La flag completa es:

text


picoCTF{*****************************}


6. Conclusión

```
    El cifrado César es reversible mediante la misma operación pero con el desplazamiento inverso.

    Restar k es equivalente a sumar 26 - k; ambos métodos producen el mismo resultado.

    La elección entre uno u otro depende de la herramienta utilizada (por ejemplo, tr necesita la rotación explícita).

    La frase «cruzar el Rubicón» es una pista histórica que confirma el acierto del descifrado.
```

