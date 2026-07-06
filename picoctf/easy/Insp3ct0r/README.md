# Writeup: Insp3ct0r
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Inspección de código fuente - Insp3ct0r


En este reto, se nos proporciona una página web que contiene la bandera fragmentada en tres partes: una en el HTML, otra en el CSS y la última en el JavaScript. El objetivo es inspeccionar el código fuente y los archivos vinculados para reconstruir la bandera completa.

Paso 1: Inspeccionar el HTML


Al abrir la página web en el navegador, podemos ver el código fuente presionando Ctrl+U (o haciendo clic derecho y seleccionando "Ver código fuente de la página"). Dentro del HTML, encontramos un comentario que revela la primera parte de la bandera:

html


<!-- Html is neat. Anyways have 1/3 of the **flag**: picoCTF{tru3_d3 -->


Esto nos da el primer fragmento: picoCTF{tru3_d3.

Paso 2: Revisar el archivo CSS


En el <head> del HTML se enlaza un archivo CSS llamado mycss.css. Podemos acceder a él directamente añadiendo /mycss.css a la URL base o desde las herramientas de desarrollador (pestaña "Sources" o "Network"). El contenido del CSS incluye otro comentario con la segunda parte:

css


/* You need CSS to make pretty pages. Here's part 2/3 of the **flag**: t3ct1ve_0r_ju5t */


El fragmento es: t3ct1ve_0r_ju5t.

Paso 3: Analizar el archivo JavaScript


De manera similar, se carga el archivo myjs.js. Al abrirlo, encontramos el último comentario:

javascript


/* Javascript sure is neat. Anyways part 3/3 of the **flag**: _lucky?302945a7} */


Este fragmento es: _lucky?302945a7}.

Paso 4: Concatenar las partes


Uniendo los tres fragmentos en orden:


```
    picoCTF{tru3_d3

    t3ct1ve_0r_ju5t

    _lucky?302945a7}

```

Obtenemos la bandera completa:

text


picoCTF{tru3_d3t3ct1ve_0r_ju5t_lucky?302945a7}


Conclusión


La bandera estaba oculta en los comentarios de los archivos HTML, CSS y JavaScript. Inspeccionando el código fuente y los recursos vinculados se pudo reconstruir fácilmente. Este tipo de retos enseña la importancia de revisar todos los archivos que componen una página web, no solo el HTML visible.

