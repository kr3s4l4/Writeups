# Writeup: findme
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: FindMe (picoCTF)


Autor: kr3s4l4

Plataforma: picoCTF

Categoría: Web Exploitation

Dificultad: Media

Descripción del desafío


Se nos proporciona un servicio web en http://saturn.picoctf.net:58483. Al acceder, vemos un formulario de login. Introducimos cualquier usuario y contraseña (por ejemplo, test:test!) y el servidor responde con una redirección. El objetivo es encontrar la flag, que está oculta en las sucesivas redirecciones.

### Análisis del tráfico HTTP


Capturé todas las peticiones y respuestas usando un proxy (Burp Suite) o el inspector de red del navegador. A continuación se muestra el flujo completo paso a paso, con las cabeceras exactas.

1. Petición POST a /login
http


POST /login HTTP/1.1

Host: saturn.picoctf.net:58483

Content-Type: application/x-www-form-urlencoded

Content-Length: 30

**Cookie**: session=VZe8OrmeEg8GgY5ajT4ZZLYoLEvaXno9%2FcdFFa9qWrYd3y4lkVwk1FYq1qPs4Ml66wK4cf4byrqalkTeq7Py6PHfpTR3%3BzrbWHV0IlQ%2BxQN%2FhjTPP%2FmdcOCPdMVqd


username=test&password=test%21


Respuesta del servidor:

http


HTTP/1.1 302 Found

Location: /next-page/id=cGljb***************X2Fs

Content-Length: 120


<p>Found. Redirecting to <a href="/next-page/id=cGlj****************X2Fs">...</a></p>


Observamos que el servidor redirige a /next-page/id=cGlj**************X2Fs. El parámetro id parece estar codificado en Base64.

2. Petición GET al primer next-page

Seguimos la redirección automáticamente (o manualmente):

http


GET /next-page/id=cGlj*****************X2Fs HTTP/1.1

Host: saturn.picoctf.net:58483

Referer: http://saturn.picoctf.net:58483/

**Cookie**: session=[...]


Respuesta:

http


## Http/1.1 200 ok

Content-Type: text/html; charset=utf-8

Content-Length: 264


<!DOCTYPE html>

<head>

```
    <title>flag</title>
```

</head>

<body>

```
    <script>
        setTimeout(function () {
           window.location = "/next-page/id=bF90*************TlhfQ==";
        }, 0.5)
      </script>
    <p></p>
```

</body>


La página contiene un JavaScript que, tras medio segundo, redirige a otro id: bF90aGVfd2F5XzI1YmJhZTlhfQ==.

3. Petición GET al segundo next-page
http


GET /next-page/id=bF90*****************TlhfQ== HTTP/1.1

Host: saturn.picoctf.net:58483

Referer: http://saturn.picoctf.net:58483/next-page/id=cGlj****************X2Fs

**Cookie**: session=[...]


Respuesta:

http


## Http/1.1 200 ok

Content-Length: 229


<!DOCTYPE html>

<head>

```
    <title>flag</title>
```

</head>

<body>

```
    <script>
        setTimeout(function () {
           window.location = "/home";
        }, 0.5)
      </script>
      <p></p>
```

</body>


Esta vez redirige a /home, la página principal con el formulario de búsqueda.

4. Petición GET a /home
http


GET /home HTTP/1.1

Host: saturn.picoctf.net:58483

Referer: http://saturn.picoctf.net:58483/next-page/id=bF90**************TlhfQ==

**Cookie**: session=[...]


Respuesta: Código 200 con el HTML de la página principal (contenido irrelevante para la flag).

Decodificación de los parámetros id


Cada uno de los id está codificado en Base64. Podemos decodificarlos directamente en la terminal:

bash


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/medium/findme]
```

```bash
└─# echo cGlj*************X2Fs | base64 -d
```

picoCTF{*********


bash


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/medium/findme]
```

```bash
└─# echo bF90**********TlhfQ== | base64 -d
```

*************}


Obtenemos dos fragmentos de la **flag**:


```
    picoCTF{proxies_al

    l_the_way_25bbae9a}

```

Construcción de la flag


Uniendo los fragmentos en el orden en que aparecen:

text


picoCTF{********* + ************}


Observamos que al seguido de l_ forma all_. Por lo tanto, la flag completa es:


picoCTF{*************************}

Script de automatización (Python)


Aunque no es necesario, podemos automatizar el proceso con el siguiente script:

python


import base64

import requests

import re


url = "http://saturn.picoctf.net:58483"

s = requests.Session()


```bash
# Login con credenciales arbitrarias
```

data = {"username": "test", "password": "test!"}

r = s.post(url + "/login", data=data)


```bash
# Extraer primer id de la Location
```

first_id = r.headers['Location'].split('id=')[1]

part1 = base64.b64decode(first_id).decode()

print(f"Parte 1: {part1}")


```bash
# Seguir a la primera redirección
```

r = s.get(url + "/next-page/id=" + first_id)


```bash
# Extraer segundo id del JavaScript
```

match = re.search(r'/next-page/id=([^"]+)', r.text)

second_id = match.group(1)

part2 = base64.b64decode(second_id).decode()

print(f"Parte 2: {part2}")


### flag = part1 + part2

print(f"**Flag**: {flag}")


Salida del script:

text


Parte 1: picoCTF{***********

Parte 2: **************}

### Flag: picoCTF{**********************}


Nota adicional


La cookie session se mantiene durante todo el proceso pero no es necesaria para obtener la flag (podríamos eliminarla y seguir funcionando). El campo de búsqueda en /home tiene una vulnerabilidad XSS, pero no se requiere para resolver el desafío.

Conclusión


La flag se encuentra fragmentada en las redirecciones del servicio web. Al seguir el flujo y decodificar los IDs en Base64 obtenemos la flag completa:

text


picoCTF{**************************}

