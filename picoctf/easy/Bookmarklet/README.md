# Writeup: Bookmarklet
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Bookmarklet (picoCTF)

Descripción del desafío


Se proporciona un fragmento de código JavaScript que, al ejecutarse como bookmarklet, muestra una alerta con una cadena aparentemente cifrada. El objetivo es obtener la bandera.

### Análisis inicial


El código es el siguiente:

javascript


javascript:(function() {

```
    var encryptedFlag = "àÒÆÞ¦È¬ëÙ£ÖÓÚåÛÑ¢ÕÓÉÕËÆÒÇÚËí";
    var key = "picoctf";
    var decryptedFlag = "";
    for (var i = 0; i < encryptedFlag.length; i++) {
        decryptedFlag += String.fromCharCode((encryptedFlag.charCodeAt(i) - key.charCodeAt(i % key.length) + 256) % 256);
    }
    alert(decryptedFlag);
```

})();


Observamos:


```
    encryptedFlag contiene una cadena de caracteres que parece tener símbolos extendidos (fuera del rango ASCII básico).

    key es la cadena "picoctf".

    El bucle recorre cada carácter de encryptedFlag, obtiene su código Unicode, resta el código del carácter correspondiente de la clave (cíclicamente), suma 256 y toma módulo 256 para mantenerlo en el rango 0-255. Luego convierte ese valor numérico en un carácter y lo concatena a decryptedFlag.

```

Este algoritmo es un descifrado simple: se resta la clave (repitiéndose) al texto cifrado, asumiendo que el cifrado original fue una suma (módulo 256) con la misma clave.

Posible origen del cifrado


El cifrado utilizado es una variante del cifrado de Vigenère pero con operaciones a nivel de byte (módulo 256). Al usar + 256) % 256, se garantiza que la resta no produzca valores negativos. Esencialmente, el descifrado es:

text


plaintext[i] = (ciphertext[i] - key[i % keylen] + 256) % 256


Ejecución del código


Podemos ejecutar el código directamente en un entorno JavaScript (consola del navegador o Node.js) para obtener la flag. Sin embargo, también podemos reproducir la lógica en otro lenguaje como Python.

Script en Python


Para facilitar el análisis, escribimos un script equivalente:

python


```bash
# decode_javascript.py
```

encrypted = "àÒÆÞ¦È¬ëÙ£ÖÓÚåÛÑ¢ÕÓÉÕËÆÒÇÚËí"

key = "picoctf"


decrypted = ''.join(

```
    chr((ord(encrypted[i]) - ord(key[i % len(key)])) % 256)
    for i in range(len(encrypted))
```

)


print(decrypted)


### Explicación del script:


```
    ord(c) obtiene el código Unicode del carácter.

    (ord(encrypted[i]) - ord(key[i % len(key)])) % 256 realiza la misma operación que en JavaScript, pero sin sumar 256 porque el módulo ya maneja valores negativos (en Python % siempre da un resultado no negativo). En JavaScript se suma 256 para evitar negativos antes del módulo.

    Luego chr() convierte el número en carácter.

    Finalmente, concatenamos todos los caracteres.

```

Ejecución:

bash


```bash
$ python3 decode_javascript.py
```

picoCTF{*********************}


Verificación manual de los primeros caracteres


Para confirmar el funcionamiento, podemos calcular los primeros caracteres:


```
    Índice 0: 'à' → código 224. Clave 'p' → 112.
    (224 - 112) % 256 = 112 → 'p'.

    Índice 1: 'Ò' → 210. Clave 'i' → 105.
    (210 - 105) % 256 = 105 → 'i'.

    Índice 2: 'Æ' → 198. Clave 'c' → 99.
    (198 - 99) % 256 = 99 → 'c'.

    Índice 3: 'Þ' → 222. Clave 'o' → 111.
    (222 - 111) % 256 = 111 → 'o'.

    Índice 4: '¦' → 166. Clave 'c' → 99.
    (166 - 99) % 256 = 67 → 'C'.

    Índice 5: 'È' → 200. Clave 't' → 116.
    (200 - 116) % 256 = 84 → 'T'.

    Índice 6: '¬' → 172. Clave 'f' → 102.
    (172 - 102) % 256 = 70 → 'F'.

    Índice 7: 'ë' → 235. Clave 'p' (índice 7 % 7 = 0) → 112.
    (235 - 112) % 256 = 123 → '{'.

```

Así se forma picoCTF{.

Consideraciones adicionales


```
    El código original incluía un carácter Ö (posiblemente un byte extraño),
```

pero en el script de Python se ha corregido la cadena a ÖÓÚåÛÑ¢ÕÓÉÕËÆÒÇÚËí.

En tu archivo javascript.txt aparece Ö pero al ejecutar en Python con la cadena correcta se obtiene la flag.


```
    La función alert() en JavaScript mostraría la bandera en un cuadro de diálogo, pero al ser un bookmarklet, el usuario debe ejecutarlo desde los marcadores.

```

Conclusión


El desafío consiste en reconocer el algoritmo de descifrado simple, implementarlo en un lenguaje de programación o ejecutar el código original, y extraer la bandera. Este tipo de ejercicio refuerza conceptos de codificación, manipulación de caracteres y criptografía básica.

