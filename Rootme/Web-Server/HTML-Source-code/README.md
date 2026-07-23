📄 Writeup: HTML - Source code
🏷️ Información del Desafío
Campo	Detalle
Nombre	HTML - Source code
Categoría	Web-Serveur
Dificultad	47% de éxito (Muy Fácil)
Autor	g0uZ
Fecha	3 de octubre de 2006
Puntos	5
Validaciones	187,013
🎯 Objetivo

El objetivo es encontrar la contraseña oculta para acceder al sistema y validar el desafío. La pista está en el propio enunciado: "Don't search too far" (No busques demasiado lejos).
🕵️ Análisis Inicial

Al acceder a la URL del desafío:
text

http://challenge01.root-me.org/web-serveur/ch1/

Nos encontramos con una página muy simple que muestra:

    Un encabezado con el título "Login v0.00001"

    Un formulario con un campo de contraseña (tipo password)

    Un botón "login"

No hay más elementos visibles en la interfaz. La pregunta es: ¿dónde está la contraseña?
🔍 Inspección del Código Fuente

El enunciado ya nos da una pista muy clara: "Don't search too far". Esto sugiere que la respuesta está en un lugar obvio y accesible.

El primer paso en cualquier desafío web es inspeccionar el código fuente. Podemos hacerlo de varias formas:

    Atajo de teclado: Ctrl + U (en la mayoría de navegadores)

    Clic derecho → Ver código fuente de la página

    Prefijo en la URL: view-source:http://challenge01.root-me.org/web-serveur/ch1/

Al abrir el código fuente, encontramos lo siguiente:
html

<html>
<body>
    <link rel='stylesheet' property='stylesheet' id='s' type='text/css' href='/template/s.css' media='all' />
    <iframe id='iframe' src='https://www.root-me.org/?page=externe_header'></iframe>

    <!--
        Bienvenue sur ce portail,
        Welcome on this portal,

        J'espère que vous passerez un agréable moment parmi nous, mais surtout que vous repartirez plein de choses dans la tête...
        I hope that you will enjoy your time among us, and above that all you will leave with lots of things in the head ...

        @ très bientôt
        See ya
    -->

    <h1>Login v0.00001</h1>

    <form>
        Password&nbsp;<input type="password" value="" name="password"/><br/>
        <input type="submit" value="login" />
    </form>

    <!--
        Je crois que c'est vraiment trop simple là !
        It's really too easy !
        password : ******************
    -->
</body>
</html>

🧐 Análisis del Código Fuente

Observamos dos comentarios en HTML:

    Primer comentario: Un mensaje de bienvenida bilingüe (francés/inglés). Es solo texto informativo.

    Segundo comentario: ¡Aquí está la clave! Contiene:
    text

    Je crois que c'est vraiment trop simple là !
    It's really too easy !
    password : ********************

    Traducción:

        "Creo que es realmente demasiado simple"

        "It's really too easy!"

        Contraseña: *********************

🔑 Validación del Desafío

Una vez descubierta la contraseña:

    Volvemos a la página principal.

    Introducimos ********************* en el campo Password.

    Hacemos clic en el botón "login".

La página nos muestra el mensaje de confirmación:

    "Vous pouvez valider ce challenge avec ce mot de passe / You can validate the challenge using this password"

🧠 Lección Aprendida

Este desafío es una introducción perfecta a la seguridad web y enseña una lección fundamental:

    Nunca almacenes información sensible (contraseñas, claves, tokens) en el código fuente HTML, ni siquiera dentro de comentarios.

Los comentarios HTML son visibles para cualquier usuario que inspeccione la página, ya sea mediante:

    Ctrl+U (ver fuente)

    Herramientas de desarrollo (F12)

    Clientes HTTP como curl o wget

Los comentarios deben usarse solo para documentación interna que no afecte a la seguridad.
