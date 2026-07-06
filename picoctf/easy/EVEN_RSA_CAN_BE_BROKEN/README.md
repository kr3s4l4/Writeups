# Writeup: EVEN_RSA_CAN_BE_BROKEN
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Write-up: Even RSA Can Be Broken

Descripción del reto


Se nos proporciona un servicio netcat que devuelve:


```
    Módulo N

    Exponente público e = 65537

    Criptograma c

```

El nombre del reto Even RSA Can Be Broken (el RSA par puede romperse)

sugiere que el módulo es par, es decir, que uno de los factores primos es 2.

Conexión inicial


Al conectar por primera vez:

bash


nc verbal-sleep.picoctf.net 56981


Obtenemos:

text


## N: 14670857079866779846849709672639419723074824373235278491953416688650252601595332417437587317072418800583493385072836590351086582261451967387356749672844066

e: 65537

cyphertext: 11151846610453460255898824075473879675796111758106081990300293177975110819514862786171352366560930395853455681861289947363543086921412076742458107851773765


Observamos que N termina en 66, por lo tanto es par.

Segunda conexión


La primera conexión caducó, así que volvemos a conectar:

bash


nc verbal-sleep.picoctf.net 53450


Ahora obtenemos:

text


## N: 13578423993723997921190791170672572213294202209066357606372747187886337844912192633357827694406362860942390977213053971527295707165646294579520063648110326

e: 65537

cyphertext: 12924432460452098449712937032491018699804503036202257649234658187112321671170404834149523662004956107543762234546622437157070188208772184101041306411133687


Nuevamente, N termina en 26, también es par.

Vulnerabilidad


En RSA, N = p * q con p y q primos. El único primo par es el 2. Por tanto, si N es par, forzosamente uno de los factores es 2. Sin pérdida de generalidad, tomamos p = 2. Entonces:


```
    q = N // 2

    φ(N) = (p-1)*(q-1) = 1 * (q-1) = q-1

    El exponente privado d = e^{-1} mod φ(N)

```

Aunque q no sea primo (en este caso sí lo es), la fórmula funciona porque e y φ(N) son coprimos (lo comprobamos al calcular el inverso).

Ataque


Con p = 2, podemos calcular d y descifrar el mensaje con una simple operación de exponenciación modular.

Script de descifrado (Python)


No es necesario instalar librerías externas; usamos el algoritmo extendido de Euclides para el inverso modular y la conversión a bytes.

python


Fermat.py:


import math


```bash
# Algoritmo de Euclides extendido para inverso modular
```

def egcd(a, b):

```
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

```

def modinv(a, m):

```
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('No existe inverso modular')
    else:
        return x % m

```

```bash
# Datos de la segunda conexión
```

## N = 13578423993723997921190791170672572213294202209066357606372747187886337844912192633357827694406362860942390977213053971527295707165646294579520063648110326

e = 65537

c = 12924432460452098449712937032491018699804503036202257649234658187112321671170404834149523662004956107543762234546622437157070188208772184101041306411133687


```bash
# Factorización trivial
```

p = 2

q = N // p


```bash
# Cálculo de phi y d
```

phi = (p - 1) * (q - 1)   # = q-1

d = modinv(e, phi)


```bash
# Descifrado
```

m = pow(c, d, N)


```bash
# Convertir a texto
```

### flag = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode('utf-8')

print("**Flag**:", flag)


-----------------------------------------------------------------------

Ejecución

bash


python3 Fermat.py


Resultado:

text


### Flag: picoCTF{***********}


Conclusión


El reto muestra una vulnerabilidad clásica: si el módulo RSA es par.

La clave privada se puede obtener de inmediato porque uno de los factores es 2.

Es importante que los generadores de claves RSA siempre escojan primos impares y,

además, que no estén demasiado cerca.

En este caso, el nombre Even hace un juego de palabras entre "par" y "incluso"

(incluso RSA puede romperse).

