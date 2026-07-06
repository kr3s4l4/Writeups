# Writeup: Local_Authority
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Local Authority (picoCTF)

Descripción del reto


El reto presenta una página web de login con validación de credenciales. El objetivo es acceder al panel de administración y obtener la flag.

### Análisis inicial


Al cargar la página principal, se muestra un formulario de login y un mensaje de error. Inspeccionando el código fuente (Ctrl+U) se encuentra el siguiente bloque JavaScript:

html


<script type="text/javascript">

```
  function filter(string) {
    filterPassed = true;
    for (let i =0; i < string.length; i++){
      cc = string.charCodeAt(i);
      if ( (cc >= 48 && cc <= 57) ||
           (cc >= 65 && cc <= 90) ||
           (cc >= 97 && cc <= 122) )
      {
        filterPassed = true;     
      }
      else
      {
        return false;
      }
    }
    return true;
  }

  window.username = "admin";
  window.password = "admin";
  
  usernameFilterPassed = filter(window.username);
  passwordFilterPassed = filter(window.password);
  
  if ( usernameFilterPassed && passwordFilterPassed ) {
    loggedIn = checkPassword(window.username, window.password);
    if(loggedIn) {
      document.getElementById('msg').innerHTML = "Log In Successful";
      document.getElementById('adminFormHash').value = "2196812e91c29df34f5e217cfd639881";
      document.getElementById('hiddenAdminForm').submit();
    } else {
      document.getElementById('msg').innerHTML = "Log In Failed";
    }
  } else {
    document.getElementById('msg').innerHTML = "Illegal character in username or password."
  }
```

</script>


El script intenta hacer login automáticamente con admin/admin. Pero como la función checkPassword no está definida en este archivo, se asume que está en otro script: <script src="secure.js"></script>.

Obtención de secure.js


Se accede directamente al archivo secure.js (por ejemplo, https://sitio.com/secure.js). Su contenido es:

javascript


function checkPassword(username, password)

{

```
  if( username === 'admin' && password === 'str************8765' )
  {
    return true;
  }
  else
  {
    return false;
  }
```

}


Aquí se revelan las credenciales válidas:


```
    Usuario: admin

    Contraseña: str**************8765

```

Acceso al panel


Al introducir manualmente esas credenciales en el formulario de login, la página ejecuta la validación correctamente y envía un formulario oculto con el hash 2196812e91c29df34f5e217cfd639881. Este hash probablemente es la flag cifrada o un token que el servidor procesa para mostrar la flag.


Tras el envío, la página muestra la flag en formato picoCTF{...} (o en su caso, la respuesta del servidor).

### Flag


picoCTF{**********************}


Conclusión


El reto enseña la importancia de revisar los archivos JavaScript externos y no confiar en la lógica del lado del cliente. Al inspeccionar el código fuente y localizar secure.js, se encontraron las credenciales en texto claro, permitiendo el acceso y la obtención de la flag.

