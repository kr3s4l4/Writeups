# Writeup: Shared_Secrets
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Shared Secrets (picoCTF)

Descripción del reto


El reto Shared Secrets presenta un intercambio de claves Diffie-Hellman. Se nos proporciona un archivo message.txt que contiene los parámetros públicos (g, p, A), el secreto del cliente (b) y el texto cifrado (enc). El objetivo es recuperar la bandera (flag).

Método de encriptación


El protocolo utilizado es el siguiente:


```
    Diffie-Hellman: El servidor elige un primo grande p y un generador g. Genera un secreto a y calcula A = g^a mod p, que envía al cliente.

    Cliente: Elige un secreto b y calcula B = g^b mod p (no se envía en este caso, pero se usa para la clave compartida). La clave compartida es K = A^b mod p = g^(a*b) mod p.

    Cifrado: La bandera se cifra con XOR usando un solo byte de la clave compartida: enc[i] = flag[i] XOR (K % 256).

```

El archivo message.txt contiene exactamente los valores necesarios para calcular K y descifrar.

Contenido de message.txt

text


g = 2

p = 1653798930689987750372209240014380521131540183716217687164747711336243702962818359267822691525697642105558753651223568056089606926425342081267821725904109431430327153613733358950243154522848602494020618427146508586350079988809469424456886589329449769221123659126892760967096413248127035734431548987006011015808526671

## A = 771122236020803078829911570090382183223626843114693013412703353349864301811612864849857638111588507084769437566078749825291937213523446695097948166153379036322108656350710200734137906115055446496743841090323252143278700024424965369059879247648625799137192258413471893876530475007392243768366999108564494255853654467

b = 502087552249276796768894199149546386713173741864561762918671131549146319658647813949433247424965048798816294966029262647803764533595143429273283374211302160540685383641060542870573303301014875733971557824236009184578986290165659257363419797500816452080900496604781986251988455903195756181696996025184087945715324970

enc = cfd6dcd0fcebf9c4dbd7e0cc8cdccd8ccbe0dddb8c87d98c8889c2


### Resolución paso a paso

1. Entender la operación de descifrado

Para descifrar necesitamos la clave compartida K = A^b mod p. Una vez obtenida, el byte que se usa para XOR es key_byte = K % 256. El descifrado es entonces:

text


### flag[i] = enc[i] XOR key_byte


2. Instalación de dependencias (problema con el entorno de Kali)

Al intentar ejecutar un script que importe Crypto, aparecía el error ModuleNotFoundError: No module named 'Crypto'. En Kali Linux (y otras distribuciones modernas), el entorno Python está protegido para evitar conflictos entre paquetes instalados con apt y con pip. Para solucionarlo, usamos un entorno virtual:

bash


cd /home/kr3s4l4/picoctf/easy/Shared_Secrets

python3 -m venv venv

source venv/bin/activate

pip install pycryptodome


Esto aísla las dependencias del proyecto y permite instalar pycryptodome sin interferir con el sistema.

3. Script de descifrado

Creamos un script XOR_decrypt.py con el siguiente código (ya no es necesario importar Crypto porque realizamos las operaciones con funciones nativas de Python):

python


```bash
# Datos del archivo message.txt
```

g = 2

p = 1653798930689987750372209240014380521131540183716217687164747711336243702962818359267822691525697642105558753651223568056089606926425342081267821725904109431430327153613733358950243154522848602494020618427146508586350079988809469424456886589329449769221123659126892760967096413248127035734431548987006011015808526671

## A = 771122236020803078829911570090382183223626843114693013412703353349864301811612864849857638111588507084769437566078749825291937213523446695097948166153379036322108656350710200734137906115055446496743841090323252143278700024424965369059879247648625799137192258413471893876530475007392243768366999108564494255853654467

b = 502087552249276796768894199149546386713173741864561762918671131549146319658647813949433247424965048798816294966029262647803764533595143429273283374211302160540685383641060542870573303301014875733971557824236009184578986290165659257363419797500816452080900496604781986251988455903195756181696996025184087945715324970

enc_hex = "cfd6dcd0fcebf9c4dbd7e0cc8cdccd8ccbe0dddb8c87d98c8889c2"


```bash
# Calcular clave compartida
```

shared = pow(A, b, p)

key_byte = shared % 256


```bash
# Descifrar
```

enc_bytes = bytes.fromhex(enc_hex)

### flag = bytes([x ^ key_byte for x in enc_bytes])


print(flag.decode())


4. Ejecución

Con el entorno virtual activado, ejecutamos:

bash


python3 XOR_decrypt.py


Obtenemos la salida:

text


picoCTF{*********}


### Explicación matemática


La seguridad de Diffie-Hellman se basa en la dificultad del logaritmo discreto. En este caso, se nos da directamente el secreto b, por lo que el descifrado es trivial: calculamos pow(A, b, p). El uso de XOR con un solo byte de la clave compartida es un método de cifrado muy simple, pero suficiente para el reto.

Lecciones aprendidas


```
    Entornos virtuales: Útiles para aislar dependencias y evitar conflictos con el sistema.

    Diffie-Hellman: Comprensión de cómo se genera una clave compartida y cómo se puede usar para cifrar.

    XOR: Operación reversible que, con la clave adecuada, permite recuperar el mensaje original.
```

