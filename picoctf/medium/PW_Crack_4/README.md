Writeup: PW Crack 4 (picoCTF)

Categoría: General Skills
Dificultad: Medium
Puntos: 85
Autor: LT 'syreal' Jones
1. Descripción del reto

    Can you crack the password to get the flag?
    Download the password checker here and you'll need the encrypted flag and the hash in the same directory too.
    There are 100 potential passwords with only 1 being correct. You can find these by examining the password checker script.

Se nos proporcionan tres archivos:

    level4.py — el script comprobador de contraseña

    level4.flag.txt.enc — la flag cifrada

    level4.hash.bin — el hash MD5 de la contraseña correcta

El objetivo es encontrar la contraseña correcta entre 100 posibles y usarla para descifrar la flag.
2. Análisis del código fuente
2.1. Función de descifrado XOR
python

def str_xor(secret, key):
    new_key = key
    i = 0
    while len(new_key) < len(secret):
        new_key = new_key + key[i]
        i = (i + 1) % len(key)        
    return "".join([chr(ord(secret_c) ^ ord(new_key_c)) for (secret_c,new_key_c) in zip(secret,new_key)])

Funcionamiento:

    Toma un secret (texto cifrado) y una key (clave).

    Si la clave es más corta que el secreto, la repite cíclicamente hasta igualar longitudes.

    Realiza una operación XOR carácter por carácter entre el texto cifrado y la clave extendida.

    El resultado es el texto descifrado.

Propiedad importante del XOR: Si A XOR B = C, entonces C XOR B = A. Por tanto, la misma función sirve para cifrar y descifrar.
2.2. Lectura de archivos
python

flag_enc = open('level4.flag.txt.enc', 'rb').read()
correct_pw_hash = open('level4.hash.bin', 'rb').read()

    flag_enc: Contiene la flag cifrada mediante XOR con la contraseña correcta.

    correct_pw_hash: Contiene el hash MD5 (en binario) de la contraseña correcta.

2.3. Función de hash
python

def hash_pw(pw_str):
    pw_bytes = bytearray()
    pw_bytes.extend(pw_str.encode())
    m = hashlib.md5()
    m.update(pw_bytes)
    return m.digest()

    Convierte la contraseña a bytes.

    Calcula su hash MD5.

    Retorna el hash en formato binario (.digest() en lugar de .hexdigest()).

2.4. Función de verificación
python

def level_4_pw_check():
    user_pw = input("Please enter correct password for flag: ")
    user_pw_hash = hash_pw(user_pw)
    
    if user_pw_hash == correct_pw_hash:
        print("Welcome back... your flag, user:")
        decryption = str_xor(flag_enc.decode(), user_pw)
        print(decryption)
        return
    print("That password is incorrect")

    Solicita una contraseña al usuario.

    Calcula su hash MD5.

    Compara con el hash correcto.

    Si coinciden, usa la contraseña para descifrar la flag mediante XOR.

    Si no, muestra un mensaje de error.

2.5. Lista de posibles contraseñas
python

pos_pw_list = ["8c86", "7692", "a519", "3e61", "7dd6", "8919", ...]

Contiene 100 cadenas de 4 caracteres hexadecimales. Solo una es la contraseña correcta.
3. Estrategia de resolución

Para obtener la flag necesitamos:

    Encontrar cuál de las 100 contraseñas produce un hash MD5 idéntico al almacenado en level4.hash.bin.

    Ejecutar level4.py con esa contraseña para descifrar la flag.

Métodos posibles:

    Manual: Probar una a una (ineficiente, 100 intentos).

    Automatizado: Crear un script que itere sobre la lista y compare hashes.

Optamos por el método automatizado.
4. Desarrollo del script de fuerza bruta

Creamos un archivo script.py en el mismo directorio:
python

import hashlib

# Leer el hash correcto
with open('level4.hash.bin', 'rb') as f:
    correct_pw_hash = f.read()

# Lista de posibles contraseñas extraída del código fuente
pos_pw_list = ["8c86", "7692", "a519", "3e61", "7dd6", "8919", "aaea", "f34b", 
               "d9a2", "39f7", "626b", "dc78", "2a98", "7a85", "cd15", "80fa", 
               "8571", "2f8a", "2ca6", "7e6b", "9c52", "7423", "a42c", "7da0", 
               "95ab", "7de8", "6537", "ba1e", "4fd4", "20a0", "8a28", "2801", 
               "2c9a", "4eb1", "22a5", "c07b", "1f39", "72bd", "97e9", "affc", 
               "4e41", "d039", "5d30", "d13f", "c264", "c8be", "2221", "37ea", 
               "ca5f", "fa6b", "5ada", "607a", "e469", "5681", "e0a4", "60aa", 
               "d8f8", "8f35", "9474", "be73", "ef80", "ea43", "9f9e", "77d7", 
               "d766", "55a0", "dc2d", "a970", "df5d", "e747", "dc69", "cc89", 
               "e59a", "4f68", "14ff", "7928", "36b9", "eac6", "5c87", "da48", 
               "5c1d", "9f63", "8b30", "5534", "2434", "4a82", "d72c", "9b6b", 
               "73c5", "1bcf", "c739", "6c31", "e138", "9e77", "ace1", "2ede", 
               "32e0", "3694", "fc92", "a7e2"]

# Probar cada contraseña
for pw in pos_pw_list:
    pw_hash = hashlib.md5(pw.encode()).digest()
    if pw_hash == correct_pw_hash:
        print(f"Contraseña encontrada: {pw}")
        break

5. Ejecución
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/PW_Crack_4]
└─# python3 script.py
Contraseña encontrada: 9f63

La contraseña correcta es 9f63.
6. Obtención de la flag

Ejecutamos el script original con la contraseña encontrada:
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/PW_Crack_4]
└─# python3 level4.py
Please enter correct password for flag: 9f63
Welcome back... your flag, user:
picoCTF{*****************************}

7. Flag
text

picoCTF{*********************************}

8. Explicación del nombre de la flag

El texto fl45h_5pr1ng1ng (leet speak de "flash springing") hace referencia a:

    Flash: Velocidad rápida.

    Springing: Saltar o brotar.

Es un juego de palabras que alude a un ataque de diccionario rápido, justo la técnica utilizada para resolver el reto: probar velozmente una lista de posibles contraseñas hasta encontrar la correcta.
9. Conceptos aprendidos
Concepto	Explicación
Cifrado XOR	Operación simétrica donde el mismo algoritmo cifra y descifra usando una clave.
MD5	Función hash criptográfica que produce un resumen de 128 bits.
.digest() vs .hexdigest()	digest() devuelve bytes, hexdigest() devuelve string hexadecimal.
Ataque de diccionario	Probar sistemáticamente una lista predefinida de posibles contraseñas.
Leet speak	Sustitución de letras por números visualmente similares (flash → fl45h).
10. Conclusión

PW Crack 4 es un reto de nivel medio que combina:

    Comprensión de código Python.

    Conceptos básicos de criptografía (XOR, MD5).

    Automatización de fuerza bruta sobre una lista limitada de candidatos.

La dificultad principal radica en identificar la necesidad de automatizar la búsqueda y entender la diferencia entre el formato binario del hash y la representación hexadecimal habitual.
