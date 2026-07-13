Writeup Detallado: PW Crack 3 - PicoCTF
📋 Información del Reto

    Nombre: PW Crack 3

    Categoría: General Skills

    Dificultad: Medium

    Puntos: 75

    Autor: LT 'syreal' Jones

    Descripción: ¿Puedes crackear la contraseña para obtener la flag?

🔍 1. Análisis Inicial
Archivos proporcionados

El reto nos da tres archivos:

    level3.py - Script principal de verificación

    level3.flag.txt.enc - Flag cifrada

    level3.hash.bin - Hash MD5 de la contraseña correcta

Inspección de archivos

level3.py - El código completo:
python

import hashlib

def str_xor(secret, key):
    #extend key to secret length
    new_key = key
    i = 0
    while len(new_key) < len(secret):
        new_key = new_key + key[i]
        i = (i + 1) % len(key)        
    return "".join([chr(ord(secret_c) ^ ord(new_key_c)) for (secret_c,new_key_c) in zip(secret,new_key)])

flag_enc = open('level3.flag.txt.enc', 'rb').read()
correct_pw_hash = open('level3.hash.bin', 'rb').read()

def hash_pw(pw_str):
    pw_bytes = bytearray()
    pw_bytes.extend(pw_str.encode())
    m = hashlib.md5()
    m.update(pw_bytes)
    return m.digest()

def level_3_pw_check():
    user_pw = input("Please enter correct password for flag: ")
    user_pw_hash = hash_pw(user_pw)
    
    if( user_pw_hash == correct_pw_hash ):
        print("Welcome back... your flag, user:")
        decryption = str_xor(flag_enc.decode(), user_pw)
        print(decryption)
        return
    print("That password is incorrect")

level_3_pw_check()

# The strings below are 7 possibilities for the correct password. 
#   (Only 1 is correct)
pos_pw_list = ["6997", "3ac8", "f0ac", "4b17", "ec27", "4e66", "865e"]

🔬 2. Análisis del Código
Estructura del programa

El script tiene tres componentes principales:
a) Función str_xor(secret, key)

    Realiza una operación XOR entre la flag cifrada y la contraseña

    Extiende la clave para que coincida con la longitud del secreto

    Es un cifrado XOR simple, reversible si conocemos la clave

b) Función hash_pw(pw_str)

    Convierte la contraseña a bytes

    Calcula el hash MD5

    Retorna el digest (hash en binario)

c) Función level_3_pw_check()

    Solicita la contraseña al usuario

    Calcula el hash de la entrada

    Compara con el hash almacenado en level3.hash.bin

    Si coinciden, descifra y muestra la flag

    Si no, muestra mensaje de error

Pista crucial
python

pos_pw_list = ["6997", "3ac8", "f0ac", "4b17", "ec27", "4e66", "865e"]

El mismo código nos da 7 posibles contraseñas, ¡solo una es correcta!
🛠️ 3. Desarrollo del Exploit
Estrategia

Como solo hay 7 contraseñas posibles, podemos hacer fuerza bruta automatizada.
Script de fuerza bruta (script.sh)
bash

#!/bin/bash

pos_pw_list=("6997" "3ac8" "f0ac" "4b17" "ec27" "4e66" "865e")

echo "[*] Iniciando fuerza bruta sobre level3.py..."
echo "----------------------------------------"

for pw in "${pos_pw_list[@]}"; do
    echo "[*] Probando contraseña: $pw"
    
    # Pasar la contraseña al script
    salida=$(echo "$pw" | python3 level3.py)
    
    # Verificar si encontró la flag
    if echo "$salida" | grep -q "Welcome back"; then
        echo ""
        echo "[+] ¡CONTRASEÑA ENCONTRADA!: $pw"
        echo "[+] Salida:"
        echo "$salida"
        break
    else
        echo "[-] $pw -> Incorrecta"
    fi
done

echo "----------------------------------------"

Explicación del script

    Array de contraseñas: Almacena las 7 posibilidades

    Bucle for: Itera sobre cada contraseña

    Pipe con echo: Pasa la contraseña como input al script Python
    bash

    salida=$(echo "$pw" | python3 level3.py)

    Detección de éxito: Busca "Welcome back" en la salida

        Si aparece → contraseña correcta, muestra la flag

        Si no → continúa con la siguiente

    break: Detiene el bucle al encontrar la correcta

🚀 4. Ejecución del Ataque
Paso 1: Crear el script
bash

nano script.sh
# Pegar el código anterior

Paso 2: Dar permisos de ejecución
bash

chmod +x script.sh

Paso 3: Ejecutar
bash

./script.sh

Salida obtenida:
text

[*] Iniciando fuerza bruta sobre level3.py...
----------------------------------------
[*] Probando contraseña: 6997
[-] 6997 -> Incorrecta
[*] Probando contraseña: 3ac8
[-] 3ac8 -> Incorrecta
[*] Probando contraseña: f0ac
[-] f0ac -> Incorrecta
[*] Probando contraseña: 4b17
[-] 4b17 -> Incorrecta
[*] Probando contraseña: ec27
[-] ec27 -> Incorrecta
[*] Probando contraseña: 4e66
[-] 4e66 -> Incorrecta
[*] Probando contraseña: 865e

[+] ¡CONTRASEÑA ENCONTRADA!: 865e
[+] Salida:
Please enter correct password for flag: Welcome back... your flag, user:
picoCTF{**************************}
----------------------------------------

🎯 5. Flag
text

picoCTF{************************}

📚 6. Conceptos Aprendidos
🔐 Criptografía

    MD5 Hashing: Función hash criptográfica (aunque insegura para uso real)

    XOR Encryption: Cifrado simétrico simple donde texto_plano XOR clave = texto_cifrado

    La seguridad recae en la clave, no en el algoritmo

💻 Programación

    Automatización con bash: Uso de pipes y bucles para interactuar con programas

    Fuerza bruta: Probar sistemáticamente todas las combinaciones posibles

    Espacio de búsqueda reducido: Solo 7 posibilidades vs millones en fuerza bruta real

🧠 Metodología

    Analizar el código fuente proporcionado

    Identificar el mecanismo de autenticación

    Encontrar las posibles contraseñas en el mismo código

    Automatizar las pruebas para eficiencia

    Extraer la flag del resultado exitoso

🔒 7. ¿Por qué es inseguro?

    Contraseñas en texto plano: Están listadas en el código fuente

    Hash sin salt: El MD5 es vulnerable a ataques de diccionario

    Espacio de búsqueda pequeño: Solo 7 opciones, crackeable en segundos

    Cifrado XOR simple: Cualquiera con la contraseña puede descifrar

🛡️ 8. Buenas Prácticas

En un sistema real se debería:

    ❌ No almacenar contraseñas en el código

    ✅ Usar algoritmos de hash seguros (bcrypt, Argon2)

    ✅ Implementar salt en los hashes

    ✅ Limitar intentos de acceso

    ✅ No mostrar pistas sobre contraseñas válidas
