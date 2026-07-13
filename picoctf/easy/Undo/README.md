Writeup: Undo (PicoCTF 2026)

Categoría: General Skills
Dificultad: Easy
Puntos: 100
Autor: Yahaya Meddy
📝 Descripción del reto

    Can you reverse a series of Linux text transformations to recover the original flag?

El reto consiste en conectarse a un servidor mediante nc y revertir una serie de transformaciones de texto aplicadas a la bandera. En cada paso, se nos muestra la bandera transformada y una pista sobre la última transformación aplicada. Debemos ingresar el comando de Linux correcto para deshacer esa transformación.
🔍 Reconocimiento

Primero, nos conectamos al servidor:
bash

nc foggy-cliff.picoctf.net 63863

El servidor nos presenta un mensaje de bienvenida y el primer paso:
text

===Welcome to the Text Transformations Challenge!===

Your goal: step by step, recover the original flag.
At each step, you'll see the transformed flag and a hint.
Enter the correct Linux command to reverse the last transformation.

🛠️ Herramientas utilizadas

    base64 - Decodificación Base64

    rev - Invertir texto

    tr - Traducir o eliminar caracteres

📊 Desarrollo paso a paso
Paso 1: Decodificar Base64

Texto actual:
text

KTBxcDI0bnIwLWZhMDFnQHplMHNmYTRlRy1nazNnLXRhMWZlcmlyRShTR1BicHZj

Pista:

    Base64 encoded the string.

Análisis:
La cadena tiene caracteres típicos de Base64 (letras mayúsculas, minúsculas, números y + /). Base64 es un método de codificación que convierte datos binarios en texto ASCII.

Comando para revertir:
bash

base64 -d

Explicación:

    base64 -d decodifica la entrada Base64

    Al ejecutar el comando, el servidor nos pide que peguemos la cadena (o la recibe automáticamente)

Resultado:
text

)0qp24nr0-fa01g@ze0sfa4eG-gk3g-ta1ferirE(SGPbpvc

Paso 2: Invertir el texto

Texto actual:
text

)0qp24nr0-fa01g@ze0sfa4eG-gk3g-ta1ferirE(SGPbpvc

Pista:

    Reversed the text.

Análisis:
El texto parece estar al revés. Por ejemplo, vemos )0qp24nr0 que invertido sería 0rn42pq0). El comando rev invierte el orden de los caracteres en cada línea.

Comando para revertir:
bash

rev

Explicación:

    rev invierte el orden de los caracteres

Resultado:
text

cvpbPGS(Erire1fat-gk3g-Ge4afs0ez@g10af-0rn42pq0)

Paso 3: Reemplazar guiones por guiones bajos

Texto actual:
text

cvpbPGS(Eriref1at-g3kg-Ge4afs0ez@g10af-0rn42pq0)

Pista:

    Replaced underscores with dashes.

Análisis:
Los guiones bajos _ fueron reemplazados por guiones -. Para revertir esto, debemos convertir todos los - a _.

Comando para revertir:
bash

tr '-' '_'

Explicación:

    tr '-' '_' traduce todos los guiones - a guiones bajos _

    tr (translate) es un comando que reemplaza caracteres

Resultado:
text

cvpbPGS(Eriref1at_g3kg_Ge4afs0ez@g10af_0rn42pq0)

Paso 4: Reemplazar paréntesis por llaves

Texto actual:
text

cvpbPGS(Eriref1at_g3kg_Ge4afs0ez@g10af_0rn42pq0)

Pista:

    Replaced curly braces with parentheses.

Análisis:
Las llaves { } fueron reemplazadas por paréntesis ( ). Para la bandera final necesitamos el formato picoCTF{...}.

Comando para revertir:
bash

tr '()' '{}'

Explicación:

    tr '()' '{}' traduce los paréntesis () a llaves {}

    El orden es importante: ( → { y ) → }

Resultado:
text

cvpbPGS{Eriref1at_g3kg_Ge4afs0ez@g10af_0rn42pq0}

Paso 5: Aplicar ROT13

Texto actual:
text

cvpbPGS{Eriref1at_g3kg_Ge4afs0ez@g10af_0rn42pq0}

Pista:

    Applied ROT13 to letters.

Análisis:
ROT13 es un cifrado César con desplazamiento 13. Es su propio inverso, así que para deshacerlo aplicamos ROT13 nuevamente.

Comando para revertir:
bash

tr 'A-Za-z' 'N-ZA-Mn-za-m'

Explicación:

    tr 'A-Za-z' 'N-ZA-Mn-za-m' aplica ROT13

    Mapea A→N, B→O, ..., M→Z, N→A, etc.

    Al ser simétrico, aplicarlo dos veces devuelve el texto original

Resultado final:
text

picoCTF{*********************************}

echo KTBxcDI0bnIwLWZhMDFnQHplMHNmYTRlRy1nazNnLXRhMWZlcmlyRShTR1BicHZj | base64 -d | rev | tr 'A-Za-z' 'N-ZA-Mn-za-m'
picoCTF(**********************************)


📚 Resumen de comandos utilizados
Paso	Transformación aplicada	Comando para revertir
1	Base64	base64 -d
2	Reverso	rev
3	- → _	tr '-' '_'
4	() → {}	tr '()' '{}'
5	ROT13	tr 'A-Za-z' 'N-ZA-Mn-za-m'
💡 Lecciones aprendidas

    Base64 es una codificación común que se reconoce por su patrón de caracteres alfanuméricos y +/=

    rev es útil para invertir texto, a menudo usado junto con otras transformaciones

    tr es una herramienta versátil para reemplazar caracteres y aplicar cifrados simples como ROT13

    ROT13 es su propio inverso, lo que significa que aplicar el mismo comando dos veces devuelve el texto original

    Los retos de "Undo" requieren identificar y deshacer transformaciones en el orden inverso al que fueron aplicadas

🔗 Referencias

    Base64 en Linux

    Comando rev

    Comando tr

    ROT13 en Wikipedia
