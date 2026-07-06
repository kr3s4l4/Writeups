# Writeup: Search_source
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Nombre del reto: Search source


Categoría: Web Exploitation / Forensics

Puntos: (por defecto 100)

Autor: Mubarak Mikail

Descripción:


```
    El desarrollador de este sitio web dejó accidentalmente un artefacto importante en el código fuente del sitio. ¿Puedes encontrarlo?

```

Enlace del reto: http://saturn.picoctf.net:51735/ (El puerto puede variar, en mi caso fue el 65023)

Objetivo


Encontrar la flag que está oculta en algún lugar del código fuente del sitio web.

### Solución paso a paso

1. Inspección inicial del sitio

Al abrir la URL en el navegador, vemos una página de plantilla de yoga (Flexed).

Usamos las herramientas de desarrollador (F12) para ver el código HTML.


En el HTML encontramos un comentario sospechoso:

html


<!-- six_box end six_box The flag is not here but keep digging :) -->


Nos indica explícitamente que la flag NO está en esa sección, pero que sigamos "cavando" (digging). Esto sugiere que debemos examinar otros archivos que carga la página.

2. Listado de recursos externos

En el <head> y al final del HTML vemos que se cargan varios archivos:


```
    Hojas de estilo:
    css/bootstrap.min.css, css/owl.carousel.min.css, css/style.css, css/responsive.css

    Scripts:
    js/jquery.min.js, js/popper.min.js, js/bootstrap.bundle.min.js, js/owl.carousel.min.js, js/custom.js, js/jquery.mCustomScrollbar.concat.min.js, js/jquery-3.0.0.min.js, y además Google Maps API.

```

También hay imágenes y el código JavaScript de Google Maps con una API key expuesta, pero esa es una pista falsa.

3. Búsqueda sistemática con curl y grep

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/medium/Search_source]
```

```bash
└─# curl http://saturn.picoctf.net:65023/css/style.css | grep -i pico
```


```
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
```

/** banner_main picoCTF{**************************} **/

100  10449 100  10449   0      0  26204      0 


La salida muestra:

css


/** banner_main picoCTF{******************************} **/


¡Encontrado! La flag está dentro de un comentario en el archivo css/style.css.

4. Verificación manual

Si abrimos directamente http://saturn.picoctf.net:65023/css/style.css en el navegador, vemos el contenido del CSS. Buscando la línea con "banner_main" encontramos el comentario que contiene la flag.

