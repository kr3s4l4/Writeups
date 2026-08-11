Writeup: Javascript - Obfuscation 1 (Root-Me)

📋 Información del Desafío
Campo	Valor
Nombre	Javascript - Obfuscation 1
Plataforma	Root-Me
Categoría	Web-Client
Dificultad	1/10
Puntos	10
Autor	Hel0ck
Fecha	7 de octubre de 2006
Challengeurs	148,930
Tasa de éxito	38%

🎯 Objetivo

El objetivo de este desafío es encontrar la contraseña oculta en un código JavaScript ofuscado mediante URL Encoding (percent-encoding).

🔍 Análisis Inicial

1. Acceso al Desafío

Al cargar la página del reto, nos encontramos con un prompt pidiendo una contraseña:

https://i.imgur.com/placeholder.png

Figura 1: Ventana emergente solicitando la contraseña

2. Inspección del Código Fuente

Usando F12 → Depurador → ch4.html, encontramos el código completo:
html

<html>
    <head>
        <title>Obfuscation JS</title>
        <script type="text/javascript">
            /* <![CDATA[ */

            pass = '%63%70%61%73%62%69%65%6e%66%75%72%70%61%75%73%76%6f%72%64';
            h = window.prompt('Entrez le mot de passe / Enter password');
            if(h == unescape(pass)) {
                alert('Password accepté, vous pouvez valider le challenge avec ce mot de passe.\nYou can validate the challenge using this pass.');
            } else {
                alert('Mauvais mot de passe / wrong password');
            }

            /* ]]> */
        </script>
    </head>
    <body>
        <link rel='stylesheet' property='stylesheet' id='s' type='text/css' href='/template/s.css' media='all' />
        <iframe id='iframe' src='https://www.root-me.org/?page=externe_header'></iframe>
    </body>
</html>

3. Identificación de la Ofuscación

En la línea clave podemos observar:
javascript

pass = '%63%70%61%74%63%69%65%6e%64%75%72%70%61%73%75%76%6f%72%64';

Esto es URL Encoding (también conocido como percent-encoding), donde cada %XX representa un carácter en hexadecimal.

🛠️ Proceso de Desofuscación

Método 1: Usando el Navegador (DevTools)

    Abrir F12 → Consola

    Ejecutar:

javascript

console.log(unescape('%63%70%63%74%62%69%65%6e%64%75%72%71%61%73%73%76%6f%72%64'));
// Resultado: *********************

https://i.imgur.com/console.png

Figura 2: Decodificación en la consola del navegador
Método 2: Usando Node.js
bash

node -e "console.log(decodeURIComponent('%63%70%61%74%62%69%65%6e%63%75%72%70%61%73%73%76%6f%72%64'))"

Resultado:
text

**************************

https://i.imgur.com/terminal.png

Figura 3: Decodificación usando Node.js
Método 3: Usando Python
bash

python3 -c "import urllib.parse; print(urllib.parse.unquote('%63%70%61%73%62%69%65%6e%64%75%72%70%61%73%73%77%6f%72%64'))"

Resultado:
text

**************************

Método 4: Usando Bash
bash

printf '%b\n' "$(echo '%63%70%69%73%62%63%65%6e%64%75%73%70%61%73%73%76%6f%72%64' | sed 's/%/\\\\x/g')"

Resultado:
text

******************

🔬 Análisis Detallado de la Ofuscación

Tabla de Decodificación
Codificado	Hexadecimal	Carácter|	Codificado	Hexadecimal	Carácter
%63		0x63		*	|	%70		0x70		*
%61		0x61		*	|	%63		0x63		*
%73		0x73		*	|	%74		0x74		*
%63		0x63		*	|	%73		0x73		*
%69		0x69		*	|	%76		0x76		*
%65		0x65		*	|	%6f		0x6F		*
%6e		0x6E		*	|	%72		0x72		*
%64		0x64		*	|	%64		0x64		*

Significado del Resultado

El resultado cpasbiendurpassword es un juego de palabras en francés:
text

c pas bien dur password
→ ce n'est pas bien dur, password
→ "no es muy difícil, contraseña"

¡Ironía del autor! El nombre del reto es "Obfuscation" pero la contraseña es muy fácil de obtener.

✅ Validación de la Solución

1. Ingresar la Contraseña

Al introducir cpasbiendurpassword en el prompt:
javascript

// El prompt recibe: "******************"
// El código compara:
if(h == unescape(pass)) {  // unescape(pass) = "******************"
    alert('Password accepté...');  // ¡Éxito!
}

2. Mensaje de Éxito

Se muestra el mensaje de confirmación:
text

Password accepté, vous pouvez valider le challenge avec ce mot de passe.
You can validate the challenge using this pass.

https://i.imgur.com/success.png

Figura 4: Mensaje de validación exitosa

3. Validación en Root-Me

La contraseña cpasbiendurpassword es aceptada por la plataforma para validar el challenge.

https://i.imgur.com/validate.png

Figura 5: Validación en la plataforma Root-Me

📚 Conceptos Aprendidos

1. URL Encoding (Percent-Encoding)

Características:

    Utiliza % seguido de dos dígitos hexadecimales

    Formato: %XX donde XX es el código ASCII en hexadecimal

    Comúnmente usado en URLs para codificar caracteres especiales

Ejemplos:

    %63 → 'c' (ASCII 99 en decimal, 0x63 en hex)

    %70 → 'p' (ASCII 112 en decimal, 0x70 en hex)

2. Funciones de Decodificación en JavaScript
javascript

// Método antiguo (obsoleto pero funciona)
unescape('%63%70%62%74')  // → "****"

// Método moderno (recomendado)
decodeURIComponent('%63%70%62%74')  // → "****"

// Versión simple: decodeURI (no recomendado para este caso)
decodeURI('%63%70%62%74')  // → "****"

3. Técnicas de Ofuscación Comunes

Técnica			Ejemplo				Dificultad
URL Encoding		%63%70%61%73			Muy Baja
Base64			Y3Bhcw==			Baja
Hexadecimal		\x63\x70\x61\x73		Baja
Unicode			\u0063\u0070\u0061\u0073	Baja
Minificación		Código sin espacios		Media
Eval con arrays		eval(_0xabcd[0])		Alta
