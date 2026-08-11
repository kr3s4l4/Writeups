Writeup: Javascript - Authentication (Root-Me)

📋 Información del Reto
Campo	Detalle
Nombre	Javascript - Authentication
Plataforma	Root-Me
Categoría	Web - Client
Nivel	5 puntos (Muy Fácil)
Autor	g0uZ
Fecha	8 octubre de 2006
Dificultad	★☆☆☆☆
Validaciones	180136 intentos - 46% éxito

🎯 Objetivo

El reto consiste en un formulario de autenticación cuya validación se realiza completamente en el lado del cliente mediante JavaScript. Nuestra misión es encontrar las credenciales correctas para obtener la bandera (flag) de validación.

🔍 Reconocimiento Inicial
1. Análisis de la Página

Al acceder al reto, nos encontramos con un formulario de login básico que solicita:

    Usuario (pseudo)

    Contraseña (password)

    Un botón para validar las credenciales

https://www.root-me.org/IMG/logo/siteon0.svg

2. Primeras Observaciones

    El título indica "Javascript - Authentication", lo que sugiere que la autenticación se maneja con JavaScript

    El formulario parece simple, sin envío de datos a un servidor

    Es probable que la validación esté en el código fuente

🛠️ Metodología de Resolución

Paso 1: Inspección del Código Fuente

La técnica más básica y efectiva es inspeccionar el código fuente de la página.

Acción realizada:

    Click derecho → "Inspeccionar" o presionar F12

    Navegar a la pestaña "Fuentes" (Sources)

    Explorar los archivos cargados

Hallazgo:
Encontramos un archivo llamado login.js que contiene la lógica de autenticación:
javascript

/* <![CDATA[ */

function Login(){
    var pseudo = document.login.pseudo.value;
    var username = pseudo.toLowerCase();
    var password = document.login.password.value;
    password = password.toLowerCase();
    
    if (pseudo == "**********" && password == "***********") {
        alert("Password accepté, vous pouvez valider le challenge avec ce mot de passe.\nYou can validate the challenge using this password.");
    } else { 
        alert("Mauvais mot de passe / wrong password"); 
    }
}
/* ]]> */

Paso 2: Análisis del Código

Desglosemos el código para entender su funcionamiento:
Variables
javascript

var pseudo = document.login.pseudo.value;      // Obtiene el usuario del formulario
var username = pseudo.toLowerCase();           // Convierte usuario a minúsculas (no usado)
var password = document.login.password.value;  // Obtiene la contraseña
password = password.toLowerCase();            // Convierte contraseña a minúsculas

Condición de Validación
javascript

if (pseudo == "**************" && password == "******************") {
    // Éxito: Credenciales correctas
} else {
    // Error: Credenciales incorrectas
}

Paso 3: Identificación de Credenciales

Del código podemos extraer las credenciales correctas:
Campo		Valor Correcto		Notas
Usuario		***********		Exactamente como está (con números)
Contraseña	***********		Case-insensitive (tolera mayúsculas/minúsculas)

Observaciones importantes:

    La variable username se crea pero no se usa en la validación

    La contraseña se convierte a minúsculas, por lo que Sh.OrG también funcionaría

    El usuario debe ser exactamente ********** (no acepta variaciones)

🚀 Métodos de Explotación

Método 1: Credenciales Directas (Recomendado)

Pasos:

    Introducir ********** en el campo de usuario

    Introducir ********** en el campo de contraseña

    Hacer clic en el botón "Login"

Resultado:
text

✅ Password accepté, vous pouvez valider le challenge avec ce mot de passe.
You can validate the challenge using this password.

Método 2: Modificación en Tiempo Real (Consola)

Si queremos ser más "hackers", podemos modificar la lógica directamente:
javascript

// Sobrescribir la función Login
function Login() {
    alert("✅ ¡Acceso concedido! La bandera es: FLAG{...}");
}

Ejecutar en la consola:

    Abrir la consola (Ctrl+Shift+I → pestaña "Console")

    Pegar el código anterior

    Presionar Enter

    Hacer clic en el botón "Login"

Método 3: Depuración Paso a Paso

Procedimiento:

    Ir a la pestaña "Sources" en DevTools

    Abrir login.js

    Establecer un breakpoint en la línea if (pseudo == "************" && password == "************")

    Introducir cualquier usuario/contraseña y hacer clic en Login

    La ejecución se detendrá en el breakpoint

    Modificar los valores de pseudo y password en el panel de Scope

    Continuar la ejecución

Método 4: Extracción Directa

En la consola, podemos ver las credenciales directamente:
javascript

// Mostrar las credenciales del código
console.log("Usuario: **********");
console.log("Contraseña: **********");

📊 Análisis de Vulnerabilidades

Este reto expone varias vulnerabilidades críticas de seguridad:
1. Validación en el Cliente ❌

    Problema: Toda la lógica de autenticación está en JavaScript

    Riesgo: El usuario puede ver y modificar el código

    Solución: La autenticación debe realizarse en el servidor

2. Credenciales en Texto Plano ❌

    Problema: Las credenciales están escritas directamente en el código

    Riesgo: Cualquier usuario puede extraerlas fácilmente

    Solución: Almacenar hashes de contraseñas en el servidor

3. Case-Insensitive Password ❌

    Problema: La contraseña se convierte a minúsculas

    Riesgo: Reduce significativamente la seguridad

    Solución: Mantener el case-sensitive

4. No hay Control de Intentos ❌

    Problema: Se pueden hacer intentos ilimitados

    Riesgo: Vulnerable a ataques de fuerza bruta

    Solución: Implementar límite de intentos y captcha

🏆 Resultado Final
Credenciales Correctas
text

👤 Usuario: **********
🔑 Contraseña: **********
