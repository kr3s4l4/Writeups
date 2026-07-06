# Writeup: WebDecode
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

WebDecode – Writeup

1. Descripción del reto

El reto se encuentra en la categoría Web Exploitation. Se nos proporciona una página web (o se nos pide inspeccionar una URL) que contiene un mensaje oculto. El objetivo es encontrar la bandera, que está codificada en Base64 dentro del código fuente.

2. Acceso a la página

Al abrir la página, vemos un sitio simple con un encabezado, menú de navegación y una sección "About". El contenido visible es:


```
    Try inspecting the page!! You might find it there

```

Esto nos da una pista clara: hay que inspeccionar el código fuente con las herramientas de desarrollador del navegador.

3. Inspección del código fuente

Abrimos las herramientas de desarrollador (F12 o clic derecho → Inspeccionar) y examinamos el HTML. Buscamos elementos sospechosos, comentarios o atributos no estándar.


En la sección <section class="about"> encontramos un atributo llamado notify_true:

html


<section class="about" notify_true="cGljb0NURnt3ZWJfc3VjYzNzc2Z1bGx5X2QzYzBkZWRfMWY4MzI2MTV9">


El valor de este atributo es una cadena de caracteres que parece estar codificada. Es común encontrar en retos de CTF datos ocultos en atributos personalizados, comentarios o incluso en el CSS/JS.

4. Identificación del encoding

La cadena cGljb0NURnt3ZWJfc3VjYzNzc2Z1bGx5X2QzYzBkZWRfMWY4MzI2MTV9 tiene las siguientes características:


```
    Solo contiene letras mayúsculas, minúsculas, números y los símbolos + y / (aunque aquí no aparecen), además del carácter = al final.

    Es típica de Base64, un esquema de codificación que representa datos binarios en texto ASCII.

```

Confirmamos que la longitud es múltiplo de 4 y termina con =, lo que indica relleno (padding) en Base64.

5. Decodificación Base64

Existen múltiples formas de decodificar Base64:


```
    Usar la terminal en Linux/macOS:
    echo "cGljb0NURnt3ZWJfc3VjYzNzc2Z1bGx5X2QzYzBkZWRfMWY4MzI2MTV9" | base64 -d

    Usar herramientas online (con cuidado, no subas información sensible en retos reales).

    Usar el propio navegador: atob("cadena") en la consola JavaScript.

```

Al ejecutar la decodificación obtenemos:

text


picoCTF{web_succ3ssfully_d3c0ded_1f832615}


6. Formato de la bandera

La cadena resultante tiene el formato picoCTF{...}, que es el estándar de las banderas en picoCTF. Por lo tanto, hemos encontrado la flag.

Conceptos clave


```
    Inspección de código fuente: Herramienta esencial en retos web para descubrir información oculta.

    Base64: Codificación utilizada para transportar datos binarios de forma segura en texto. Es reversible y no proporciona cifrado real, solo ofuscación simple.

    Atributos personalizados en HTML: Pueden contener datos que el desarrollador deja para scripts, pero a veces se convierten en pistas.

```

### Resolución en terminal (opcional)


Si prefieres hacerlo desde la línea de comandos:

bash


```bash
$ echo "cGljb0NURnt3ZWJfc3VjYzNzc2Z1bGx5X2QzYzBkZWRfMWY4MzI2MTV9" | base64 -d
```

picoCTF{web_succ3ssfully_d3c0ded_1f832615}


Conclusión


El reto es sencillo y está diseñado para enseñar a los participantes a inspeccionar el código fuente y reconocer codificaciones comunes como Base64. La bandera final es:

text


picoCTF{********************}

