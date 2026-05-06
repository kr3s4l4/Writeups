# Writeup: SQLiLite
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup – SQLiLite (picoCTF)


Autor del reto: Mubarak Mikail

Categoría: Web Exploitation / SQL Injection

Dificultad: Muy fácil / Principiante

🔍 1. Descripción


```
    Can you login to this website? Try to login here.

```

Accedemos a un sitio web con un formulario de login: campos username y password.

El nombre del reto, SQLiLite, ya anticipa que la vulnerabilidad es Inyección SQL.

🧪 2. Primeras pruebas


Enviamos credenciales arbitrarias, por ejemplo:

text


username: prueba

**password**: 1234


La respuesta es un mensaje de error o “Login failed”.

Pero lo interesante es que la propia página nos muestra la consulta SQL que se ejecuta:

text


SQL query: SELECT * FROM users WHERE name='prueba' AND password='1234'


Esto es una pista de depuración muy útil para atacar.

💉 3. Explotación de la SQLi


Probamos el payload clásico:

text


username: kr3s4l4' or 1=1 --

**password**: (lo que sea)


La consulta resultante es:

sql


SELECT * FROM users WHERE name='kr3s4l4' or 1=1 --' AND password='pass'


```
    La comilla simple cierra el string 'kr3s4l4'.

    or 1=1 hace que la condición sea siempre verdadera.

    -- comenta el resto de la consulta (la parte de la contraseña).

```

El resultado: Logged in! ✅


Podemos usar también admin' or 1=1 -- para mayor elegancia.

🚩 4. Obtención de la flag


Después del login, la página muestra:


```
    Logged in! But can you see the flag, it is in plainsight.

```

Inspeccionamos el código fuente de la página (Ctrl+U o clic derecho → Ver código fuente).


Allí encontramos un párrafo oculto con el atributo hidden:

html


<p hidden>Your flag is: picoCTF{************************}</p>


¡Bingo! La flag está a simple vista… en el código fuente.

🧠 5. Explicación técnica (para aprender)


La consulta original vulnerable sería algo como:

sql


SELECT * FROM users WHERE name='$username' AND password='$password'


Al inyectar admin' or 1=1 -- en $username, la consulta se convierte en:

sql


SELECT * FROM users WHERE name='admin' or 1=1 --' AND password='...'


Esto devuelve todos los registros de la tabla users. Como existe al menos un usuario, el sistema da acceso sin necesidad de contraseña.

🛡️ 6. Lecciones de seguridad


```
    ✅ Usar sentencias preparadas (prepared statements) o consultas parametrizadas.

    ✅ No mostrar las consultas SQL al usuario en producción.

    ✅ No confiar en la entrada del usuario ($_POST['username'] en PHP, por ejemplo).

    ✅ Ocultar información en HTML no es seguro si se puede inspeccionar el código fuente.
```

