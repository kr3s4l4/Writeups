# Writeup: GET_aHEAD
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

🧩 Descripción del reto


Nombre: GET aHEAD

Autor: madStacks

Descripción original: Find the flag being held on this server to get ahead of the competition

URL del servidor: http://wily-courier.picoctf.net:53031/


El reto juega con el doble sentido de “get ahead” (adelantarse) y el método HTTP HEAD. La flag está oculta en las cabeceras de respuesta cuando se utiliza el método HEAD en lugar del habitual GET.

🧠 Concepto clave: métodos HTTP GET y HEAD


```
    GET: Solicita un recurso. El servidor devuelve código de estado, cabeceras y cuerpo (el contenido de la página).

    HEAD: Idéntico a GET, pero el servidor solo devuelve las cabeceras, sin el cuerpo. Es útil para obtener metadatos sin descargar todo el contenido.

```

En este desafío, el servidor responde con la flag en una cabecera personalizada cuando se usa el método HEAD, no cuando se usa GET. El nombre del reto es una pista directa.

🛠️ Herramientas necesarias


```
    Navegador web (para inspeccionar las peticiones con F12 > Red)

    curl (línea de comandos, disponible en Linux/macOS/WSL)

    Burp Suite (opcional, pero útil para modificar peticiones)

```

📝 Proceso paso a paso

1. Acceder al servidor con el navegador

Al abrir http://wily-courier.picoctf.net:53031/ vemos una página web simple. Si inspeccionamos con F12 > Red, vemos que la petición inicial es un GET y la respuesta es el código HTML. No aparece ninguna flag en las cabeceras de respuesta.

2. Probar con curl usando método HEAD

Abrimos una terminal y ejecutamos:

bash


curl -I http://wily-courier.picoctf.net:53031/


La opción -I hace una petición HEAD. La salida muestra solo las cabeceras:

text


## Http/1.1 200 ok

### flag: picoCTF{r3j3ct_th3_du4l1ty_8b13f07}

Content-Type: text/html; charset=utf-8

...


¡Ahí está la flag! En la cabecera **flag**:.

3. Verificar con Burp Suite (opcional)

```
    Configurar Burp como proxy.

    Navegar a la URL, interceptar la petición.

    Cambiar el método de GET a HEAD.

    Enviar la petición y observar en la pestaña Response → Headers.

```

4. Incluso desde el navegador (sin herramientas externas)

Aunque el navegador por defecto hace GET, se puede simular un HEAD con herramientas de desarrollador:


```
    Abrir F12 > Red.

    Hacer clic derecho en la petición original → Editar y reenviar.

    Cambiar el método a HEAD y enviar.

    La respuesta mostrará las cabeceras, donde aparecerá flag: ....

```

🏁 Flag

text


picoCTF{*************}


💡 Lecciones aprendidas


```
    Los métodos HTTP no se limitan a GET y POST; conocer HEAD puede ser clave en retos CTF.

    Las cabeceras de respuesta pueden contener información sensible si el servidor está mal configurado.

    Herramientas como curl y Burp Suite permiten modificar peticiones de forma rápida y efectiva.
```

