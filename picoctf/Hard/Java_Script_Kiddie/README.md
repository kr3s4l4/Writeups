# Writeup: Java_Script_Kiddie
**Categoría:** Hard
**Fecha de conversión:** 2026-04-24

---

Write-up extremadamente detallado: Java Script Kiddie (picoCTF)

Descripción del reto


Se nos proporciona una página web con un campo para introducir una "clave mágica" de 16 dígitos. Al enviarla, la página descarga un array de números (bytes) desde /bytes y los reordena según la clave para mostrar una imagen PNG. La imagen debe ser un código QR que contiene la flag. El objetivo es encontrar la clave correcta.

### Análisis del código fuente


La página contiene el siguiente JavaScript (simplificado):

javascript


var bytes = [];

```bash
$.get("bytes", function(resp) {
```

```
    bytes = Array.from(resp.split(" "), x => Number(x));
```

});


function assemble_png(u_in){

```
    var LEN = 16;
    var key = "0000000000000000";
    if(u_in.length == LEN) key = u_in;
    var result = [];
    for(var i = 0; i < LEN; i++){
        var shifter = key.charCodeAt(i) - 48;  // dígito numérico
        for(var j = 0; j < (bytes.length / LEN); j++){
            result[(j * LEN) + i] = bytes[(((j + shifter) * LEN) % bytes.length) + i];
        }
    }
    // eliminar ceros finales
    while(result[result.length-1] == 0) result.pop();
    // mostrar como imagen
    document.getElementById("Area").src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, new Uint8Array(result)));
```

}


Observaciones:


```
    El array bytes tiene 2479 elementos (obtenido con curl).

    La clave debe tener exactamente 16 caracteres (dígitos).

    El reordenamiento se hace por columnas: para cada columna i (0..15), se toma un desplazamiento shifter (el dígito de la clave en esa posición) y se reordenan los bloques verticalmente.

    La primera fila (j=0) del resultado viene dada por:
    text

    result[i] = bytes[ (shifter * 16) % bytes.length + i ]

    Dado que bytes.length = 2479, (shifter*16) % 2479 es simplemente shifter*16 para shifter=0..9 (porque 9*16=144 < 2479). Así que result[i] = bytes[ shifter*16 + i ]. Es decir, el byte en la columna i de la primera fila se extrae del bloque número shifter (bloque 0 = primeros 16 bytes, bloque 1 = siguientes 16, etc.), en la misma columna i.

```

Vulnerabilidad estructural


La cabecera de un archivo PNG es siempre la misma (16 bytes):

text


[137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82]


Por lo tanto, para que la imagen generada sea un PNG válido, los primeros 16 bytes de result deben coincidir con esa secuencia. Esto nos permite determinar cada dígito de la clave de forma independiente: para cada columna i, buscamos en qué bloque (0..9) aparece el valor esperado de la cabecera en esa misma columna. El índice del bloque es el dígito de la clave para esa columna.

Obtención de los bytes


Desde la terminal, descargamos los bytes:

bash


curl -s http://fickle-tempest.picoctf.net:50048/bytes


La salida es una larga lista de números. Guardamos los primeros 160 bytes (10 bloques de 16) para analizar. Podemos copiarlos manualmente o usar un script. A continuación, los mostramos organizados en bloques (cada bloque comienza en un índice múltiplo de 16):


Bloque 0 (bytes 0-15):

69, 36, 1, 151, 249, 58, 81, 34, 0, 191, 105, 66, 249, 247, 243, 198


Bloque 1 (16-31):

137, 156, 68, 233, 167, 190, 130, 0, 1, 243, 0, 219, 61, 242, 0, 228


Bloque 2 (32-47):

0, 221, 78, 230, 88, 16, 26, 10, 84, 82, 0, 63, 249, 172, 0, 135


Bloque 3 (48-63):

164, 27, 1, 110, 191, 222, 1, 114, 200, 0, 0, 59, 76, 188, 68, 73


Bloque 4 (64-79):

64, 127, 0, 174, 24, 61, 68, 65, 24, 0, 156, 0, 9, 0, 95, 0


Bloque 5 (80-95):

33, 78, 69, 71, 205, 255, 44, 109, 6, 0, 114, 0, 231, 0, 106, 82


Bloque 6 (96-111):

229, 80, 154, 114, 50, 203, 50, 7, 199, 120, 47, 13, 239, 72, 114, 108


Bloque 7 (112-127):

72, 0, 59, 2, 66, 96, 199, 211, 139, 1, 209, 0, 0, 192, 22, 228


Bloque 8 (128-143):

119, 0, 169, 159, 13, 10, 99, 241, 204, 40, 112, 237, 0, 65, 241, 164


Bloque 9 (144-159):

48, 12, 121, 27, 0, 0, 173, 88, 201, 105, 191, 148, 73, 13, 231, 85

Deducción de los dígitos de la clave


Ahora, para cada columna i (de 0 a 15), buscamos el valor de la cabecera PNG en esa columna dentro de los 10 bloques. El número de bloque (0-9) es el dígito de la clave.

i	Cabecera	Buscar en columna i	Bloque	Dígito

0	137	bloque1[0]=137	1	1

1	80	bloque6[1]=80	6	6

2	78	bloque2[2]=78	2	2

3	71	bloque5[3]=71	5	5

4	13	bloque8[4]=13	8	8

5	10	bloque8[5]=10	8	8

6	26	bloque2[6]=26	2	2

7	10	bloque2[7]=10	2	2

8	0	bloque0[8]=0	0	0

9	0	Múltiples: bloque3[9]=0, bloque4[9]=0, bloque5[9]=0	3,4,5	?

10	0	Múltiples: bloque1[10]=0, bloque2[10]=0, bloque3[10]=0	1,2,3	?

11	13	bloque6[11]=13	6	6

12	73	bloque9[12]=73	9	9

13	72	bloque6[13]=72	6	6

14	68	bloque3[14]=68	3	3

15	82	bloque5[15]=82	5	5


Las posiciones 9 y 10 son ambiguas (múltiples candidatos 0). Para i=9: {3,4,5}; para i=10: {1,2,3}. La clave parcial es:

* * * * * * * * * * * * * * * * con X∈{3,4,5}, Y∈{1,2,3}.
### Resolución de ambigüedades


Probamos las combinaciones manualmente en la página web (o con un script). La clave que genera una imagen PNG válida (y no un error) es 1625882204269635. Esto corresponde a X=4, Y=2. Por tanto, la clave completa es:


**************

Generación del código QR


Introducimos la clave en el formulario y la página muestra una imagen. Inspeccionamos el elemento <img id="Area"> y copiamos el contenido del atributo src. Obtenemos:

text


data:image/png;base64,*********************************kAAACfklEQVR4nO2bQWrkQAxFn8aGLG3IAXKU8g1ypCFHmhu4jjIHGCgvAzZ/FlXluDtkkhDH0wZp0dhdb/FBSC2p1CY+Y/HHp3Bw3nnnnXfeeeff4q1Yi1m/GEwtwGIw1bPhQD3O78wHSVICQgKzHmC6E9BIknTJf7ce53fmpxKherI7QTcD3bMBYGbt0Xqc/x7efqbFNLIY0e5kw3/W4/zX+PbqXbEHQlqwkHo7XI/z+/LVv52ACYBmJg6NgDmfbkcgt6bf+X9b8W/MkdpgId3Xj1/3slxEH6fH+X35VxEa+yY/KD48my6j9/b0O/8R3obJjGhmkmbKd/mghdgv3v+ek6/xO4EFLa2FcWlzfxTGpRxsyrBb0+/8O5aHUyGxGWJppBFBM/lVcv+elN/0R8bUAzSz0f0xYp9kdPNFi3xr+p3/CF9TcymtahCvNw3TOsm6Tf3Ov2nbywMaaewk6ErO1khTLx48P5+WL/VVjt/FCGkxoJENLGb2UEqwW9Xv/Ef48LvkYj31TYnpXERPLTYcrsf5r/OlLs4/uPlWsFTNtT/S1jw/n4yv/VGdWpVeN62OX1sj9+8Z+VfxG1av5te0Flnu3xPydW5RfclaRJeCCijltPv3hPw2+b5Msl4NKd2/J+Wv+9+6elXjN6R1Uun+PS+/jp5zk7SOo19mWjYcqcf5nfl1fzI3Sfk6uIVo9elYPc5/D2/D1KKnvgRs7Z58//mk/PX+JPFBWBDA1JviY0JM9/NBepzfl7/en1R8JK/bCfLqxgzds+kYPc7vy79dP+esHOT7G2fmzf/f7bzzzjvvvPOH838BbjLLUSITUmkAAAAASUVORK5CYII=


Extracción de la flag


Guardamos la parte Base64 en un archivo y lo decodificamos a PNG:

bash


echo "*******************************kAAACfklEQVR4nO2bQWrkQAxFn8aGLG3IAXKU8g1ypCFHmhu4jjIHGCgvAzZ/FlXluDtkkhDH0wZp0dhdb/FBSC2p1CY+Y/HHp3Bw3nnnnXfeeeff4q1Yi1m/GEwtwGIw1bPhQD3O78wHSVICQgKzHmC6E9BIknTJf7ce53fmpxKherI7QTcD3bMBYGbt0Xqc/x7efqbFNLIY0e5kw3/W4/zX+PbqXbEHQlqwkHo7XI/z+/LVv52ACYBmJg6NgDmfbkcgt6bf+X9b8W/MkdpgId3Xj1/3slxEH6fH+X35VxEa+yY/KD48my6j9/b0O/8R3obJjGhmkmbKd/mghdgv3v+ek6/xO4EFLa2FcWlzfxTGpRxsyrBb0+/8O5aHUyGxGWJppBFBM/lVcv+elN/0R8bUAzSz0f0xYp9kdPNFi3xr+p3/CF9TcymtahCvNw3TOsm6Tf3Ov2nbywMaaewk6ErO1khTLx48P5+WL/VVjt/FCGkxoJENLGb2UEqwW9Xv/Ef48LvkYj31TYnpXERPLTYcrsf5r/OlLs4/uPlWsFTNtT/S1jw/n4yv/VGdWpVeN62OX1sj9+8Z+VfxG1av5te0Flnu3xPydW5RfclaRJeCCijltPv3hPw2+b5Msl4NKd2/J+Wv+9+6elXjN6R1Uun+PS+/jp5zk7SOo19mWjYcqcf5nfl1fzI3Sfk6uIVo9elYPc5/D2/D1KKnvgRs7Z58//mk/PX+JPFBWBDA1JviY0JM9/NBepzfl7/en1R8JK/bCfLqxgzds+kYPc7vy79dP+esHOT7G2fmzf/f7bzzzjvvvPOH838BbjLLUSITUmkAAAAASUVORK5CYII=" | base64 -d > qr.png


Luego escaneamos el código QR. Podemos usar zbarimg (Linux) o un servicio web como https://webqr.com/. El resultado es:

text


picoCTF{***************************}


### Flag final

text


picoCTF{***************************}


Resumen de la vulnerabilidad


El algoritmo de reordenamiento es débil porque:


```
    Cada columna se procesa independientemente.

    La primera fila del resultado se compone directamente de bytes de los bloques originales según los dígitos de la clave.

    La cabecera fija del PNG permite recuperar cada dígito (o un pequeño conjunto de candidatos) con una simple búsqueda.

    Solo unas pocas combinaciones necesitan probarse manualmente
```

