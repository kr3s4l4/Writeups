📖 Writeup: Powershell - Basic Jail (Root-Me)
🔐 Información General
Campo	Valor
Reto	Powershell - Basic Jail
Plataforma	Root-Me
Puntuación	25 puntos
Dificultad	1%
Categoría	App-Script
Autor	hat.time

Conexión:
bash

ssh -p 2225 app-script-ch20@challenge05.root-me.org
Contraseña: app-script-ch20

📋 Tabla de Contenidos

    Fase 1: Reconocimiento Inicial

    Fase 2: El Mapeo del WAF

    Fase 3: Entendiendo la Jaula

    Fase 4: Estrategias de Bypass

    Fase 5: El Bypass Definitivo

    Lecciones Aprendidas

Fase 1: Reconocimiento Inicial
🔌 Conexión al Servidor
bash

ssh -p 2225 app-script-ch20@challenge05.root-me.org

Al conectarnos, entramos en un entorno PowerShell con el prompt:
text

PS JAIL:\powershell\restricted>

📂 Listado de Archivos

El primer paso fue explorar el directorio:
powershell

ls

Resultado:
text

PS JAIL:\powershell\restricted> ls

    Directory: C:\cygwin64\challenge\app-script\ch20

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       12/12/2021   9:25 AM             43 .git
-a----        4/20/2020  12:10 PM             22 .passwd
------       12/12/2021   9:50 AM            574 ._perms
-a----        4/20/2020  12:57 PM           3825 ch20.ps1

Archivos encontrados:

    .passwd - Presumiblemente contiene la flag (22 bytes)

    ch20.ps1 - Script principal de la cárcel (3825 bytes)

    ._perms - Archivo de permisos

    .git - Directorio de control de versiones

📝 Primeros Intentos de Lectura
Intento 1: cat
powershell

PS JAIL:\powershell\restricted> cat ch20.ps1

Resultado:
text

c20.ps1 : The term 'c20.ps1' is not recognized...

Observación: ch20.ps1 se transformó en c20.ps1 - ¡La h fue eliminada!
Intento 2: Get-Content
powershell

PS JAIL:\powershell\restricted> Get-Content ch20.ps1

Resultado:
text

GetContent : The term 'GetContent' is not recognized...

Observación: Get-Content se convirtió en GetContent - ¡El guión (-) fue eliminado!
Fase 2: El Mapeo del WAF
🕵️‍♂️ Probando Diferentes Comandos
Prueba con .passwd
powershell

PS JAIL:\powershell\restricted> Get-Content .passwd

Resultado:
text

The term 'GetContent' is not recognized...

Prueba con type y Ruta Completa
powershell

PS JAIL:\powershell\restricted> type "C:\cygwin64\challenge\app-script\ch20\.passwd"

Resultado:
text

C:\cygwin64\callenge\apppt\c20\.passwd

Análisis de la Transformación:
Original	Transformado	¿Qué pasó?
challenge	callenge	Perdió la h
app-script	apppt	Perdió -s-c-r-i
ch20	c20	Perdió la h
🔬 Mapeo Completo del WAF
Prueba con Método .NET
powershell

PS JAIL:\powershell\restricted> [System.IO.File]::ReadAllText(".passwd")

Resultado:
text

iex : At line:1 char:69
+ System.IO.File]::ReadAllText"C:\cygwin64\callenge\apppt\c20\.passwd")
+                                                                     ~
Unexpected token ')'...

Caracteres eliminados: [, (, ) y el punto inicial
Prueba de Concatenación
powershell

PS JAIL:\powershell\restricted> $a = "app" + "cpt"

Resultado:
text

Unexpected token '"cpt"' in expression or statement.

Carácter eliminado: +
Prueba con Módulo de PowerShell
powershell

PS JAIL:\powershell\restricted> Microsoft.PowerShell.Management\Get-Content .passwd

Resultado:
text

croso.PowerSell.Management\GetContent : The module 'croso.PowerSell.Management' could not be loaded.

Transformaciones:

    Microsoft → croso (perdió i, c, r, s)

    PowerShell → PowerSell (perdió h)

📊 Mapa de Caracteres Prohibidos
text

┌──────────────────────────────────────────────────────────┐
│                      WAF CHARACTER MAP                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  SÍMBOLOS PROHIBIDOS:                                    │
│  ┌───────────────────────────────────────────────────┐   │
│  │  [   ]   (   )   -   +                            │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  LETRAS PROHIBIDAS:                                      │
│  ┌───────────────────────────────────────────────────┐   │
│  │  h   s   r   i   c                                │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  EJEMPLOS DE TRANSFORMACIÓN:                             │
│  ┌───────────────────────────────────────────────────┐   │
│  │  Get-Content    →  GetContent                     │   │
│  │  [System.IO]    →  System.IO]                     │   │
│  │  Microsoft      →  croso                          │   │
│  │  challenge      →  callenge                       │   │
│  │  app-script     →  apppt                          │   │
│  │  ch20           →  c20                            │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘

Fase 3: Entendiendo la Jaula
📄 Análisis de ch20.ps1

El script ch20.ps1 es el corazón de la cárcel. Aunque no pudimos leerlo completamente, pudimos inferir su funcionamiento:

Línea 119 del script:
powershell

iex $line

Funcionamiento:

    El script recibe nuestra entrada

    Aplica un filtro que elimina caracteres prohibidos

    Pasa la entrada filtrada a Invoke-Expression (iex)

    iex ejecuta el comando en PowerShell

Problema: El filtro es demasiado agresivo y elimina caracteres necesarios para la sintaxis válida.
📌 Resumen del Funcionamiento
text

┌───────────────────────────────────────────────────────────┐
│                FLUJO DE EJECUCIÓN DE LA JAIL              │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐                                     │
│  │  Usuario escribe │                                     │
│  │  un comando      │                                     │
│  └────────┬─────────┘                                     │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────┐     ┌──────────────────────────┐    │
│  │  Filtro WAF      │────▶│  Elimina: [ ] ( ) - +    │    │
│  │  (Sanitización)  │     │  Elimina: h s r i c      │    │
│  └────────┬─────────┘     └──────────────────────────┘    │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────┐                                     │
│  │  $line = comando │                                     │
│  │  sanitizado      │                                     │
│  └────────┬─────────┘                                     │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────┐                                     │
│  │  iex $line       │  ◄─── Línea 119 del script          │
│  │  (Ejecución)     │                                     │
│  └────────┬─────────┘                                     │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────┐                                     │
│  │  ¡ERROR!         │  ◄─── El comando es inválido        │
│  └──────────────────┘                                     │
│                                                           │
└───────────────────────────────────────────────────────────┘

Fase 4: Estrategias de Bypass
🎯 Estrategia 1: Comodines

Dado que no podemos escribir letras prohibidas, usamos comodines:
powershell

PS JAIL:\powershell\restricted> gc "C:\cygwin64\c*all*ng*\app*c*p*\c*20\.p*w*"

Resultado:
text

C:\cygwin64\c*all*ng*\app*c*p*\c*20\.p*w*

Problema: gc sigue siendo interceptado y el comando solo imprime la ruta como texto.
🎯 Estrategia 2: Uso de Variables
powershell

PS JAIL:\powershell\restricted> $f = gc "C:\cygwin64\c*all*ng*\app*c*p*\c*20\.p*w*"
PS JAIL:\powershell\restricted> $f

Resultado:
text

C:\cygwin64\c*all*ng*\app*c*p*\c*20\.p*w*

Problema: El comando gc no se ejecuta, solo asigna la ruta como texto.
🎯 Estrategia 3: El Acento Grave (`)

El acento grave es un carácter de escape en PowerShell que puede evadir filtros estáticos:
powershell

PS JAIL:\powershell\restricted> g`c C:\cygw??64\*\*\*\.p?w?

Resultado:
text

gc : An object at the specified path C:\cygw??64\*\*\*\.p?w? does not exist...

¡Avance! El comando g``c funcionó y ejecutó Get-Content real. El WAF fue derrotado, pero la ruta no es correcta.
🎯 Estrategia 4: Refinando la Ruta

Ruta real:
text

C:\cygwin64\challenge\app-script\ch20\.passwd

Ruta ofuscada:
text

C:\cygw?n64\*allenge\app*pt\*20\.pa*wd

Desglose:
text

C:\cygw?n64\     →  cygwin64 (sin 'i')
*allenge\        →  challenge (sin 'ch')
app*pt\          →  app-script (sin '-script')
*20\             →  ch20 (sin 'ch')
.pa*wd           →  .passwd (sin 's')

Fase 5: El Bypass Definitivo
🚀 El Comando Ganador
powershell

PS JAIL:\powershell\restricted> g`c C:\cygw?n64\*allenge\app*pt\*20\.pa*wd

Salida:
text

*************

🔍 Análisis del Payload
powershell

g`c                                    # Get-Content con backtick
     C:\cygw?n64\                      # cygwin64 sin la 'i'
                  *allenge\            # challenge sin la 'ch'
                           app*pt\     # app-script sin '-script'
                                   *20\ # ch20 sin 'ch'
                                       .pa*wd  # .passwd sin 's'

Componentes del bypass:
Componente	Propósito
` (backtick) | Escapa el carácter para evadir el WAF |	
?	Reemplaza un solo carácter
*	Reemplaza cualquier cantidad de caracteres
C:\	Ruta raíz
cygw?n64	cygwin64 sin la 'i'
*allenge	challenge sin 'ch'
app*pt	app-script sin '-script'
*20	ch20 sin 'ch'
.pa*wd	.passwd sin 's'
📊 Diagrama del Bypass
text

┌────────────────────────────────────────────────────────────┐
│                   FLUJO DEL BYPASS FINAL                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  COMANDO OFUSCADO:                                 │    │
│  │  g`c C:\cygw?n64\*allenge\app*pt\*20\.pa*wd        │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                    │
│                       ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  WAF: Detecta "g`c" y no lo reconoce como malo     │    │
│  │       No detecta letras prohibidas en la ruta      │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                    │
│                       ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  iex $line: Ejecuta en PowerShell                  │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                    │
│                       ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PowerShell:                                       │    │
│  │  1. Interpreta `g`c` como `gc` (Get-Content)       │    │
│  │  2. Expande los comodines en la ruta               │    │
│  │  3. Encuentra: .passwd                             │    │
│  │  4. Lee y muestra: *************                   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘

Lecciones Aprendidas
🎯 Técnicas Clave para Evadir Jails
Técnica	Descripción	Ejemplo
Acento Grave	Escapa caracteres para evadir filtros	g``c → gc
Comodines	Reemplazan caracteres prohibidos	? = 1 char, * = cualquier cantidad
Ofuscación de Rutas	Construir rutas sin letras prohibidas	C:\cygw?n64\*allenge\...
Análisis de Errores	Leer los errores para mapear el WAF	Identificar caracteres eliminados
