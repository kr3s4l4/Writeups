📝 Writeup: JavaScript Obfuscation 2

🎯 Resumen del Reto

Categoría	JavaScript - Ofuscación
Puntos	10
Nivel	Principiante
Objetivo	Desofuscar código JavaScript para encontrar la contraseña/bandera

📖 Introducción

El reto "JavaScript Obfuscation 2" presenta un código JavaScript ofuscado que debemos descifrar. La pista "Bajando 3 pisos..." nos indica que hay 3 capas de ofuscación que debemos desencriptar secuencialmente para obtener la respuesta final.

🔍 Análisis Inicial
Código Ofuscado Original
javascript

pass = unescape("unescape%28%22String.fromCharCode%2528104%252C68%252C117%252C102%252C106%252C100%252C107%252C105%252C49%252C53%252C54%2529%22%29");

Observaciones

    Función unescape(): Indica que el string está codificado con URL encoding

    Patrón %XX: Caracteres hexadecimales que representan caracteres URL encoded

    %2528, %252C, %2529: Doble codificación (el %25 representa el carácter %)

    String.fromCharCode(): Función que convierte códigos ASCII a caracteres

Pista

    "Bajando 3 pisos..." → Hay 3 niveles de ofuscación que descifrar

🏗️ Metodología de Desofuscación

Capa 1: Primer unescape()

Comando:
javascript

var capa1 = unescape("unescape%28%22String.fromCharCode%2528104%252C68%252C117%252C102%252C106%252C100%252C107%252C105%252C49%252C53%252C54%2529%22%29");
console.log("Capa 1:", capa1);

Explicación:

    unescape() decodifica la URL encoding

    El string contiene %28 = (, %22 = ", %29 = )

    Convierte %2528 → %28 (primer nivel)

Resultado:
javascript

unescape("String.fromCharCode%28104%2C68%2C117%2C102%2C106%2C100%2C107%2C105%2C49%2C53%2C54%29")

Análisis del resultado:

    Aparece un segundo unescape()

    %28 = (, %2C = ,, %29 = )

    String.fromCharCode() está codificado

Capa 2: Segundo unescape()

Comando:
javascript

var interior = "String.fromCharCode%28104%2C68%2C117%2C102%2C106%2C100%2C107%2C105%2C49%2C53%2C54%29";
var capa2 = unescape(interior);
console.log("Capa 2:", capa2);

Explicación:

    Extraemos el string interior del primer unescape()

    Aplicamos unescape() nuevamente para decodificar el segundo nivel

    Los códigos %28, %2C, %29 se convierten en caracteres literales

Resultado:
javascript

String.fromCharCode(104,68,117,102,106,100,107,105,49,53,54)

Análisis del resultado:

    Tenemos la función String.fromCharCode() limpia

    Los números son códigos ASCII decimales

    104 = h, 68 = D, 117 = u, etc.

Capa 3: Ejecutar String.fromCharCode()

Comando:
javascript

var numeros = [104,68,117,102,106,100,107,105,49,53,54];
var capa3 = String.fromCharCode(...numeros);
console.log("Capa 3 (FINAL):", capa3);

Explicación:

    Guardamos los números en un array

    Usamos el spread operator (...) para pasar los números como argumentos

    String.fromCharCode() convierte cada número a su carácter ASCII

Resultado:
text

*****************************

🔢 Tabla de Conversión ASCII
Número	Carácter|	Número	Carácter
104	*	|	107	*
68	*	|	105	*
117	*	|	49	*
102	*	|	53	*
106	*	|	54	*
100	*	|	91	*

Resultado Final: hDufjdki156

📝 Comandos Utilizados (Resumen)

1. Decodificar Capa 1
javascript

var capa1 = unescape("unescape%28%22String.fromCharCode%2528104%252C68%252C117%252C102%252C106%252C100%252C107%252C105%252C49%252C53%252C54%2529%22%29");

2. Decodificar Capa 2
javascript

var interior = "String.fromCharCode%28104%2C68%2C117%2C102%2C106%2C100%2C107%2C105%2C49%2C53%2C54%29";
var capa2 = unescape(interior);

3. Convertir ASCII a Caracteres
javascript

var numeros = [104,68,117,102,106,100,107,105,49,53,54,91];
var capa3 = String.fromCharCode(...numeros);

4. Comando Todo en Uno
javascript

// Versión simplificada
String.fromCharCode(104,68,117,102,106,100,107,105,49,53,54,91)

🛠️ Herramientas Alternativas
Python
python

import urllib.parse

codigo = "unescape%28%22String.fromCharCode%2528104%252C68%252C117%252C102%252C106%252C100%252C107%252C105%252C49%252C53%252C54%2529%22%29"
paso1 = urllib.parse.unquote(codigo)
print(f"Capa 1: {paso1}")

# Extraer números
import re
numeros = re.findall(r'\d+', paso1)
final = ''.join(chr(int(n)) for n in numeros)
print(f"FINAL: {final}")

Node.js (Terminal)
bash

node -e "console.log(String.fromCharCode(104,68,117,102,106,100,107,105,49,53,54))"

Bash + Node
bash

node -p "String.fromCharCode(104,68,117,102,106,100,107,105,49,53,54)"

🎓 Lecciones Aprendidas
Técnicas de Ofuscación Identificadas

Técnica			Descripción				Cómo Identificarla
URL Encoding		Uso de %XX para codificar caracteres	Patrón %XX visible
Doble Codificación	%25XX (donde %25 = %)			%25 seguido de XX
String.fromCharCode()	Conversión de ASCII a caracteres	Función visible con números
Anidamiento		Capas de funciones dentro de otras	Paréntesis anidados

Patrones de Reconocimiento

    unescape(...) → Decodificar URL encoding

    String.fromCharCode(N,N,N) → Convertir ASCII a texto

    %XX → Caracteres URL encoded

    %25 → Doble codificación (representa %)

🚀 Mejores Prácticas para Desofuscar
Paso a Paso

    Identificar el tipo de codificación:

        %XX → URL encoding

        \xNN → Hexadecimal

        \uXXXX → Unicode

        eval() → Código ejecutable

    Decodificar capa por capa:

        Usar console.log() para mostrar cada paso

        Verificar el resultado antes de continuar

    Buscar patrones:

        String.fromCharCode() + números → ASCII

        atob()/btoa() → Base64

        unescape()/escape() → URL encoding

    Validar el resultado:

        ¿Es legible?

        ¿Tiene sentido en el contexto del reto?

✅ Resultado Final
text

🏆 BANDERA / CONTRASEÑA: ***************

📊 Flujo de Desofuscación
text

Código Ofuscado
       ↓
┌─────────────────────────────────┐
│   Capa 1: unescape()            │
│   "unescape(...)"               │
└─────────────────────────────────┘
       ↓
┌─────────────────────────────────┐
│   Capa 2: unescape()            │
│   "String.fromCharCode(...)"    │
└─────────────────────────────────┘
       ↓
┌─────────────────────────────────┐
│   Capa 3: String.fromCharCode() │
│   ASCII → Texto                 │
└─────────────────────────────────┘
       ↓
   *************** ✅
