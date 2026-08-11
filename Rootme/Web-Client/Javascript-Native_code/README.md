Root-Me Writeup: Javascript - Native code

📝 Challenge Description
Category: Web - Client
Difficulty: Easy
Técnica: Desofuscación no alfanumérica / Reconstrucción de ASCII Octal.
Objetivo: Analizar un script de JavaScript altamente ofuscado ejecutado en el lado del cliente para extraer la contraseña de validación (Flag).

🔍 Initial AnalysisAl inspeccionar el código fuente proporcionado por el reto, nos topamos con un bloque de código JavaScript que no utiliza variables alfanuméricas comunes, sino una técnica conocida como JJEncode. 
El script utiliza coerción de tipos (Type Coercion) y operaciones aritméticas de bits a través de variables con caracteres especiales (É, ó, Ë, þ) para construir funciones dinámicamente.

1. Resolución Matemática de Variables BaseJavaScript interpreta los arreglos vacíos [] y operadores lógicos como números enteros. 

Analizando el inicio del código:
É = -~-~[]: Sabiendo que ~[] es -1, la negación -~[] es 1. 
Al repetirse, É = 2.ó = -~É: Incrementa en 1 el valor anterior. 
ó = 3.Ë = É << É: Desplazamiento de bits (\(2 \ll 2\)). 
Ë = 8.þ = Ë + ~[]: Equivalente a 8 + (-1). 
þ = 7.2. Abuso del Constructor de Objetos

El script construye la cadena "constructor" extrayendo letras de objetos nativos en formato string (como "[object Object]" o "undefined").
La línea Ì = (ó-ó)[Û] se resuelve como 0["constructor"]["constructor"], otorgando acceso directo a la función global Function(), permitiendo ejecutar strings de texto como código arbitrario.

🛠️ Exploitation & Scripting
Intentar traducir el código de forma manual es propenso a errores humanos de transcripción.
Para automatizar el proceso de manera segura y nativa dentro de nuestro entorno de Kali Linux, desarrollamos un script en Python 

3.El script lee el código ofuscado original, computa de manera dinámica el valor real de las variables matemáticas y decodifica las secuencias Octales (Base 8) ocultas tras las barras invertidas (\).
Exploit Script (solucion.py)python#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Root-Me: Javascript - Native code Decoder
Author: Root User @ Kali Linux
"""
import re

raw_code = """É=-~-~[],ó=-~É,Ë=É<<É,þ=Ë+~[];Ì=(ó-ó)[Û=(''+{})[É+ó]+(''+{})[ó-É]+([].ó+'')[ó-É]+(!!''+'')[ó]+({}+'')[ó+ó]+(!''+'')[ó-É]+(!''+'')[É]+(''+{})[É+ó]+({}+'')[ó+ó]+(''+{})[ó-É]+(!''+'')[ó-É]][Û];Ì(Ì((!''+'')[ó-É]+(!''+'')[ó]+(!''+'')[ó-ó]+(!''+'')[É]+((!''+''))[ó-É]+([].$+'')[ó-É]+'\''+''+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(þ)+(É+ó)+'\\'+(ó-É)+(ó+ó)+(ó-ó)+'\\'+(ó-É)+(ó+ó)+(É)+'\\'+(ó-É)+(É+ó)+(þ)+'\\'+(ó-É)+(É+ó)+(É+ó)+'\\'+(ó-É)+(ó+ó)+(ó-ó)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(É+ó)+(ó-ó)+'\\'+(É+É)+(þ)+'\\'+(ó-É)+(ó-ó)+(É+ó)+'\\'+(ó-É)+(É+ó)+(ó+ó)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(ó-É)+(ó+ó)+(É)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(ó-É)+(þ)+(É)+'\\'+(É+É)+(ó-ó)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(É+É)+(ó-ó)+'\\'+(ó-É)+(É+ó)+(É+ó)+'\\'+(ó-É)+(É+ó)+(þ)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(É+É)+(ó-ó)+'\\'+(ó-É)+(É+É)+(É+É)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(É+É)+(ó-ó)+'\\'+(ó-É)+(ó+ó)+(ó-ó)+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(ó-É)+(ó+ó)+(ó)+'\\'+(ó-É)+(ó+ó)+(ó)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(É+É)+(þ)+'\\'+(É+ó)+(ó-É)+'\\'+(þ)+(ó)+'\\'+(ó-É)+(É+ó)+(ó-É)+'\\'+(ó-É)+(É+É)+(ó+ó)+'\\'+(É+ó)+(ó-ó)+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(þ)+(É+ó)+'\\'+(þ)+(É+ó)+'\\'+(É+É)+(þ)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(ó-É)+(É+ó)+(þ)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(ó-É)+(É+ó)+(þ)+'\\'+(ó+ó)+(ó-É)+'\\'+(ó+ó)+(É)+'\\'+(ó+ó)+(ó)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(ó-É)+(É+ó)+(þ)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(É+É)+(þ)+'\\'+(É+ó)+(ó-É)+'\\'+(ó-É)+(þ)+(ó)+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(ó-É)+(ó+ó)+(É)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(É+ó)+(ó-ó)+'\\'+(É+É)+(þ)+'\\'+(ó-É)+(É+É)+(É)+'\\'+(ó-É)+(ó+ó)+(É)+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(ó-É)+(ó+ó)+(ó+ó)+'\\'+(ó-É)+(É+ó)+(þ)+'\\'+(É+É)+(þ)+'\\'+(É+ó)+(ó-É)+'\\'+(þ)+(ó)+'\\'+(ó-É)+(þ)+(É+ó)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(ó-É)+(ó+ó)+(ó)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(ó-É)+(þ)+(ó)+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(ó-É)+(É+É)+(É+ó)+'\\'+(ó-É)+(ó+ó)+(É)+'\\'+(ó-É)+(ó+ó)+(É+É)+'\\'+(É+ó)+(ó-ó)+'\\'+(É+É)+(þ)+'\\'+(ó-É)+(É+É)+(ó+ó)+'\\'+(ó-É)+(É+É)+(ó-É)+'\\'+(ó-É)+(É+ó)+(ó-É)+'\\'+(ó-É)+(É+ó)+(É+É)+'\\'+(É+ó)+(ó+ó)+'\\'+(É+ó)+(ó+ó)+'\\'+(É+ó)+(ó+ó)+'\\'+(É+É)+(þ)+'\\'+(É+ó)+(ó-É)+'\\'+(þ)+(ó)+'\\'+(ó-É)+(þ)+(É+ó)+'\'')())()"""

# Inicialización exacta de variables simuladas
É, ó, þ = 2, 3, 7

# Separación del payload por su delimitador de escape
chunks = raw_code.split("'\\'")
decoded_output = []

for chunk in chunks[1:]:
    clean_chunk = chunk.split("'\\'")[0].split("'")[0]
    parenthesis_blocks = re.findall(r'\(([^)]+)\)', clean_chunk)
    
    if not parenthesis_blocks:
        continue
        
    octal_digits = []
    for expr in parenthesis_blocks:
        # Normalización estricta de cadenas matemáticas
        expr_mod = expr.replace('ó-É', '1').replace('ó-ó', '0')\
                       .replace('É+É', '4').replace('É+ó', '5')\
                       .replace('ó+ó', '6').replace('É', '2')\
                       .replace('ó', '3').replace('þ', '7')
        octal_digits.append(str(eval(expr_mod)))
            
    if octal_digits:
        octal_string = "".join(octal_digits)
        decoded_output.append(chr(int(octal_string, 8)))

print("".join(decoded_output))

Ejecución y Salida Real

Al correr el script en la terminal, el código oculto se revela en texto claro:
bash$ 
python3 solucion.py

a=prompt('Entrez le mot de passe');if(a=='*****************'){alert('bravo');}else{alert('fail...');}

🔍 Code Review & VulnerabilityEl código desofuscado expone una validación de contraseña en el lado del cliente (Client-Side Authentication):javascripta = prompt('Entrez le mot de passe');

if (a == '****************') {
    alert('bravo');
} else {
    alert('fail...');
}

Vulnerabilidad Crítica:

Client-Side Authentication Bypass: El flujo de autenticación reside por completo en el navegador del usuario.
Aunque se intente ocultar la lógica mediante algoritmos de ofuscación complejos como JJEncode, cualquier atacante con acceso a las herramientas de desarrollo o herramientas de scripting básico puede revertir el proceso y extraer las credenciales sin interactuar con un servidor legítimo.

🏁 Flag / Password

El string requerido para completar exitosamente el reto es:*****************
