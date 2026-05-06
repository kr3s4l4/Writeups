# Writeup: Flag_Hunters
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup detallado – Flag Hunters (picoCTF)

1. Contexto y análisis del programa

El programa lyric-reader.py está diseñado como un “lector de letras” interactivo. Su funcionamiento es el siguiente:


```
    Lee la bandera desde un archivo flag.txt.

    La inserta en una cadena de texto llamada secret_intro, que es la primera parte de la canción.

    Define la canción completa song_flag_hunters concatenando secret_intro con el resto de la letra.

    Luego llama a la función reader(song_flag_hunters, '[VERSE1]'), que imprime la letra comenzando desde el verso 1.

```

La clave está en que la bandera se encuentra en secret_intro, pero el programa nunca imprime esa sección porque comienza desde [VERSE1]. La única manera de verla es hacer que el flujo de ejecución salte hacia atrás, a las primeras líneas.

2. La vulnerabilidad (control de flujo)

Dentro de la función reader, cada línea de la canción se divide por punto y coma (;). Cada fragmento se procesa de la siguiente manera:


```
    Si el fragmento es "REFRAIN", se guarda un retorno (se modifica la línea RETURN para que sepa a qué línea volver) y se salta al estribillo.

    Si coincide con "CROWD...", se pide entrada al usuario y se reemplaza esa línea por "Crowd: " + entrada.

    Si coincide con "RETURN <número>", se salta a la línea indicada.

    Si es "END", termina.

    En cualquier otro caso, imprime el fragmento y avanza a la siguiente línea.

```

El punto crítico es que la entrada del usuario (Crowd:) puede contener instrucciones. Cuando el programa procesa de nuevo esa línea (por ejemplo, después de volver del estribillo), interpretará el texto ingresado como si fuera parte de la letra. Si el usuario escribe algo como "RETURN 0", el programa lo detectará y realizará un salto a la línea 0.

3. Estrategia de explotación

Queremos forzar un salto a la línea donde se encuentra la bandera. ¿Cuál es esa línea? Observando el código:

python


secret_intro = \

'''Pico warriors rising, puzzles laid bare,

Solving each challenge with precision and flair.

With unity and skill, flags we deliver,

The ether’s ours to conquer, '''\

+ flag + '\n'


La cadena secret_intro ocupa las primeras líneas de song_flag_hunters. Al dividir en líneas, la bandera se encuentra en una línea que contiene el texto "The ether’s ours to conquer, picoCTF{...}". Si contamos desde 0, esa línea es la línea 3 (aproximadamente, dependiendo del formato exacto). Pero es más fácil saltar directamente a la línea 0: al imprimir desde la línea 0, el programa recorrerá todas las siguientes y mostrará la bandera.


Entonces, en el prompt Crowd:, ingresamos RETURN 0. También podemos incluir un punto y coma al inicio para asegurarnos de que se procese como un fragmento independiente (por ejemplo, ;RETURN 0), aunque en este caso el RETURN 0 por sí solo también funciona porque el fragmento se extrae de la línea completa.

4. Ejecución y resultado

Al conectarnos al servicio remoto con nc verbal-sleep.picoctf.net 59142, vemos que se imprimen los versos y el estribillo. En el primer Crowd: (después del primer estribillo), introducimos ;RETURN 0 y presionamos Enter.


El programa procesa esa línea, interpreta el RETURN 0 y salta a la primera línea. Desde allí imprime todo el contenido, incluyendo secret_intro con la bandera. Después de imprimir la bandera, continúa con el resto de la canción y vuelve a pedir Crowd: nuevamente debido a la estructura de repetición. En cada iteración, el programa se encuentra nuevamente con la línea que contiene ;RETURN 0, por lo que vuelve a saltar a la línea 0 y muestra la bandera una y otra vez en un bucle.


Finalmente, la flag aparece en la salida:

text


picoCTF{*************}


5. Explicación del código (detalle técnico)

```
    La función reader obtiene una lista de líneas de la canción con song.splitlines().

    Busca las posiciones de [VERSE1], [REFRAIN] y RETURN (la línea que indica dónde volver después del estribillo).

    El bucle principal itera sobre song_lines[lip] y divide cada línea por ;.

    Cuando encuentra una instrucción RETURN <n>, actualiza lip con ese número, saltando a la línea correspondiente.

    La entrada del usuario se guarda en song_lines[lip], reemplazando la línea original que contenía CROWD.... Luego, cuando esa línea es procesada nuevamente (porque el flujo vuelve a pasar por ella), su contenido se interpreta como si fueran fragmentos de la canción.

```

6. Conclusión

Este desafío enseña cómo una entrada no validada puede ser interpretada como código de control en un intérprete simple, permitiendo manipular el flujo de ejecución para acceder a información oculta. La flag se obtiene explotando la capacidad de saltar a cualquier línea mediante la instrucción RETURN.

