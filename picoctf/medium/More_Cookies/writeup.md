# Writeup: More_Cookies
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Write-up: More Cookies (picoCTF)

1. Descripción del reto

El sitio web muestra un mensaje: "Only the admin can use it!". Para acceder, el servidor verifica una cookie llamada auth_name. Si la cookie pertenece a un administrador, se muestra la flag. Nosotros tenemos una cookie de usuario normal (posiblemente con "admin":0). El objetivo es modificar la cookie para convertirnos en administrador.


La cookie tiene este aspecto (en la petición original):

text


**Cookie**: name=-1; auth_name=ZE8vZTJHOUlkRFBPREEwazluNTJuZmNrUFltTk45VVAvRXdTdU5RNTJSakZuV04rVVVFTHNwTFpvb1lQOXhnNjdGUWxnakVOWXYzQ3ZFUktQakhoYkFKVFpZNFJPVWUwZVhXbkhQbkxFazRDUWJHRE1PQU1lT3lTN3Fjb29FUjM=


2. Identificación del cifrado

El valor de auth_name está codificado en Base64. Al decodificarlo, obtenemos una cadena de bytes. Dado que el reto se llama "More Cookies" y se menciona en la descripción de picoCTF que usa AES-CBC, sabemos que:


```
    Los primeros 16 bytes son el vector de inicialización (IV).

    El resto es el texto cifrado.

    El texto plano descifrado contiene un JSON o una estructura con el campo admin (por ejemplo: {"username":"user","admin":0}).

```

3. Vulnerabilidad: Bit-flipping en CBC

El modo CBC (Cipher Block Chaining) descifra cada bloque usando el IV o el bloque cifrado anterior. La propiedad clave es que modificando un byte del IV se altera el byte correspondiente del primer bloque de texto plano, sin romper la integridad del cifrado (no hay MAC).


Fórmula de descifrado CBC:

text


P1 = Decrypt(C1) XOR IV


Si cambiamos un bit en el IV, el mismo bit cambiará en P1. Podemos forzar que un valor booleano (0 → 1) o un carácter cambie a otro.


El ataque consiste en:


```
    Tomar la cookie original.

    Modificar un byte del IV (o del bloque cifrado anterior) para que, al descifrarse, el campo admin pase de 0 a 1.

    Enviar la nueva cookie al servidor.

    Repetir con diferentes posiciones y bits hasta que el servidor muestre la flag.

```

4. Estrategia del script

El script que utilizamos realiza las siguientes tareas:


```
    Decodifica la cookie original en Base64.

    Separa el IV y el texto cifrado.

    Itera sobre cada byte del IV (16 bytes) y cada bit dentro de ese byte (8 bits).

    Para cada combinación, voltea ese bit (XOR con 1 << bit).

    Construye una nueva cookie con el IV modificado + el texto cifrado original.

    Envía una petición HTTP GET con esa cookie.

    Si en la respuesta HTML aparece la cadena "picoCTF{", muestra la flag y termina.

    Si tras probar todos los bytes del IV no encuentra la flag, entonces prueba a modificar el primer bloque del texto cifrado (esto afecta al segundo bloque de texto plano, útil si el campo admin está en otro bloque).

```

Además, el script maneja timeouts y errores de red para no quedarse colgado.

5. Explicación línea a línea del script final
python


import requests

import base64


url = "http://wily-courier.picoctf.net:52522/"

cookie_original = "ZE8vZTJHOUlkRFBPREEwazluNTJuZmNrUFltTk45VVAvRXdTdU5RNTJSakZuV04rVVVFTHNwTFpvb1lQOXhnNjdGUWxnakVOWXYzQ3ZFUktQakhoYkFKVFpZNFJPVWUwZVhXbkhQbkxFazRDUWJHRE1PQU1lT3lTN3Fjb29FUjM="

decodificado = base64.b64decode(cookie_original)

iv = decodificado[:16]

ct = decodificado[16:]


```bash
# Prueba modificando el IV
```

for i in range(16):

```
    for bit in range(8):
        nuevo_iv = bytearray(iv)
        nuevo_iv[i] ^= (1 << bit)   # Voltea el bit
        nueva_cookie = base64.b64encode(bytes(nuevo_iv) + ct).decode()
        try:
            r = requests.get(url, cookies={"name": "-1", "auth_name": nueva_cookie}, timeout=3)
            if "picoCTF{" in r.text:
                print("¡Flag encontrada!")
                print(r.text)
                exit()
            else:
                print(".", end="", flush=True)  # Progreso
        except:
            print("X", end="", flush=True)

```

¿Qué hace cada parte?


```
    decodificado = base64.b64decode(...): Convierte la cookie de Base64 a bytes.

    iv = decodificado[:16], ct = decodificado[16:]: Separa IV y ciphertext.

    Doble bucle for i in range(16) y for bit in range(8): Recorre todos los 128 bits del IV.

    nuevo_iv[i] ^= (1 << bit): Voltea un solo bit en la posición i, bit bit.

    base64.b64encode(...).decode(): Vuelve a codificar la cookie para enviarla.

    requests.get(..., cookies=...): Envía la petición con la cookie modificada.

    Si la respuesta contiene picoCTF{, se imprime y termina.

    Los puntos (".") indican intentos fallidos; "X" indica error de red/timeout.

```

En la ejecución que hiciste, se observaron muchos puntos (intentos fallidos) y algún error de resolución DNS, pero finalmente se encontró la flag. Esto significa que en algún byte y bit concretos la modificación convirtió a la cookie en admin.

6. Resultado obtenido

El servidor respondió con la página que contiene:

text


### Flag: picoCTF{***********************}


Por lo tanto, la flag es:


picoCTF{*********************}

7. Resolución de problemas

```
    El script se quedaba "colgado": Añadimos timeout=3 para evitar esperas infinitas.

    Errores de resolución DNS: Ocurrieron esporádicamente (Failed to resolve 'wily-courier.picoctf.net'), pero el script los capturaba con except y seguía probando.

    No encontraba la flag modificando el IV: Por eso incluimos también la opción de modificar el primer bloque del ciphertext (aunque en este caso bastó con el IV).

```

8. Conclusión

El ataque de bit-flipping en CBC es una vulnerabilidad clásica cuando el servidor confía en datos cifrados sin autenticación (sin HMAC). Cambiando un solo bit en el IV logramos que el texto plano descifrado modifique el valor de admin de 0 a 1, otorgándonos privilegios. El script automatiza la búsqueda de la posición correcta del bit

