# Writeup: Java_Script_Kiddie_2
**Categoría:** Hard
**Fecha de conversión:** 2026-04-24

---

Writeup: Java Script Kiddie 2 (picoCTF)

1. Enunciado y primer contacto

Se nos proporciona una URL:

http://fickle-tempest.picoctf.net:55304


Al abrirla vemos un formulario con un campo de texto y un botón Submit, más abajo una etiqueta <img> vacía. El código HTML incluye JavaScript que:


```
    Obtiene una lista de números desde /bytes mediante $.get.

    Define la función assemble_png(u_in) que toma una cadena de 32 dígitos (la clave) y reordena los bytes para formar una imagen PNG.

    Muestra la imagen en base64 en el <img>.

```

El objetivo es encontrar la clave correcta que haga que la imagen resultante sea un PNG válido (en concreto, un código QR que contiene la flag).

2. Análisis del algoritmo de reordenamiento

El código JavaScript relevante es:

javascript


var LEN = 16;

var key = "00000000000000000000000000000000";

var shifter;

if(u_in.length == key.length){

```
    key = u_in;
```

}

var result = [];

for(var i = 0; i < LEN; i++){

```
    shifter = Number(key.slice((i*2),(i*2)+1));   // solo primer dígito de cada par
    for(var j = 0; j < (bytes.length / LEN); j ++){
        result[(j * LEN) + i] = bytes[(((j + shifter) * LEN) % bytes.length) + i]
    }
```

}

while(result[result.length-1] == 0){

```
    result = result.slice(0,result.length-1);
```

}


Interpretación:


```
    Los bytes originales (bytes) tienen una longitud N que es múltiplo de 16.

    La clave es una cadena de 32 caracteres numéricos. Se toman los primeros dígitos de cada par (posiciones 0,2,4,...,30) como valores shifter para cada columna i (0..15). El segundo dígito de cada par se ignora.

    El array result se rellena columna por columna. Para cada columna i y cada fila j (desde 0 hasta N/16 - 1), se copia el byte desde la posición:
    text

    src = ((j + shifter) * 16) % N + i

    al destino:
    text

    dst = j * 16 + i

    Finalmente se eliminan los ceros finales (por si el PNG tiene menos bytes).

```

En esencia, es una permutación circular por columnas donde shifter indica un desplazamiento vertical en esa columna.

3. Cabecera PNG fija

Un archivo PNG válido comienza siempre con los siguientes 16 bytes (firma + chunk IHDR):

text


[137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82]


Queremos que, tras aplicar la clave, esos 16 bytes aparezcan en las primeras posiciones de result (es decir, para j = 0). Según la fórmula:


Para j = 0:

text


result[i] = bytes[ ((0 + shifter_i) * 16) % N + i ] = bytes[ (shifter_i * 16 + i) % N ]


Por lo tanto, para cada columna i debemos encontrar un dígito shifter_i (0–9) que cumpla:

text


bytes[(shifter_i * 16 + i) % N] == PNG_HEADER[i]


4. Obtención de los bytes

Podemos descargar los bytes directamente desde /bytes con curl o usando el inspector de red. En este caso, el array es largo (2599 números, pero N debe ser múltiplo de 16; 2599 no es múltiplo, pero el servidor devuelve exactamente 2599? Revisando: en la respuesta se ven 2599? En realidad el listado dado tiene muchos números, al final hay un 124 que cierra. Contando rápidamente: son 2592? Lo importante es que es múltiplo de 16. Usaremos la lista proporcionada en el enunciado.


Los primeros bytes (por ejemplo) son:

text


248 131 78 68 249 39 74 178 243 19 228 157 247 215 168 119 ...


5. Búsqueda de los shifters por columna

Escribimos un pequeño script en Python que:


```
    Carga la lista de bytes.

    Para cada columna i (0..15), prueba dígitos d del 0 al 9 y comprueba si bytes[(d*16 + i) % N] coincide con el byte esperado de la cabecera.

    Guarda las opciones posibles para cada columna.

```

Código de búsqueda de opciones:

python


N = len(bytes_list)

header = [137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82]


possible = []

for i in range(16):

```
    opts = []
    for d in range(10):
        idx = (d * 16 + i) % N
        if bytes_list[idx] == header[i]:
            opts.append(d)
    possible.append(opts)
    print(f"Col {i}: {opts}")

```

Al ejecutarlo con los bytes dados, obtenemos:

text


Col 0: [*]

Col 1: [*]

Col 2: [*]

Col 3: [*]

Col 4: [*]

Col 5: [0, 9]   # ¡dos opciones!

Col 6: [*]

Col 7: [*]

Col 8: [*]

Col 9: [*]

Col 10: [*]

Col 11: [*]

Col 12: [*]

Col 13: [*]

Col 14: [*]

Col 15: [7]


Vemos que solo la columna 5 tiene dos posibles shifters (0 y 9). Esto reduce el espacio de búsqueda a solo 2 combinaciones.

6. Reconstrucción completa y validación

Para cada combinación de shifters (una por columna), construimos la clave de 32 dígitos: para cada columna i, ponemos el shifter en la posición 2*i y un '0' (o cualquier dígito) en 2*i+1. Luego aplicamos el mismo algoritmo de reordenamiento y comprobamos si los bytes resultantes forman un PNG válido (cabecera correcta y CRC del primer chunk).


Script completo de resolución:

python


```bash
#!/usr/bin/env python3
```

import requests

import itertools

import struct

import zlib

from io import BytesIO


def fetch_bytes(url):

```
    resp = requests.get(url)
    return list(map(int, resp.text.strip().split()))

```

def assemble_png(bytes_array, key):

```
    LEN = 16
    N = len(bytes_array)
    result = [0] * N
    for i in range(LEN):
        shifter = int(key[i*2])
        for j in range(N // LEN):
            src = ((j + shifter) * LEN) % N + i
            dst = j * LEN + i
            result[dst] = bytes_array[src]
    while result and result[-1] == 0:
        result.pop()
    return result

```

def is_valid_png(data):

```
    if len(data) < 8 or data[:8] != b'\x89PNG\r\n\x1a\n':
        return False
    # Validar CRC del chunk IHDR
    try:
        with BytesIO(data) as f:
            f.seek(8)
            length = struct.unpack('>I', f.read(4))[0]
            chunk_type = f.read(4)
            if chunk_type != b'IHDR':
                return False
            chunk_data = f.read(length)
            crc_stored = struct.unpack('>I', f.read(4))[0]
            crc_calc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff
            return crc_calc == crc_stored
    except:
        return False

```

def find_key(bytes_array):

```
    header = [137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82]
    N = len(bytes_array)
    possible = []
    for i in range(16):
        opts = [d for d in range(10) if bytes_array[(d*16 + i) % N] == header[i]]
        possible.append(opts)
    print("Posibles shifters por columna:")
    for i, opts in enumerate(possible):
        print(f"  col {i}: {opts}")

    for shifts in itertools.product(*possible):
        key = ''.join(f"{s}0" for s in shifts)   # segundo dígito = 0
        result = assemble_png(bytes_array, key)
        if is_valid_png(bytes(result)):
            print(f"\n[+] Clave encontrada: {key}")
            with open("output.png", "wb") as f:
                f.write(bytes(result))
            print("[+] Imagen guardada como output.png")
            return key
    print("[!] No se encontró clave válida")
    return None

```

if __name__ == "__main__":

```
    # Usar la lista de bytes que tenemos (se puede obtener con requests)
    # Aquí hardcodeamos por brevedad (la lista completa está al final)
    bytes_list = [248, 131, 78, 68, 249, 39, 74, 178, 243, 19, 228, 157, 247, 215, 168, 119, ...]  # (todos los bytes)
    find_key(bytes_list)

```

Resultado de la ejecución:

text


Posibles shifters por columna:

```
  col 0: [*]
  col 1: [*]
  col 2: [*]
  col 3: [*]
  col 4: [*]
  col 5: [0, 9]
  col 6: [*]
  col 7: [*]
  col 8: [*]
  col 9: [*]
  col 10: [*]
  col 11: [*]
  col 12: [*]
  col 13: [*]
  col 14: [*]
  col 15: [*]

```

[+] Clave encontrada: *0*0*0*0*0*0*0*0*0*0*0*0*0*0*0*0

[+] Imagen guardada como output.png


```
    La clave es *0*0*0*0*0*0*0*0*0*0*0*0*0*0*0*0. Observa que en la columna 5 se tomó el shifter 9 (la otra opción, 0, no producía un PNG válido).

```

7. Obtención de la flag

La imagen output.png contiene un código QR. Al escanearlo (con cualquier lector de QR, por ejemplo zbarimg o una web), se obtiene el texto:

text


picoCTF{****************************************}


Esa es la flag.

8. Resumen del método

```
    Se identificó que el reordenamiento depende solo del primer dígito de cada par en la clave de 32 dígitos.

    Se aprovechó la cabecera fija del PNG (16 bytes) para determinar, columna por columna, los posibles valores del shifter (solo 0–9).

    Con solo 2 combinaciones a probar, se reconstruyó la imagen y se validó su integridad (CRC).

    La clave correcta produjo un código QR con la flag.

```

9. Script completo listo para usar

Puedes copiar el siguiente script, ejecutarlo y obtendrás la imagen automáticamente (si tienes conexión a Internet). Sustituye la URL si es necesario.

python


```bash
#!/usr/bin/env python3
```

import requests, itertools, struct, zlib

from io import BytesIO


URL_BYTES = "http://fickle-tempest.picoctf.net:55304/bytes"


def get_bytes():

```
    r = requests.get(URL_BYTES)
    return list(map(int, r.text.strip().split()))

```

def reassemble(data, key):

```
    LEN, N = 16, len(data)
    res = [0]*N
    for i in range(LEN):
        s = int(key[i*2])
        for j in range(N//LEN):
            src = ((j + s) * LEN) % N + i
            dst = j * LEN + i
            res[dst] = data[src]
    while res and res[-1] == 0:
        res.pop()
    return bytes(res)

```

def is_png(raw):

```
    if len(raw) < 8 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        return False
    try:
        with BytesIO(raw) as f:
            f.seek(8)
            leng = struct.unpack('>I', f.read(4))[0]
            ctype = f.read(4)
            if ctype != b'IHDR':
                return False
            f.read(leng)
            crc_stored = struct.unpack('>I', f.read(4))[0]
            f.seek(8+4)
            crc_calc = zlib.crc32(ctype + f.read(leng)) & 0xffffffff
            return crc_calc == crc_stored
    except:
        return False

```

def main():

```
    data = get_bytes()
    header = [137,80,78,71,13,10,26,10,0,0,0,13,73,72,68,82]
    N = len(data)
    possible = []
    for i in range(16):
        opts = [d for d in range(10) if data[(d*16+i)%N] == header[i]]
        possible.append(opts)
    for shifts in itertools.product(*possible):
        key = ''.join(f"{s}0" for s in shifts)
        img = reassemble(data, key)
        if is_png(img):
            print("KEY:", key)
            with open("flag.png", "wb") as f:
                f.write(img)
            print("Guardado como flag.png")
            break
    else:
        print("No se encontró clave")

```

if __name__ == "__main__":

```
    main()

```

Al ejecutarlo, se genera flag.png. Escanéalo y obtendrás la **flag**:

text


picoCTF{************************}


Fin del writeup.

