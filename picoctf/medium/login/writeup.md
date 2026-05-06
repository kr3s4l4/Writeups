# Writeup: login
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup detallado del desafío "login" (PicoCTF)


Se nos proporciona la URL del sitio: login.mars.picoctf.net. Al acceder, vemos un formulario de login simple con campos para usuario y contraseña. Inspeccionando el código fuente (usando la opción view-source o las herramientas de desarrollador), encontramos dos archivos relevantes:


```
    index.html – estructura del formulario.

    index.js – lógica de validación del lado del cliente.

```

El archivo index.js contiene el siguiente código (formateado para claridad):

javascript


(async() => {

```
    await new Promise((e => window.addEventListener("load", e)));
    document.querySelector("form").addEventListener("submit", (e => {
        e.preventDefault();
        const r = {
            u: "input[name=username]",
            p: "input[name=password]"
        };
        const t = {};
        for (const e in r)
            t[e] = btoa(document.querySelector(r[e]).value).replace(/=/g, "");
        return "YWRtaW4" !== t.u
            ? alert("Incorrect Username")
            : "cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ" !== t.p
                ? alert("Incorrect Password")
                : void alert(`Correct Password! Your flag is ${atob(t.p)}.`);
    }));
```

})();


¿Qué hace el código?


```
    Espera a que la página cargue completamente.

    Captura el evento de envío del formulario.

    Impide el envío real (e.preventDefault()), así que la validación es completamente local (no hay verificación en el servidor).

    Toma los valores de los campos username y password, los codifica en Base64 y elimina los signos = al final.

    Compara:

        El username codificado debe ser exactamente "YWRtaW4" (admin).

        El password codificado debe ser exactamente "cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ".

    Si coinciden, muestra una alerta con la flag (decodificando el password desde Base64).

```

Obtención de la flag


Como el password ya está en Base64, solo tenemos que decodificarlo. Podemos hacerlo en la terminal de Linux/macOS o en cualquier decodificador online.


Comando en terminal (Linux/macOS):

bash


echo "cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ" | base64 -d


Resultado:

text


picoCTF{********************************}


También podemos usar JavaScript en la consola del navegador:

javascript


atob("cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ")


¿Por qué el username es YWRtaW4?

Al decodificar YWRtaW4 obtenemos la cadena admin. Esto significa que el usuario esperado es admin. Si probamos a introducir admin como usuario, el código lo codificará a YWRtaW4 y la comparación será correcta.


### Solución paso a paso para obtener la flag manualmente


```
    Abre la página https://login.mars.picoctf.net/.

    Abre las herramientas de desarrollador (F12) y ve a la consola.

    Ejecuta el siguiente comando para decodificar el password:
    javascript

    console.log(atob("cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ"));

    Verás impresa la flag: picoCTF{******************************}.

```

También puedes simplemente introducir en el formulario:


```
    Usuario: admin

    Contraseña: cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ

```

El código JS hará la conversión interna y te mostrará la flag en un alert.


Lección aprendida


```
    Nunca confíes en la validación del lado del cliente para proteger información sensible. Aquí la flag estaba expuesta directamente en el código fuente.

    La codificación Base64 no es cifrado; es solo una representación que cualquiera puede revertir.

    Siempre inspecciona el código fuente y los archivos JavaScript de los sitios CTF; a menudo contienen pistas o incluso las respuestas completas.
```

