# Writeup: Unminify
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Unminify – Writeup

Descripción del reto


```
    I don't like scrolling down to read the code of my website, so I've squished it. As a bonus, my pages load faster! Browse here, and find the flag!

```

Se nos proporciona una página web que contiene la bandera, pero el código HTML está minificado (todo en una sola línea, sin espacios ni saltos). El objetivo es encontrar la flag.

### Análisis


Al cargar la página, vemos un mensaje simple y un logo, pero la flag no es visible directamente. Para encontrar pistas ocultas en el código fuente, debemos inspeccionarlo.

1. Ver el código fuente

En cualquier navegador podemos presionar Ctrl+U (o Cmd+Option+U en Mac) para ver el código fuente de la página. También podemos usar las herramientas de desarrollador (F12) y revisar la pestaña Elements.


El código se ve así (minificado):

html


<!doctype html><html lang="en"><head>...<style>body{font-family:"Lucida Console",Monaco,monospace}h1,p{color:#000}</style></head><body class="picoctf{}" style="margin:0">...<p class="picoCTF{pr3tty_c0d3_51d374f0}"></p>...</body></html>


2. “Unminificar” el código

La minificación elimina espacios en blanco, saltos de línea y comentarios para reducir el tamaño. Para leerlo mejor, podemos formatearlo con una herramienta online o manualmente agregando saltos de línea.


Usando un formateador de HTML (o simplemente el inspector de elementos del navegador), obtenemos una versión legible. En las herramientas de desarrollador, la pestaña Elements ya muestra el código con formato.

3. Encontrar la flag

Una vez formateado, buscamos partes sospechosas. En este caso, la flag está dentro de un atributo class de un elemento <p>:

html


<p class="picoCTF{******************}"></p>


A simple vista parece un texto sin contenido, pero el valor del atributo class contiene la flag completa.

### Solución


Conclusión


Este reto enseña la importancia de inspeccionar el código fuente de las páginas web y cómo la minificación puede ocultar información valiosa. Siempre es recomendable “embellecer” (beautify) el código para analizarlo correctamente.

