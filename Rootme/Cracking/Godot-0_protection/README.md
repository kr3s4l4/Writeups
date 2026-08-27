Writeup: Godot – 0 protection (Root-Me)

1. Introducción

El reto Godot - 0 protection de Root‑Me presenta un juego desarrollado con el motor Godot Engine. El objetivo es llegar a la «isla de la luz en el cielo» y leer el cartel que hay en ella. El enunciado asegura que es «imposible» llegar, y nos pide demostrar lo contrario.

El nombre del reto ya nos da una pista fundamental: 0 protección significa que los recursos y scripts no están ofuscados ni encriptados. Por tanto, podemos extraerlos fácilmente y leer la lógica del juego sin necesidad de realizar ingeniería inversa sobre el binario nativo.

A lo largo de este writeup, recorreremos todas las fases del análisis: desde la extracción de los recursos hasta la comprensión del mecanismo que genera la frase del cartel. Al final, obtendremos la flag que valida el reto.

2. Reconocimiento inicial

El fichero proporcionado es un ejecutable de Windows: 0_protection.exe. No se nos da ningún archivo .pck separado, pero en Godot los recursos suelen ir incrustados al final del ejecutable o en un .pck adjunto. Como el reto dice 0 protection, es muy probable que el PCK no esté encriptado.
2.1. Identificar el motor

Ejecutamos el comando strings para buscar referencias a Godot:
bash

strings 0_protection.exe | grep -i godot

La salida muestra claramente Godot Engine y la versión, confirmando que se trata de un juego exportado con Godot.
2.2. Confirmar la ausencia de protección

Buscamos el encabezado típico de los paquetes de Godot (GDPC):
bash

grep -oba "GDPC" 0_protection.exe

Esto nos devuelve un offset (por ejemplo, 123456:GDPC). Eso indica que el PCK está embebido y no está cifrado. Con esto, tenemos vía libre para extraer todo su contenido.

3. Herramientas empleadas

Para el análisis hemos utilizado:

    godot-unpacker – extrae los recursos (imágenes, escenas, scripts compilados) del ejecutable o del .pck.

    gdre_tools (binario precompilado) – descompila los scripts de bytecode (.gdc) a GDScript legible.

    Python 3 – para traducir y ejecutar la lógica de generación de la flag.

    strings, grep, less – utilidades estándar de Linux para búsqueda y visualización de texto.

4. Extracción de recursos
4.1. Clonar e instalar godot-unpacker
bash

git clone https://github.com/tehskai/godot-unpacker.git
cd godot-unpacker

4.2. Ejecutar el extractor
bash

python3 godot-unpacker.py ../0_protection.exe

Esto crea una carpeta 0_protection_exe/ con todo el árbol de recursos del juego.
4.3. Exploración de la estructura

Al listar el contenido, encontramos la típica organización de un proyecto Godot:
text

0_protection_exe/
├── res/
│   ├── img/            # imágenes (ground, splash, rootme, etc.)
│   ├── misc/           # fuentes, materiales
│   ├── scenes/         # escenas (.tscn)
│   └── src/            # scripts (posiblemente compilados)
└── ...

Lo más interesante está en res/scenes/ y res/src/.

5. Análisis de las escenas
5.1. Examinar Main.tscn

La escena principal contiene el menú del juego. Con cat y less observamos textos como:

    "Escape from this"

    "weebs > all"

    "Crackme v0.1"

    "Start game"

No hay flag visible.
5.2. Examinar island.tscn

La escena de la isla es la clave. Al inspeccionarla, encontramos el siguiente contenido relevante:
text

[node name="FlagPanel" parent="." instance=ExtResource( 2 )]
[node name="Sprite3D" type="Sprite3D" parent="FlagPanel"]
[node name="Viewport" type="Viewport" parent="FlagPanel/Sprite3D"]
[node name="FlagLabel" type="Label" parent="FlagPanel/Sprite3D/Viewport"]
script = ExtResource( 3 )

El nodo FlagLabel tiene asignado un script llamado FlagLabel.gd (referenciado como ExtResource( 3 )). Ese script es el que genera el texto del cartel.
5.3. Buscar el script

En la carpeta res/src/ encontramos FlagLabel.gd (si está compilado, será FlagLabel.gdc). Con godot-unpacker obtuvimos el archivo en texto plano, pero si hubiera estado compilado, habríamos usado gdre_tools para descompilarlo.

6. El script FlagLabel.gd

El contenido del script es el siguiente:
gdscript

extends Label

func _ready():
        var key = [119, 104, 52, 116, 52, 114, 51, 121, 48, 117, 100, 48, 49, 110, 103, 63]
        var enc = [32, 13, 88, 24, 20, 22, 92, 23, 85, 89, 68, 68, 89, 11, 71, 89, 27, 9, 83, 84, 93, 1, 57, 42, 83, 7, 13, 96, 69, 29, 86, 81, 52, 4, 7, 64, 70]

        text = ""
        for i in range(len(enc)):
                text += char(enc[i] ^ key[i % len(key)])

Análisis:

    key es un array de 16 números enteros que, interpretados como ASCII, forman la frase:
    wh4t4r3y0ud01ng? → "what are you doing?" (con leetspeak).

    enc es un array de 37 números.

    El bucle recorre cada elemento de enc, aplica una operación XOR con el correspondiente byte de la clave (cíclicamente) y convierte el resultado a carácter (char() en GDScript).

    El texto resultante se asigna a la propiedad text del Label.

Este mecanismo es un pequeño cifrado que impide ver la flag directamente en el archivo de la escena, pero al estar el script en texto plano, es totalmente recuperable.

7. Obtención de la flag
7.1. Traducción a Python

Para ejecutar la misma lógica y obtener el texto, escribimos un script en Python de apenas unas líneas:
python

#!/usr/bin/env python3

key = [119, 104, 52, 116, 52, 114, 51, 121, 48, 117, 100, 48, 49, 110, 103, 63]
enc = [32, 13, 88, 24, 20, 22, 92, 23, 85, 89, 68, 68, 89, 11, 71, 89, 27, 9, 83, 84, 93, 1, 57, 42, 83, 7, 13, 96, 69, 29, 86, 81, 52, 4, 7, 64, 70]

text = ""
for i in range(len(enc)):
    text += chr(enc[i] ^ key[i % len(key)])

print(text)

7.2. Ejecución
bash

python3 flag.py

La salida es:
text

Well done, the flag is
*************************

Es decir, el cartel muestra una frase de felicitación y la cadena que debemos presentar como prueba.

8. Conclusión

Este reto ilustra perfectamente la importancia de conocer las herramientas adecuadas para cada tecnología. Godot exporta sus juegos con los recursos en un formato abierto (a menos que se ofusquen o encripten), y 0 protection significa que todo el código y los activos están accesibles.

El flujo de trabajo ha sido:

    Identificar el motor y la ausencia de protección.

    Extraer los recursos con godot-unpacker.

    Explorar las escenas para localizar el cartel y su script asociado.

    Leer el script y comprender su lógica (XOR con clave).

    Reproducir esa lógica en Python para obtener el texto final.
