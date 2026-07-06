# Writeup: Client-side-again
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Write-up: Client-side-again (picoCTF)

1. Descripción del reto

Se nos proporciona una página HTML que contiene un formulario de login con un único campo de contraseña. Al hacer clic en "verify", se ejecuta un script JavaScript ofuscado que comprueba si la contraseña es correcta. El objetivo es encontrar la contraseña que muestra el mensaje "Password Verified".

2. Primer vistazo al código

El fragmento relevante es el siguiente:

html


<script type="text/javascript" src="md5.js"></script>

<script type="text/javascript">

```
  var _0x5a46 = ['daf93}', '_again_4', 'this', 'Password\x20Verified', 
                 'Incorrect\x20password', 'getElementById', 'value', 
                 'substring', 'picoCTF{', 'not_this'];
  
  (function(_0x4bd822, _0x2bd6f7) {
    var _0xb4bdb3 = function(_0x1d68f6) {
      while (--_0x1d68f6) {
        _0x4bd822.push(_0x4bd822.shift());
      }
    };
    _0xb4bdb3(++_0x2bd6f7);
  })(_0x5a46, 0x1b3);
  
  var _0x4b5b = function(_0x2d8f05, _0x4b81bb) {
    _0x2d8f05 = _0x2d8f05 - 0x0;
    var _0x4d74cb = _0x5a46[_0x2d8f05];
    return _0x4d74cb;
  };
  
  function verify() {
    checkpass = document[_0x4b5b('0x0')]('pass')[_0x4b5b('0x1')];
    split = 0x4;
    if (checkpass[_0x4b5b('0x2')](0, split * 2) == _0x4b5b('0x3')) {
      if (checkpass[_0x4b5b('0x2')](7, 9) == '{n') {
        if (checkpass[_0x4b5b('0x2')](split * 2, split * 2 * 2) == _0x4b5b('0x4')) {
          if (checkpass[_0x4b5b('0x2')](3, 6) == 'oCT') {
            if (checkpass[_0x4b5b('0x2')](split * 3 * 2, split * 4 * 2) == _0x4b5b('0x5')) {
              if (checkpass['substring'](6, 11) == 'F{not') {
                if (checkpass[_0x4b5b('0x2')](split * 2 * 2, split * 3 * 2) == _0x4b5b('0x6')) {
                  if (checkpass[_0x4b5b('0x2')](0xc, 0x10) == _0x4b5b('0x7')) {
                    alert(_0x4b5b('0x8'));
                  }
                }
              }
            }
          }
        }
      }
    } else {
      alert(_0x4b5b('0x9'));
    }
  }
```

</script>


Observamos que el array _0x5a46 contiene las cadenas que se usarán, pero luego hay una función que lo reordena. También hay una función _0x4b5b que sirve como "desofuscador" devolviendo la cadena correspondiente a un índice del array ya reordenado.

3. Desofuscación: rotación del array

La función anónima recibe el array y 0x1b3 (435 en decimal). Luego hace ++_0x2bd6f7 → 436, y llama a _0xb4bdb3(436).

Dentro de _0xb4bdb3, el bucle while (--n) realiza n-1 rotaciones (porque la primera iteración decrementa antes de comprobar). Por tanto, el número real de rotaciones es 436 - 1 = 435.


Como el array tiene 10 elementos, rotar 435 veces equivale a 435 mod 10 = 5 rotaciones a la izquierda.

Rotar 5 posiciones a la izquierda significa tomar los elementos desde el índice 5 hasta el final y luego los primeros 5.


Array original (índices 0..9):

text


0: 'daf93}'

1: '_again_4'

2: 'this'

3: 'Password Verified'

4: 'Incorrect password'

5: 'getElementById'

6: 'value'

7: 'substring'

8: 'picoCTF{'

9: 'not_this'


Tras rotar 5 a la izquierda:


```
    nuevo[0] = original[5] = 'getElementById'

    nuevo[1] = original[6] = 'value'

    nuevo[2] = original[7] = 'substring'

    nuevo[3] = original[8] = 'picoCTF{'

    nuevo[4] = original[9] = 'not_this'

    nuevo[5] = original[0] = 'daf93}'

    nuevo[6] = original[1] = '_again_4'

    nuevo[7] = original[2] = 'this'

    nuevo[8] = original[3] = 'Password Verified'

    nuevo[9] = original[4] = 'Incorrect password'

```

4. Mapeo de la función _0x4b5b

La función _0x4b5b recibe un string como '0x0', le resta 0 (lo convierte a número) y devuelve _0x5a46[índice]. Por tanto, la correspondencia es:

Código	Índice	Valor real

_0x4b5b('0x0')	0	'getElementById'

_0x4b5b('0x1')	1	'value'

_0x4b5b('0x2')	2	'substring'

_0x4b5b('0x3')	3	'picoCTF{'

_0x4b5b('0x4')	4	'not_this'

_0x4b5b('0x5')	5	'daf93}'

_0x4b5b('0x6')	6	'_again_4'

_0x4b5b('0x7')	7	'this'

_0x4b5b('0x8')	8	'Password Verified'

_0x4b5b('0x9')	9	'Incorrect password'

5. Traducción de la función verify()

Sustituimos cada _0x4b5b(...) por su valor real y simplificamos los cálculos (split = 0x4 = 4):

javascript


function verify() {

```
  checkpass = document.getElementById('pass').value;   // _0x4b5b('0x0') y '0x1'
  split = 4;
  if (checkpass.substring(0, 8) == 'picoCTF{') {            // _0x4b5b('0x3')
    if (checkpass.substring(7, 9) == '{n') {
      if (checkpass.substring(8, 16) == 'not_this') {      // _0x4b5b('0x4')
        if (checkpass.substring(3, 6) == 'oCT') {
          if (checkpass.substring(24, 32) == 'daf93}') {   // _0x4b5b('0x5')
            if (checkpass.substring(6, 11) == 'F{not') {
              if (checkpass.substring(16, 24) == '_again_4') { // _0x4b5b('0x6')
                if (checkpass.substring(12, 16) == 'this') {   // _0x4b5b('0x7')
                  alert('Password Verified');               // _0x4b5b('0x8')
                }
              }
            }
          }
        }
      }
    }
  } else {
    alert('Incorrect password');                           // _0x4b5b('0x9')
  }
```

}


6. Análisis de las condiciones

El script compara subcadenas de la contraseña en posiciones específicas. A continuación, enumeramos cada restricción (índices de caracteres base 0):


```
    substring(0, 8) == "picoCTF{" → los 8 primeros caracteres son picoCTF{.

    substring(7, 9) == "{n" → los caracteres en índices 7 y 8 son { y n.

    substring(8, 16) == "not_this" → índices 8 a 15 = n o t _ t h i s.

    substring(3, 6) == "oCT" → índices 3,4,5 = o, C, T (coherente con el prefijo).

    substring(24, 32) == "daf93}" → índices 24 a 31. La cadena "daf93}" tiene 6 caracteres, pero substring(24,32) devolverá desde 24 hasta el final de la cadena si esta es más corta. Por tanto, la contraseña debe tener al menos hasta el índice 29, y esos 6 caracteres deben ser daf93}.

    substring(6, 11) == "F{not" → índices 6 a 10 = F, {, n, o, t.

    substring(16, 24) == "_again_4" → índices 16 a 23 = _ a g a i n _ 4 (8 caracteres).

    substring(12, 16) == "this" → índices 12 a 15 = t h i s (ya incluido en not_this).

```

7. Reconstrucción de la contraseña (flag)

Unimos todas las posiciones:


```
    Índices 0-7: picoCTF{

    Índice 7 ya es {, índice 8 = n (de la condición 2)

    Índices 8-15: not_this (condición 3) → 8:n, 9:o, 10:t, 11:_, 12:t, 13:h, 14:i, 15:s

    Índices 16-23: _again_4 (condición 7) → 16:, 17:a, 18:g, 19:a, 20:i, 21:n, 22:, 23:4

    Índices 24-29: daf93} (condición 5) → 24:d, 25:a, 26:f, 27:9, 28:3, 29:}

```

La cadena resultante tiene 30 caracteres (índices 0 a 29). La concatenación es:

text


picoCTF{not_this_again_4daf93}


8. Verificación de todas las condiciones

Comprobamos rápidamente con la cadena obtenida:


```
    substring(0,8) → picoCTF{ ✅

    substring(7,9) → índices 7='{', 8='n' → {n ✅

    substring(8,16) → not_this ✅

    substring(3,6) → índices 3='o',4='C',5='T' → oCT ✅

    substring(24,32) → desde índice 24 hasta el final (29) → daf93} ✅

    substring(6,11) → índices 6='F',7='{',8='n',9='o',10='t' → F{not ✅

    substring(16,24) → _again_4 ✅

    substring(12,16) → this ✅

```

Todas las condiciones se cumplen. Por tanto, la contraseña es correcta.

9. Papel de los índices 0, 8 y 9 (descartables)

Dentro del array, los índices tienen diferentes funciones:


```
    Índice 0 ('getElementById'): se usa para acceder al DOM y obtener el campo de entrada.

    Índice 1 ('value'): para leer el valor del campo.

    Índice 2 ('substring'): para llamar al método de cadena.

    Índices 3 a 7: contienen las subcadenas que se comparan con la contraseña.

    Índice 8 ('Password Verified'): mensaje de éxito.

    Índice 9 ('Incorrect password'): mensaje de error.

```

Por lo tanto, los índices 0, 8 y 9 no intervienen en la construcción de la flag y pueden ignorarse por completo durante el análisis de las condiciones. El índice 0 solo es parte de la infraestructura del script, mientras que 8 y 9 son los mensajes de los popups.

10. Respuesta final

La contraseña que hay que introducir en el formulario es:

text


picoCTF{***************************}


Al hacer clic en "verify", aparecerá el mensaje "Password Verified" y el reto se da por superado.


Nota adicional: Aunque el código carga una librería md5.js, nunca se utiliza. Es un señuelo para despistar. La verificación es puramente por comparación de subcadenas.

