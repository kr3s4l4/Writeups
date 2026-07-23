🐦 Twitter Secret Messages — Writeup

Plataforma: Root-Me
Categoría: Esteganografía
Dificultad: 8% de resolución
Autor: Kira_
Fecha: 21 de diciembre de 2016
📝 Enunciado

    Sospechamos que este tweet esconde un punto de encuentro. Ayúdanos a encontrarlo.

El reto proporciona el siguiente texto:
text

Ｃhｏose  a  jοｂ  yоu  lονｅ,  and  you  ｗіｌl  ｎeｖｅｒ  have  tο  ｗｏrk  a  day  in  yοur  lіfｅ．                    

La contraseña de validación es el lugar de encuentro (en minúsculas).
🔍 Análisis inicial

A simple vista, el texto parece una frase célebre con algunas letras extrañas:

    "Choose a job you love, and you will never have to work a day in your life."

Sin embargo, hay alteraciones evidentes:

    Algunas letras están en cirílico o son homoglifos (Ｃ, ｏ, ｅ, ｗ, і, ｌ).

    Hay espacios de diferentes anchos (Unicode U+2000–U+200F).

    El texto contiene caracteres invisibles al final.

Todo apunta a una técnica de esteganografía Unicode conocida como "Homoglyph Steganography".
🛠️ Resolución
1. Identificar la técnica

El reto utiliza homoglifos (caracteres que se ven igual pero tienen códigos Unicode diferentes) y espacios de ancho variable para codificar información binaria.

En este caso, el mensaje oculto está codificado en caracteres Unicode no estándar que reemplazan a las letras normales.
2. Usar una herramienta de decodificación

Para extraer el mensaje oculto, se puede usar una herramienta especializada en esteganografía Unicode.

La página https://holloway.nz/steg/ está diseñada para este propósito.

Pasos:

    Copiar el texto completo del tweet (incluyendo los caracteres invisibles al final).

    Pegarlo en la sección "Decode" de la herramienta.

    La herramienta procesa el texto y revela el mensaje oculto.

3. Mensaje obtenido

La herramienta devuelve:
text

rendezvous at ***** ****** ******* on friday.

El mensaje indica claramente el lugar de encuentro:
text

grand central terminal

4. Validar la flag

La contraseña solicitada es el lugar de encuentro en minúsculas:
text

****** ****** ********

📖 Explicación técnica
¿Cómo funciona la esteganografía con homoglifos?

    Codificación:

        El mensaje oculto se convierte a binario (6 bits por carácter usando un alfabeto restringido).

        Cada bit se representa mediante la elección entre dos caracteres visualmente idénticos pero de diferente código Unicode (homoglifos).

        Por ejemplo: una letra latina a (U+0061) puede reemplazarse por una ａ (U+FF41) para codificar un bit 1, o dejarse como a para codificar un 0.

    Decodificación:

        El proceso inverso: al identificar qué caracteres son homoglifos, se extrae la secuencia binaria y se convierte de nuevo a texto.

¿Por qué es efectivo?

    Los homoglifos son invisibles a simple vista.

    La mayoría de las plataformas (como Twitter) no los filtran.

    El texto sigue siendo legible para un humano, pero oculta información adicional.
