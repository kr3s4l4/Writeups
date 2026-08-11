🔐 Writeup: JavaScript Authentication 2 - CTF Challenge

📋 Resumen Ejecutivo
Campo	Detalle
Challenge	JavaScript Authentication 2
Categoría	Web - Autenticación
Dificultad	Fácil ⭐
Puntos	10
Técnicas	Análisis de código, Ingeniería Inversa, Bypass de Autenticación

🎯 Objetivo del Challenge

El desafío presenta un sistema de autenticación implementado completamente en JavaScript del lado del cliente. El objetivo es encontrar las credenciales correctas o explotar vulnerabilidades en el código para obtener la bandera.

🔍 Fase 1: Reconocimiento
1.1 Análisis Inicial

Al acceder al reto, nos encontramos con una página web que solicita autenticación. El primer paso es siempre:
bash

# Abrir herramientas de desarrollador
F12 o Ctrl+Shift+I

1.2 Inspección del Código Fuente

Navegando a la pestaña Depurador (Debugger) → login.js, encontramos:
javascript

function connexion(){
    var username = prompt("Username :", "");
    var password = prompt("Password :", "");
    var TheLists = ["********:*********"];
    for (i = 0; i < TheLists.length; i++)
    {
        if (TheLists[i].indexOf(username) == 0)
        {
            var TheSplit = TheLists[i].split(":");
            var TheUsername = TheSplit[0];
            var ThePassword = TheSplit[1];
            if (username == TheUsername && password == ThePassword)
            {
                alert("Vous pouvez utiliser ce mot de passe pour valider ce challenge (en majuscules) / You can use this password to validate this challenge (uppercase)");
            }
        }
        else
        {
            alert("Nope, you're a naughty hacker.")
        }
    }
}

🕵️ Fase 2: Análisis de Vulnerabilidades

2.1 Credenciales en Texto Plano
javascript

var TheLists = ["********:************"];

🔴 Vulnerabilidad Crítica: Las credenciales están almacenadas en texto plano en el código fuente del cliente. Cualquier usuario con acceso a las herramientas de desarrollador puede verlas.

2.2 Validación Débil con indexOf()
javascript

if (TheLists[i].indexOf(username) == 0)

🔴 Vulnerabilidad: El método indexOf() verifica si la subcadena aparece en la posición 0 (al inicio). Esto permite:

    ✅ Username exacto: "***********"

    ✅ Username parcial: "*", "****", "*******" y cualquier prefijo de "**************"

2.3 Lógica Incorrecta del Bucle
javascript

for (i = 0; i < TheLists.length; i++)
{
    if (TheLists[i].indexOf(username) == 0)
    {
        // Código de éxito
    }
    else
    {
        alert("Nope, you're a naughty hacker.")  // ❌ Se ejecuta aunque no sea la iteración correcta
    }
}

🔴 Vulnerabilidad: El else se ejecuta para cada iteración que no coincide, mostrando "Nope" incluso si la autenticación es exitosa. Esto crea confusión y revela información.

⚔️ Fase 3: Explotación
Método 1: Credenciales Directas (Recomendado) ⭐
javascript

// Paso 1: Abrir consola (F12 → Console)
// Paso 2: Ejecutar
connexion();

// Credenciales:
// Username: ************
// Password: **************

// Paso 3: Obtener flag en mayúsculas
// Flag: *************

Resultado:
javascript

alert("Vous pouvez utiliser ce mot de passe pour valider ce challenge (en majuscules)")
// → *************

Método 2: Bypass con Prefijo
javascript

// Debido a la vulnerabilidad de indexOf()
connexion();

// Username: **     // Cualquier prefijo de "*******" funciona
// Password: ****************N

// ⚠️ Funciona porque "**********".indexOf("*") == 0

Método 3: Extracción Directa de la Flag
javascript

// En la consola de DevTools
const credenciales = ["**********:**************"];
const partes = credenciales[0].split(":");
const flag = partes[1].toUpperCase();

console.log(`🏁 Flag: ${flag}`);
// Output: 🏁 Flag: *************

Método 4: Manipulación de Variables
javascript

// Forzar la alerta directamente
alert("Vous pouvez utiliser ce mot de passe pour valider ce challenge (en majuscules)");

// La flag es: **************

Método 5: Script Automatizado
javascript

// Script completo para extraer la flag automáticamente
(function extractFlag() {
    const TheLists = ["*******:************"];
    const [username, password] = TheLists[0].split(":");
    
    console.log("🔍 Credenciales encontradas:");
    console.log(`   Username: ${username}`);
    console.log(`   Password: ${password}`);
    console.log(`\n🏁 FLAG: ${password.toUpperCase()}`);
    
    // Mostrar en alerta
    alert(`🏁 FLAG: ${password.toUpperCase()}`);
    
    return password.toUpperCase();
})();

🎨 Fase 4: Prueba de Concepto (PoC)
PoC Completa
html

<!DOCTYPE html>
<html>
<head>
    <title>PoC - JavaScript Auth Bypass</title>
</head>
<body>
    <h1>🔐 JavaScript Authentication 2 - PoC</h1>
    <button onclick="exploit()">🚀 Ejecutar Exploit</button>
    <div id="output"></div>

    <script>
    function exploit() {
        // El código vulnerable original
        const TheLists = ["***********:*************"];
        const [username, password] = TheLists[0].split(":");
        
        // Extraer flag
        const flag = password.toUpperCase();
        
        // Mostrar resultado
        const output = document.getElementById('output');
        output.innerHTML = `
            <h2>✅ Exploit Exitoso</h2>
            <p><strong>Usuario:</strong> ${username}</p>
            <p><strong>Contraseña:</strong> ${password}</p>
            <p style="color: green; font-size: 24px; font-weight: bold;">🏁 FLAG: ${flag}</p>
            <p style="color: red;">⚠️ Las credenciales están en texto plano en el código fuente</p>
        `;
        
        console.log(`🏁 Flag extraída: ${flag}`);
    }
    </script>
</body>
</html>

🛡️ Fase 5: Análisis de Seguridad

5.1 Vulnerabilidades Identificadas
ID	Vulnerabilidad				Nivel	CVSS
V1	Credenciales en texto plano		Crítico	7.5
V2	Validación débil con indexOf()		Medio	5.3
V3	Lógica de autenticación en cliente	Crítico	8.1
V4	Información expuesta en código		Bajo	3.7

5.2 Impacto

    🔴 Confidencialidad: Las credenciales son visibles para cualquier usuario

    🔴 Autenticación: El sistema es fácilmente eludible

    🔴 Integridad: Cualquier usuario puede obtener la flag

🔧 Fase 6: Corrección y Buenas Prácticas

6.1 Código Vulnerable vs. Seguro

❌ Código Vulnerable:
javascript

var TheLists = ["*********:***********"];  // Credenciales en texto plano
if (TheLists[i].indexOf(username) == 0)  // Validación débil

✅ Código Seguro (Backend):

javascript

// Servidor Node.js con autenticación segura
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;
    
    // Buscar usuario en base de datos
    const user = await User.findOne({ username });
    if (!user) {
        return res.status(401).json({ error: 'Credenciales inválidas' });
    }
    
    // Verificar hash de contraseña
    const validPassword = await bcrypt.compare(password, user.passwordHash);
    if (!validPassword) {
        return res.status(401).json({ error: 'Credenciales inválidas' });
    }
    
    // Generar JWT
    const token = jwt.sign(
        { userId: user.id, role: user.role },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
    );
    
    // Enviar token (HttpOnly cookie)
    res.cookie('token', token, {
        httpOnly: true,
        secure: true,
        sameSite: 'strict',
        maxAge: 3600000
    });
    
    res.json({ success: true });
});

6.2 Mejores Prácticas

    ✅ Autenticación en Backend: Nunca en cliente

    ✅ Contraseñas Hasheadas: Usar bcrypt, argon2, etc.

    ✅ Tokens Seguros: JWT con firma y expiración

    ✅ Cookies HttpOnly: Prevenir XSS

    ✅ Validación Estricta: Usar === para comparaciones

    ✅ Manejo de Errores: No revelar información sensible


📚 Lecciones Aprendidas

Para Desarrolladores:

    🔒 Nunca almacenes credenciales en el código cliente

    🔒 Siempre valida en el servidor, no confíes en el cliente

    🔒 Usa comparaciones estrictas (===) y hashing

    🔒 Implementa autenticación robusta con JWT + cookies HttpOnly

Para Hackers/CTF Players:

    🔍 Siempre revisa el código fuente y JS

    🔍 Usa DevTools para depurar y modificar variables

    🔍 Busca patrones de credenciales en el código

    🔍 Prueba diferentes formas de bypass
