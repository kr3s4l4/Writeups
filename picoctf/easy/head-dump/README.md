# Writeup: head-dump
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

writeup detallado y explicado del desafío head-dump de picoCTF.

Descripción del desafío


```
    En este desafío, explorarás una aplicación web y encontrarás un endpoint que expone un archivo que contiene una bandera oculta. La aplicación es un blog simple donde puedes leer artículos sobre varios temas, incluyendo un artículo sobre "API Documentation". El objetivo es encontrar el endpoint que genera archivos que almacenan la memoria del servidor, donde está escondida la bandera secreta.

```

Categoría: Web Exploitation / Forensics

Dificultad: Easy / Medium

Técnicas involucradas:


```
    Exploración de aplicaciones web

    Lectura de documentación de API (Swagger/OpenAPI)

    Descarga de volcados de memoria (heap dump)

    Búsqueda de strings en archivos binarios

```

Paso 1: Acceder al sitio web


Se nos proporciona una URL similar a:

http://verbal-sleep.picoctf.net:59750/


Al visitarla, vemos un blog llamado "picoCTF News" con varios artículos. Uno de ellos se titula "API Documentation". Este artículo contiene una pista: probablemente la aplicación expone una interfaz Swagger o una documentación de la API.

Paso 2: Encontrar la documentación de la API


Al hacer clic en el artículo "API Documentation", se menciona que la API está documentada en /api-docs/ o en /swagger-ui/. Probamos la ruta:

text


http://verbal-sleep.picoctf.net:59750/api-docs/


Esto muestra la especificación OpenAPI (JSON). Pero a menudo también hay una interfaz amigable en:

text


http://verbal-sleep.picoctf.net:59750/api-docs/#/


Accediendo a esa URL, vemos la interfaz Swagger UI donde se listan los endpoints disponibles. Entre ellos, destaca un endpoint llamado /heapdump con método GET. La descripción indica que genera un volcado del heap (memoria) del servidor.

Paso 3: Descargar el heap dump


Desde la terminal, usamos curl para descargar el archivo generado por ese endpoint:

bash


curl http://verbal-sleep.picoctf.net:59750/heapdump -o heapdump


El comando descarga el contenido y lo guarda en un archivo llamado heapdump. El tamaño suele ser varios megabytes (en este caso ~10.91 MB).

Paso 4: Extraer la bandera


Un heap dump es un archivo binario que contiene volcados de objetos en memoria. La bandera (flag) está almacenada como una cadena de texto en algún lugar de ese volcado. Podemos usar la herramienta strings para extraer todas las secuencias de caracteres imprimibles y luego filtrar por el patrón picoCTF:

bash


strings heapdump | grep picoCTF


El resultado muestra directamente la bandera:

text


picoCTF{****************}


### Explicación técnica


```
    ¿Qué es un heap dump?
    Es una instantánea de la memoria del servidor en un momento dado. Puede contener variables, objetos, datos sensibles, etc. Si la aplicación tiene una vulnerabilidad o un endpoint intencional para depuración (como /heapdump en Spring Boot Actuator), un atacante podría filtrar información confidencial.

    ¿Por qué funciona strings?
    La bandera es texto legible almacenado en memoria. strings extrae cualquier secuencia de 4 o más caracteres imprimibles (por defecto) y las muestra en pantalla. Al filtrar con grep picoCTF, encontramos justo la cadena que buscamos.

    Lección de seguridad:
    Nunca expongas endpoints de diagnóstico (/heapdump, /actuator, /env, /trace, etc.) en entornos de producción sin una autenticación fuerte, ya que pueden revelar secretos.

```

Resumen de comandos útiles

bash


```bash
# 1. Descargar heap dump
```

curl http://verbal-sleep.picoctf.net:59750/heapdump -o heapdump


```bash
# 2. Extraer y buscar la flag
```

strings heapdump | grep picoCTF


-----------------------------------------------------------------------------------------


Usando xxd para encontrar la **flag**:


xxd convierte un archivo binario a representación hexadecimal + ASCII. Puedes usarlo así:

bash


xxd heapdump | grep "picoCTF"


O mejor, buscar en la columna ASCII (la de la derecha) sin mostrar todo el hexadecimal:

bash


xxd -c 256 heapdump | grep -o 'picoCTF{[^}]*}'


Pero xxd muestra todo el archivo línea por línea, lo cual es lento.

Una forma más eficiente es usar xxd con -p (solo hex) y luego convertir, pero es engorroso.

Lo más común es:

bash


xxd heapdump | grep "picoCTF"


Esto mostrará la línea donde aparece la cadena "picoCTF" en la parte ASCII,

y verás la flag completa.


¿Por qué strings es más simple?

strings extrae directamente las cadenas legibles, mientras que xxd requiere que filtres visualmente o con expresiones regulares. Para este desafío, strings es la herramienta adecuada

