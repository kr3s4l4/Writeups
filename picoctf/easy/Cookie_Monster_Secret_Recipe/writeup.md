# Writeup: Cookie_Monster_Secret_Recipe
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Cookie Monster Secret Recipe (picoCTF)

Introducción


En este desafío de picoCTF, se nos presenta un sitio web que contiene una galleta (cookie) con un mensaje oculto. El objetivo es encontrar la bandera (flag) inspeccionando las cookies almacenadas por el navegador y descifrando su contenido.

Herramientas necesarias


```
    Navegador web (Chrome, Firefox, etc.) con herramientas de desarrollador (F12).

    Terminal de Linux (o cualquier entorno con base64).

    Conocimientos básicos de codificación Base64 y URL encoding.

```

### Pasos a seguir

1. Acceder al sitio web del desafío

Primero, se carga la página correspondiente al reto. Normalmente, este tipo de desafíos incluye un pequeño sitio que coloca una cookie con información codificada.

2. Inspeccionar las cookies

Una vez en la página, se abren las herramientas de desarrollador con la tecla F12. Luego:


```
    En la pestaña Application (o Storage, según el navegador), se busca la sección Cookies.

    Se selecciona el dominio del sitio y se observa la lista de cookies.
    En este caso, encontramos una cookie con un nombre sugerente (p.ej., secret o recipe) y un valor similar a:
    text

    cGljb0NURntjMDBrMWVfbTBuc3Rlcl9sMHZlc19jMDBraWVzXzJDODA0MEVGfQ%3D%3D

    Notamos que el valor termina con %3D%3D, que es la representación URL-encoded del símbolo =. Esto indica que el contenido está codificado en Base64 y luego aplicado URL encoding.

```

3. Decodificar la cookie

El valor de la cookie se debe procesar en dos pasos:


```
    Primero, reemplazar %3D por = (o usar una herramienta que decodifique URL automáticamente).

    Luego, aplicar decodificación Base64.

```

En la terminal, podemos hacerlo de la siguiente manera:

bash


echo "cGljb0NURntjMDBrMWVfbTBuc3Rlcl9sMHZlc19jMDBraWVzXzJDODA0MEVGfQ%3D%3D" | sed 's/%3D/=/g' | base64 -d


O, si se prefiere, se puede decodificar la URL primero con una herramienta como python3 -c "import urllib.parse; print(urllib.parse.unquote('...'))" y luego pasar el resultado a base64 -d.


En el ejemplo del usuario, directamente se usó:

bash


echo cGljb0NURntjMDBrMWVfbTBuc3Rlcl9sMHZlc19jMDBraWVzXzJDODA0MEVGfQ%3D%3D | base64 -d


Aunque apareció un mensaje de error (base64: entrada inválida) debido a los caracteres %, el resultado igualmente se mostró porque base64 ignoró los caracteres no válidos y decodificó la parte válida. Para evitar errores, es mejor limpiar primero la cadena.


El resultado de la decodificación es:

text


picoCTF{*************************}


Conclusión


Este desafío muestra la importancia de revisar las cookies almacenadas por los sitios web, ya que a veces contienen información sensible o datos codificados. La combinación de URL encoding y Base64 es común para ofuscar contenido, pero es fácilmente reversible con herramientas estándar.

