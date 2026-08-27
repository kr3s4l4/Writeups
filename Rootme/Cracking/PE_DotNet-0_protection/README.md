Writeup: PE DotNet - 0 protection (Root-me)

Autor del reto: Geluchat
Fecha: 15 de septiembre de 2014
Dificultad: 1/5 (10 puntos)
Categoría: Cracking – .NET sin protección
Plataforma: Root-me.org
📌 Descripción del desafío

Se nos proporciona un binario ejecutable de Windows (ch22.exe) desarrollado en .NET. Al ejecutarlo, aparece una ventana con un campo de texto, un botón "Valider" y una etiqueta "Password". El objetivo es descubrir la contraseña correcta que hace que el programa muestre un mensaje de felicitación.

El reto indica explícitamente "0 protection", lo que significa que el código no está ofuscado, empaquetado ni protegido con herramientas como Dotfuscator o ConfuserEx. Por lo tanto, la lógica de validación y la contraseña deben estar en texto plano dentro del ensamblado, accesibles mediante ingeniería inversa estática.
🛠️ Enfoque y herramientas

Para resolver el reto, empleamos exclusivamente técnicas de análisis estático sobre el código gestionado (CIL – Common Intermediate Language). Dado que no hay protección, podemos extraer la cadena de comparación directamente del binario sin necesidad de depuración dinámica.

Herramientas utilizadas:

    strings (Linux) – para extraer cadenas de texto ASCII y Unicode del binario.

    monodis (Mono) – desensamblador de IL (no llegó a funcionar por problemas de compatibilidad).

    Decompiler.com – descompilador online de .NET que convierte el CIL a código C# legible.

    Wine / Mono (opcional) – para ejecutar el binario y verificar la contraseña localmente.

🔍 Paso a paso: análisis y descubrimiento
1. Primer vistazo con strings

En primer lugar, utilizamos la herramienta strings para extraer todas las cadenas imprimibles del ejecutable. Esto nos da una visión rápida de posibles contraseñas o pistas.
bash

strings -n 6 ch22.exe > strings.txt
cat strings.txt

La salida muestra numerosas cadenas del framework .NET, pero también algunas que parecen sospechosas:
text

wwwwww
wwwwwwwwwwwwww
CrackMe
Geluchat
...

Nota: La opción -n 6 limita la extracción a cadenas de al menos 6 caracteres para reducir el ruido.

Aunque estas cadenas parecen candidatas, no podemos confirmar que ninguna sea la contraseña real. Además, la cadena correcta podría estar en formato Unicode (UTF-16), que strings no captura por defecto; para ello habría que usar strings -el (little-endian Unicode). Aun así, la contraseña real (como veremos) es una cadena ASCII de 7 caracteres, pero por alguna razón no apareció en el volcado inicial (quizás por estar en una sección no estándar o por alineación). Por tanto, necesitamos un análisis más profundo.
2. Intento de desensamblado con monodis

En sistemas Linux, la suite Mono proporciona monodis, un desensamblador de IL que puede generar una representación textual del código intermedio. Ejecutamos:
bash

monodis ch22.exe > ch22.il

Sin embargo, obtuvimos un error de segmentación (segmentation fault), lo que indica que el binario podría estar compilado con una versión de .NET no soportada por la versión de Mono instalada, o que el ejecutable tiene algún tipo de empaquetado que impide su correcta carga. Descartamos esta vía.
3. Descompilación online con decompiler.com

La alternativa más fiable es utilizar un descompilador .NET. Existen varias herramientas gratuitas (ILSpy, dnSpy, dotPeek), pero para evitar instalaciones, recurrimos a un servicio web: decompiler.com.

Procedimiento:

    Accedemos a https://www.decompiler.com/.

    Subimos el archivo ch22.exe (arrastrarlo o seleccionarlo desde el sistema).

    El sitio procesa el ensamblado y muestra el código fuente en C# reconstruido, incluyendo todas las clases, métodos y eventos.

    Para ver el contenido, es posible que sea necesario desactivar temporalmente el bloqueador de anuncios (el sitio muestra un pequeño anuncio para mantener el servicio gratuito).

    Navegamos por el árbol de clases hasta encontrar CrackMe.Form1.Button1_Click.

🧩 Código extraído (fragmento relevante)

Dentro del método Button1_Click, encontramos la lógica de validación:
csharp

private void Button1_Click(object sender, EventArgs e)
{
    // Compara el texto del cuadro con una cadena literal
    if (Operators.CompareString(TextBox1.Text, "*****", false) == 0)
    {
        Interaction.MsgBox((object)"Bravo! Vous pouvez valider avec ce mot de passe\r\nWell done! You can validate with this password", (MsgBoxStyle)0, (object)null);
    }
    else
    {
        Interaction.MsgBox((object)"Mauvais mot de passe\r\nBad password", (MsgBoxStyle)0, (object)null);
    }
}

(La cadena real ha sido reemplazada por ***** en este writeup para no revelar la solución antes de tiempo.)

La comparación se realiza mediante Operators.CompareString (propio de Visual Basic .NET, ya que el programa está escrito en VB.NET). Si la cadena ingresada coincide exactamente con la cadena literal, se muestra el mensaje de éxito; en caso contrario, mensaje de error.
🧠 Explicación técnica

    CIL (Common Intermediate Language): El código fuente se compila a CIL, que es un lenguaje de bajo nivel independiente de la plataforma. En el CIL, las cadenas literales se cargan mediante la instrucción ldstr.

    Descompilación: Herramientas como decompiler.com leen los metadatos y el CIL del ensamblado, y los traducen a un lenguaje de alto nivel (C# o VB.NET) que es fácil de leer. Como el binario no está ofuscado, la traducción es prácticamente exacta.

4. Verificación local (opcional)

Para confirmar que la contraseña encontrada es correcta, podemos ejecutar el binario en un entorno Windows o en Linux con Wine o Mono.

En nuestro sistema Kali, intentamos con:
bash

# Configurar Wine en modo 32 bits
export WINEPREFIX=~/wine32
export WINEARCH=win32
wine ch22.exe

Aunque aparecieron errores relacionados con libvulkan y wine-mono (el runtime .NET para Wine), el programa se ejecutó a medias. Para solucionarlo, sería necesario instalar el paquete wine-mono:
bash

sudo apt install wine-mono -y

Alternativamente, con Mono:
bash

mono ch22.exe

Pero dio un error de carga del ensamblado Microsoft.VisualBasic; la solución sería instalar mono-vbnc:
bash

sudo apt install mono-vbnc -y

Dado que la contraseña ya estaba confirmada por el código, no fue necesario ejecutarlo localmente.
🏁 Resultado

Contraseña correcta: *****
(La cadena real ha sido ocultada por motivos didácticos; se obtiene del código descompilado.)

Validación en Root-me:

    Introducir la contraseña en el campo de texto de la ventana.

    Pulsar el botón "Valider".

    Si es correcta, el programa muestra el mensaje de éxito.

    En la plataforma Root-me, introducir la misma cadena en el formulario de validación (normalmente en la parte inferior de la página del reto) otorga los 10 puntos.

📝 Conclusión

Este reto ilustra perfectamente la vulnerabilidad de los binarios .NET que no están protegidos. Cualquier usuario con acceso a un descompilador puede extraer la lógica de autenticación y las credenciales embebidas en el código. Para proteger una aplicación .NET, sería necesario ofuscar el código (dificultando la lectura) y, en casos críticos, implementar validaciones en el lado del servidor.

Lecciones aprendidas:

    strings puede dar pistas, pero no siempre revela todas las cadenas, especialmente si están en formato Unicode o comprimidas.

    Herramientas como decompiler.com, ILSpy o dnSpy son imprescindibles para el análisis de ensamblados .NET.

    La ausencia de ofuscación convierte la extracción de secretos en una tarea trivial.

📎 Anexo: Código completo de Form1

A continuación, el código C# completo de la clase Form1 (con la cadena sensible ofuscada). Se puede observar la estructura del formulario, la inicialización de controles y el evento del botón.
csharp

using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Runtime.CompilerServices;
using System.Windows.Forms;
using Microsoft.VisualBasic;
using Microsoft.VisualBasic.CompilerServices;

namespace CrackMe
{
    [DesignerGenerated]
    public class Form1 : Form
    {
        private IContainer components;

        [AccessedThroughProperty("Label1")]
        private Label _Label1;

        [AccessedThroughProperty("TextBox1")]
        private TextBox _TextBox1;

        [AccessedThroughProperty("Button1")]
        private Button _Button1;

        // ... propiedades y constructores ...

        private void InitializeComponent()
        {
            // Configuración de los controles (Label, TextBox, Button)
            // ...
            this.Text = "CrackMe DotNet bat86";
        }

        private void TextBox1_TextChanged(object sender, EventArgs e) { }

        private void Button1_Click(object sender, EventArgs e)
        {
            if (Operators.CompareString(TextBox1.Text, "*****", false) == 0)
            {
                Interaction.MsgBox("Bravo! ...", MsgBoxStyle.OkOnly, null);
            }
            else
            {
                Interaction.MsgBox("Mauvais mot de passe ...", MsgBoxStyle.OkOnly, null);
            }
        }
    }
}
