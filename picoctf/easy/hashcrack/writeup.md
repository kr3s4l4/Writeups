# Writeup: hashcrack
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: HashCrack – PicoCTF

Descripción del desafío


El reto consiste en conectarse a un servicio remoto mediante netcat. Este servicio nos presenta tres hashes de diferentes algoritmos (MD5, SHA-1 y SHA-256) y nos pide que encontremos la contraseña original para cada uno. Al superar cada fase, obtenemos la bandera final.

Conexión inicial

bash


nc verbal-sleep.picoctf.net 50030


Al conectarnos, el servicio muestra:

text


Welcome!! Looking For the Secret?


We have identified a hash: 482c811da5d5b4bc6d497ffa98491e38

Enter the password for identified hash: 


El primer hash es 482c811da5d5b4bc6d497ffa98491e38. Debemos descifrarlo.

Paso 1: Identificar el tipo de hash


Existen varias herramientas para identificar el algoritmo de un hash. En este caso usamos hash-identifier (también podríamos usar hashid o sitios web).

bash


hash-identifier 482c811da5d5b4bc6d497ffa98491e38


La salida indica que se trata de MD5 (longitud 32 caracteres hexadecimales).

hash-identifier también muestra otras posibilidades, pero por su formato y longitud es claramente MD5.

Paso 2: Craquear el hash con hashcat


Usamos hashcat con el modo MD5 (-m 0) y un ataque de diccionario (-a 0). El diccionario utilizado es rockyou.txt, una lista de contraseñas muy conocida.

bash


hashcat -m 0 -a 0 482c811da5d5b4bc6d497ffa98491e38 /ruta/rockyou.txt


El resultado:

text


482c811da5d5b4bc6d497ffa98491e38:p***w**d**3


La contraseña es p***w**d**3. Introducimos esta contraseña en el servicio y obtenemos:

text


Correct! You've cracked the MD5 hash with no secret found!


### Flag is yet to be revealed!! Crack this hash: b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3

Enter the password for the identified hash: 


Paso 3: Segundo hash (SHA-1)


El nuevo hash es b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3.

Lo identificamos con hash-identifier:

bash


hash-identifier b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3


La herramienta indica que es SHA-1 (también puede ser MySQL5, etc., pero lo común es SHA-1).


En hashcat, el modo para SHA-1 es -m 100. Ejecutamos:

bash


hashcat -m 100 -a 0 b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3 /ruta/rockyou.txt


Resultado:

text


b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3:l*t*e*n


La contraseña es l*t*e*n. La ingresamos y el servicio responde:

text


Correct! You've cracked the SHA-1 hash with no secret found!


Almost there!! Crack this hash: 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745

Enter the password for the identified hash: 


Paso 4: Tercer hash (SHA-256)


El hash es 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745.

Nuevamente usamos hash-identifier:

bash


hash-identifier 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745


La salida indica SHA-256 (64 caracteres hexadecimales).

En hashcat, el modo para SHA-256 es -m 1400.

bash


hashcat -m 1400 -a 0 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745 /ruta/rockyou.txt


Resultado:

text


916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745:q*e*t*0*8


La contraseña es q*e*t*0*8. La ingresamos y el servicio nos da la bandera:

text


Correct! You've cracked the SHA-256 hash with a secret found. 

The flag is: picoCTF{*****************}



Lecciones aprendidas


```
    Los hashes débiles (MD5, SHA-1) y contraseñas comunes (password123, letmein, qwerty098) son fácilmente crackeables con diccionarios como rockyou.txt.

    Es importante identificar correctamente el tipo de hash antes de intentar crackearlo. Herramientas como hash-identifier, hashid o sitios web son útiles.

    Hashcat es una herramienta poderosa que soporta cientos de algoritmos y modos de ataque.

    Para proteger contraseñas, se deben usar algoritmos modernos (como bcrypt, Argon2) y evitar contraseñas comunes.

```

Comandos resumidos

bash


```bash
# MD5
```

hashcat -m 0 -a 0 482c811da5d5b4bc6d497ffa98491e38 rockyou.txt


```bash
# SHA-1
```

hashcat -m 100 -a 0 b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3 rockyou.txt


```bash
# SHA-256
```

hashcat -m 1400 -a 0 916e8c4f79b25028c9e467f1eb8eee6d6bbdff965f9928310ad30a8d88697745 rockyou.txt

