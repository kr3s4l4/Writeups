Writeup: Root-Me - "Javascript - Source"

📋 Información General

    Plataforma: Root-Me

    Categoría: Web - Client Side

    Dificultad: Muy Fácil (1/5)

    Puntos: 5

    Objetivo: Encontrar la contraseña oculta en el código JavaScript

🎯 Descripción del Reto

El reto consiste en una página web que solicita una contraseña mediante un cuadro de diálogo (prompt). El objetivo es encontrar la contraseña correcta para validar el desafío. La contraseña está oculta en el código fuente del lado del cliente.

🔍 Metodología de Resolución

1. Análisis Inicial

Al acceder a la página, nos encontramos con un cuadro de diálogo que solicita una contraseña:
text

Entrez le mot de passe / Enter password

Si introducimos una contraseña incorrecta, obtenemos el mensaje:
text

Mauvais mot de passe / wrong password !

2. Inspección del Código Fuente

El primer paso lógico es inspeccionar el código fuente de la página. Para ello:
Opción A: Ver Código Fuente HTML

    Click derecho → "Ver código fuente de la página"

    O presionar Ctrl+U (Windows/Linux) o Cmd+Option+U (Mac)

Opción B: Herramientas de Desarrollador (Recomendado)

    Presionar F12 o Ctrl+Shift+I (Windows/Linux)

    O Cmd+Option+I (Mac)

    Ir a la pestaña "Sources" (Depurador)

    Navegar por los archivos hasta encontrar index

3. Análisis del Código

Al examinar el código HTML, encontramos el siguiente script:
html

<html>
    <head>
        <script type="text/javascript">
        /* <![CDATA[ */
            function login(){
                pass=prompt("Entrez le mot de passe / Enter password");
                if ( pass == "******************" ) {
                    alert("Mot de passe accepté, vous pouvez valider le challenge avec ce mot de passe.\nYou can validate the challenge using this password.");  
                }
                else {
                    alert("Mauvais mot de passe / wrong password !");
                }
            }
        /* ]]> */
        </script>
    </head>
    <body onload="login();">
        <!-- Resto del contenido -->
    </body>
</html>

4. Identificación de la Vulnerabilidad

El código revela varios problemas de seguridad:

    Contraseña en texto plano: La contraseña está hardcodeada en el código fuente.

    Validación del lado del cliente: La verificación se realiza en el navegador, no en el servidor.

    Accesibilidad: Cualquier usuario puede ver el código fuente fácilmente.

5. Obtención de la Contraseña

La contraseña es claramente visible en la condición if:
javascript

if ( pass == "**************" )

Contraseña encontrada: ***************

6. Validación del Reto

    Introducir la contraseña ************** en el cuadro de diálogo

    El sistema muestra el mensaje de éxito:
    text

    Mot de passe accepté, vous pouvez valider le challenge avec ce mot de passe.
    You can validate the challenge using this password.

    Validar el reto en la plataforma Root-Me con esta contraseña

🛠️ Herramientas Utilizadas

Herramienta				Uso
Navegador Web				Acceder a la página del reto
Herramientas de Desarrollador (F12)	Inspeccionar código fuente y depurar
Pestaña "Sources"			Visualizar archivos JavaScript

📊 Análisis de Vulnerabilidades

Vulnerabilidades Encontradas
Vulnerabilidad					Impacto				Severidad
Contraseña en texto plano			Exposición de credenciales	Crítica
Validación del lado del cliente			Bypass de seguridad		Alta
Información sensible en código fuente		Fuga de información		Media

Recomendaciones de Seguridad

    ✅ Almacenar contraseñas de forma segura:

        Usar hashing (bcrypt, Argon2, etc.)

        Almacenar solo el hash en la base de datos

    ✅ Validación del lado del servidor:

        Nunca confiar en la validación del cliente

        Implementar autenticación en el backend

    ✅ Ofuscar código sensible:

        Minificar y ofuscar JavaScript

        Usar variables de entorno para secretos

    ✅ Implementar autenticación robusta:

        Sistema de login con sesiones

        Autenticación multifactor (MFA)

        Rate limiting para prevenir ataques de fuerza bruta

💡 Lecciones Aprendidas
Para el Desarrollador

    Nunca almacenar información sensible en el frontend

    La seguridad del lado del cliente es solo una capa adicional, nunca la principal

    Usar siempre autenticación del lado del servidor

Para el Pentester

    Siempre inspeccionar el código fuente en retos web

    Buscar información sensible en:

        Comentarios HTML

        Código JavaScript

        Archivos de configuración

        Peticiones HTTP interceptadas
