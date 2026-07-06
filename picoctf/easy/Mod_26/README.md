# Writeup: Mod_26
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Mod 26 (picoCTF)

Descripción del reto


El reto se llama Mod 26, haciendo referencia al cifrado por desplazamiento módulo 26, es decir, un cifrado César con desplazamiento de 13 posiciones (ROT13). Se nos proporciona un texto cifrado con la estructura típica de una bandera de picoCTF.

Texto cifrado

text


cvpbPGS{arkg_gvzr_V'yy_gel_2_ebhaqf_bs_ebg13_45559noq}


### Solución


Para resolverlo, podemos usar cualquier herramienta que aplique ROT13. En mi caso, contaba con un script en Python llamado Rot13.py que implementa un menú interactivo para aplicar ROT13 a un texto. Aunque el script fue originalmente creado para otro CTF, funciona perfectamente porque ROT13 es exactamente el cifrado necesario.

### Pasos realizados


```
    Ejecuté el script:
    bash

    python3 Rot13.py

    En el menú, seleccioné la opción 1 para ingresar el texto cifrado.

    Introduje el texto:
    text

    cvpbPGS{arkg_gvzr_V'yy_gel_2_ebhaqf_bs_ebg13_45559noq}

    Luego, elegí la opción 2 para aplicar ROT13. El script mostró el resultado:
    text

    picoCTF{next_time_I'll_try_2_rounds_of_rot13_45559abd}

```

Bandera

text


picoCTF{next_time_I'll_try_2_rounds_of_rot13_45559abd}


### Explicación


El nombre "Mod 26" indica que el cifrado se basa en la aritmética modular con módulo 26, típico del cifrado César.

Un desplazamiento de 13 es el más común porque es involutivo:

aplicar ROT13 dos veces devuelve el texto original.

En este caso, el texto cifrado ya estaba en ROT13, por lo que una sola aplicación lo descifra.


Aunque usé un script pensado para ROT13,

el resultado es el mismo que si hubiera aplicado un desplazamiento de 13 manualmente

o con cualquier otra herramienta de cifrado César.


Reflexión


MOD26 y ROT13 son equivalentes

Este reto es un ejemplo clásico de criptografía básica.

La solución es directa y sirve para familiarizarse con los cifrados de sustitución simples.

La lección es que a veces los nombres de los retos dan pistas sobre el método de cifrado utilizado.


