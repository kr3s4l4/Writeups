# Writeup: Old_Sessions
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Old Sessions (picoCTF)

Descripción del desafío


El desafío presenta una plataforma de redes sociales cuyo desarrollador implementó una funcionalidad de "nunca cerrar sesión". El objetivo es explotar una mala gestión de sesiones y obtener la bandera (flag).


Pistas proporcionadas:


```
    ¿Sabes usar el inspector web?

    ¿Dónde se almacenan las cookies?

```

Vulnerabilidad


La aplicación presenta dos fallos de seguridad principales:


```
    Las cookies de sesión nunca expiran (tienen fecha de caducidad muy lejana, como se ve en la respuesta HTTP: Expires=Mon, 03 Dec 2057 16:53:14 GMT).

    El endpoint /sessions expone las cookies de sesión de todos los usuarios autenticados (incluido el administrador) a cualquier usuario que haya iniciado sesión.

```

Al robar la cookie de sesión del administrador, un atacante puede hacerse pasar por él y acceder a zonas restringidas donde se encuentra la bandera.

### Pasos para la explotación

1. Acceder a la instancia

La URL proporcionada es, por ejemplo:

http://dolphin-cove.picoctf.net:61799/login

(En tu caso fue ...:61917, pero el proceso es idéntico.)

2. Registrarse como usuario normal

Haz clic en el enlace de registro (o ve directamente a /register). Crea un usuario cualquiera, por ejemplo:


```
    Usuario: test

    Contraseña: test

```

3. Iniciar sesión

Vuelve a la página de login y autentícate con las credenciales recién creadas. El servidor te asignará una cookie de sesión. Puedes verla en las herramientas de desarrollador (F12 → Aplicación → Cookies).

4. Descubrir el endpoint /sessions

Navega a http://dolphin-cove.picoctf.net:61799/sessions. Allí se muestra una lista de todas las sesiones activas en el sistema. Encontrarás algo similar a:

text


Active sessions:

- admin: jLCAvuEKVb9qgCWLoIe7UXMnzsOWOoXmImFHmE2Q3Vo
- test: yR1F9NffoLP_bU2XONCLeltHrpvS_EMwFOJoC-sSWEo

5. Robar la cookie del administrador

Copia el valor de la cookie que corresponde al usuario admin. En el ejemplo anterior sería jLCAvuEKVb9qgCWLoIe7UXMnzsOWOoXmImFHmE2Q3Vo.

6. Reemplazar tu cookie de sesión

En las herramientas de desarrollador (F12), ve a la pestaña Aplicación → Cookies. Localiza la cookie llamada session (o el nombre que tenga la cookie de sesión en la aplicación). Edita su valor y pégalo con el valor robado del administrador.


También puedes hacerlo desde la consola con JavaScript:

javascript


document.cookie = "session=jLCAvuEKVb9qgCWLoIe7UXMnzsOWOoXmImFHmE2Q3Vo; path=/";

location.reload();


7. Obtener la bandera

Una vez recargada la página, ahora estás autenticado como el administrador. Ve a la página principal o a rutas típicas como /flag, /admin, o /dashboard. La bandera aparecerá en algún lugar, por ejemplo en el contenido de la página de inicio.

¿Por qué funciona?


```
    El endpoint /sessions no restringe la visualización de sesiones ajenas; cualquier usuario autenticado puede verlas.

    Las cookies de sesión nunca expiran, por lo que la sesión del administrador sigue siendo válida incluso si inició sesión hace mucho tiempo.

    Al usar su cookie, el servidor te identifica como administrador y te otorga todos sus privilegios.

```

Medidas de mitigación


```
    No exponer las cookies de sesión en ningún endpoint accesible por usuarios no administradores.

    Establecer tiempos de expiración razonables para las sesiones, y rotarlas periódicamente.

    Si se necesita un listado de sesiones, mostrar únicamente las del propio usuario o requerir privilegios de administrador para ver todas.

```

Bandera (flag)


Tras seguir los pasos, la bandera se muestra en la página. Su formato típico es:

text


picoCTF{...}

