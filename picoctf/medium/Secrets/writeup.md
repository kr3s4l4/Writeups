# Writeup: Secrets
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: Secrets (picoCTF)


Descripción del reto:

"Tenemos varias páginas ocultas. ¿Puedes encontrar la que tiene la bandera?"

URL del objetivo: http://saturn.picoctf.net:58199/

Objetivo


Encontrar la bandera (flag) que está en una página oculta dentro del sitio web.

### Resolución paso a paso

1. Reconocimiento inicial

Al cargar la página principal (http://saturn.picoctf.net:58199/), se ve un mensaje sencillo: "You shouldn't be here" (No deberías estar aquí). Esto ya sugiere que hay contenido oculto.

2. Inspección del código fuente

Abrimos las herramientas de desarrollador (F12) y miramos el código HTML de la página principal.

Encontramos un comentario dentro del código:

html


<!-- secret -->


Este comentario indica que probablemente exista un directorio o página llamada secret.

3. Primer directorio oculto

Probamos a acceder a http://saturn.picoctf.net:58199/secret/.

Vemos una nueva página que dice: "Finally. You found me. But can you see me" (Finalmente. Me encontraste. Pero ¿puedes verme?)

Esto confirma que secret es un directorio válido.

4. Búsqueda automatizada con dirb

Para descubrir más rutas ocultas, usamos dirb (herramienta de fuerza bruta sobre directorios). Primero, escaneamos http://saturn.picoctf.net:58199/secret/:

bash


dirb http://saturn.picoctf.net:58199/secret/


El resultado muestra dos directorios interesantes:


```
    http://saturn.picoctf.net:58199/secret/assets/

    http://saturn.picoctf.net:58199/secret/hidden/

```

Además, encuentra index.html dentro de secret/.

5. Segundo directorio oculto

Accedemos a http://saturn.picoctf.net:58199/secret/hidden/.

La página vuelve a mostrar el mismo mensaje: "Finally. You found me. But can you see me".

Esto sugiere que todavía hay más niveles ocultos.

6. Tercer directorio (la bandera)

A continuación, escaneamos http://saturn.picoctf.net:58199/secret/hidden/ con dirb para encontrar subdirectorios adicionales:

bash


dirb http://saturn.picoctf.net:58199/secret/hidden/


Pero en tu caso, el escaneo falló por problemas de conexión (posiblemente porque al encontrar la bandera manualmente o porque el servidor dejó de responder).

Sin embargo, el nombre del siguiente nivel se puede adivinar por el patrón: si secret lleva a hidden, lo lógico sería que hidden lleve a superhidden.

Probamos manualmente: http://saturn.picoctf.net:58199/secret/hidden/superhidden/


¡Y funciona! La página muestra:

text


Finally. You found me. But can you see me ### Asi que inspeccionamos el html y.... 

picoCTF{*********************}


7. Alternativa: inspección visual

Incluso sin dirb, basta con hacer clic derecho y "Ver código fuente" en cada nivel. En el código de secret/hidden/ no hay pistas adicionales, pero la estructura creciente (secret → hidden → superhidden) es una convención común en retos de directorios ocultos. Otra forma es usar un diccionario que contenga la palabra superhidden, o realizar fuzzing con herramientas como gobuster, ffuf o dirb con una wordlist más amplia.

8. Bandera final

La bandera está clara en el html de la página:

text


picoCTF{****************************}


### Explicación del error en tu escaneo


Al final de tu ejecución de dirb sobre hidden/ apareció (Possible cause: COULDNT CONNECT). Esto puede deberse a que ya habías accedido a la página final y el servidor dejó de aceptar conexiones (algunos CTF cierran el contenedor tras obtener la flag) o a un timeout temporal. En condiciones normales, si la palabra superhidden estuviera en el diccionario common.txt de dirb, la habría encontrado. Como no está, se necesita una wordlist más completa o adivinación manual.

Conclusión


El reto enseña la importancia de:


```
    Revisar comentarios en el código fuente.

    Explorar directorios manualmente cuando hay pistas.

    Usar herramientas de enumeración (dirb, gobuster) para descubrir rutas no enlazadas.

    Pensar en patrones de nombres (secret → hidden → superhidden)
```

