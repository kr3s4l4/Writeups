PW Crack 5 – Writeup para Principiantes
📦 ¿Qué nos dan?

Al descargar los archivos del reto, tenemos:
Archivo	Descripción
level5.py	Script principal de Python que pide una contraseña. Si es correcta, muestra la flag.
level5.flag.txt.enc	Flag cifrada (ilegible directamente).
level5.hash.bin	Hash de la contraseña correcta (en binario).
dictionary.txt	Diccionario con 65536 posibles contraseñas.
script.sh	Script en Bash que automatiza la prueba de contraseñas.
script2.py	Script en Python que automatiza la prueba de contraseñas.
🧠 ¿Cómo funciona level5.py?

Vamos a leerlo por partes para entender qué hace:
python

import hashlib

Importa la librería hashlib, que permite calcular hashes (como MD5, SHA1, etc.).
python

flag_enc = open('level5.flag.txt.enc', 'rb').read()
correct_pw_hash = open('level5.hash.bin', 'rb').read()

    Carga la flag cifrada desde el archivo level5.flag.txt.enc.

    Carga el hash de la contraseña correcta desde level5.hash.bin.

python

def hash_pw(pw_str):
    pw_bytes = bytearray()
    pw_bytes.extend(pw_str.encode())
    m = hashlib.md5()
    m.update(pw_bytes)
    return m.digest()

Esta función:

    Convierte la contraseña (texto) a bytes.

    Calcula su hash MD5.

    Devuelve el hash en formato binario (digest).

python

def level_5_pw_check():
    user_pw = input("Please enter correct password for flag: ")
    user_pw_hash = hash_pw(user_pw)
    
    if( user_pw_hash == correct_pw_hash ):
        print("Welcome back... your flag, user:")
        decryption = str_xor(flag_enc.decode(), user_pw)
        print(decryption)
        return
    print("That password is incorrect")

El programa:

    Pide una contraseña al usuario.

    Calcula el hash MD5 de lo que escribimos.

    Compara ese hash con correct_pw_hash (el hash de la contraseña real).

    Si coinciden, descifra la flag usando XOR con la contraseña y la imprime.

    Si no coinciden, dice "That password is incorrect".

    🔍 La función str_xor no necesitamos entenderla a fondo; solo saber que descifra la flag usando la contraseña correcta como clave.

🎯 Objetivo

Encontrar la contraseña que hace que el hash MD5 coincida con el almacenado en level5.hash.bin. Como tenemos un diccionario de posibles contraseñas, vamos a probarlas una por una hasta dar con la correcta.
🐍 Script en Python (script2.py)

Este script automatiza la prueba de todas las contraseñas del diccionario contra level5.py.
Explicación línea por línea
python

#!/usr/bin/env python3
import subprocess
import sys

    subprocess: permite ejecutar otros programas desde Python.

    sys: para manejar errores y salir del script.

python

DICCIONARIO = "dictionary.txt"

Variable que guarda el nombre del archivo de diccionario.
python

def probar_contrasena(password):
    proceso = subprocess.run(
        ["python3", "level5.py"],
        input=password + "\n",
        capture_output=True,
        text=True
    )
    salida = proceso.stdout
    
    if "Welcome back" in salida:
        return True, salida
    return False, salida

Esta función:

    Ejecuta python3 level5.py.

    Le pasa la contraseña como si el usuario la escribiera (input=password + "\n").

    Captura lo que el programa imprime (stdout).

    Revisa si en la salida aparece "Welcome back", que significa que la contraseña fue correcta.

    Devuelve True y la salida si fue correcta, o False y la salida si no.

python

with open(DICCIONARIO, 'r') as f:
    passwords = [line.strip() for line in f if line.strip()]

    Abre dictionary.txt en modo lectura.

    Lee cada línea, le quita espacios y saltos de línea (strip).

    Ignora líneas vacías.

    Guarda todas las contraseñas en una lista.

python

for i, pw in enumerate(passwords, 1):
    exito, salida = probar_contrasena(pw)
    if exito:
        print(f"[+] ¡CONTRASEÑA ENCONTRADA!: {pw}")
        print(salida)
        return

    Recorre la lista de contraseñas una por una.

    Llama a probar_contrasena con cada una.

    Si encuentra la correcta, la imprime junto con la flag y termina.

🖥️ Script en Bash (script.sh)

Es la versión en Bash del mismo ataque de fuerza bruta. Ideal si prefieres la terminal de Linux.
Explicación línea por línea
bash

#!/bin/bash
DICCIONARIO="dictionary.txt"

Declara el intérprete y la variable con el nombre del diccionario.
bash

total=$(wc -l < "$DICCIONARIO")
actual=0

    wc -l cuenta las líneas del archivo.

    total guarda el número total de contraseñas.

    actual llevará la cuenta de cuántas hemos probado.

bash

while IFS= read -r pw; do
    actual=$((actual + 1))

    Lee el diccionario línea por línea.

    pw contiene la contraseña actual.

    Incrementa el contador.

bash

    salida=$(echo "$pw" | python3 level5.py)

    Pasa la contraseña a level5.py usando una tubería (echo -> |).

    Guarda la salida del programa en la variable salida.

bash

    if echo "$salida" | grep -q "Welcome back"; then
        echo "[+] ¡CONTRASEÑA ENCONTRADA!: $pw"
        echo "[+] Salida:"
        echo "$salida"
        exit 0
    fi

    Busca la frase "Welcome back" en la salida.

    Si la encuentra, muestra la contraseña y la flag, y termina el script.

⚡ Ejecución y resultado

Al ejecutar cualquiera de los dos scripts, vemos cómo prueba contraseñas hasta que encuentra la correcta:
text

[*] Probando contraseña (32352/65536): 7e5f

[+] ¡CONTRASEÑA ENCONTRADA!: 7e5f
[+] Salida completa:
Please enter correct password for flag: Welcome back... your flag, user:
picoCTF{***********************}


💡 Conceptos clave aprendidos
Concepto	Explicación breve
Hash	Función que convierte datos en una cadena de longitud fija. MD5 es un tipo de hash.
Fuerza bruta	Probar todas las combinaciones posibles hasta dar con la correcta.
Diccionario	Lista de posibles contraseñas usada en ataques de fuerza bruta.
subprocess (Python)	Módulo para ejecutar comandos del sistema desde Python.
Tuberías en Bash	Pasar la salida de un comando como entrada de otro (echo | python3).
XOR	Operación lógica usada para cifrar/descifrar con una clave.
