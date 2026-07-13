# 🕵️ Redaction gone wrong
### picoCTF 2022 — Forensics · Medium · 100 pts

> *"Now you DON'T see me."*  
> *Este informe contiene datos críticos, algunos redactados correctamente y otros no. ¿Puedes encontrar una clave importante que no se redactó bien?*

---

## 📌 Información general

| Campo           | Detalle                                      |
|----------------|----------------------------------------------|
| **Categoría**  | Forensics                                    |
| **Dificultad** | Media (100 puntos)                           |
| **Autor**      | Mubarak Mikail                               |
| **Archivo**    | `Financial_Report_for_ABC_Labs.pdf`          |
| **Flag**       | `picoCTF{C4n_Y0u_S33_m3_fully}`              |

---

## 🧠 Resumen ejecutivo

El reto consiste en un documento PDF que aparenta tener información **redactada visualmente**. Sin embargo, la redacción se hizo de forma incorrecta: solo se pintaron rectángulos negros sobre el texto, sin eliminar los datos del archivo.

El proceso de investigación siguió varias fases: primero, un análisis superficial para entender el contexto; luego, una inspección más profunda del contenido; y finalmente, la confirmación mediante extracción de texto. Cada fase aportó pistas que nos llevaron a la flag.

---

## 🔍 Fase 1: Análisis inicial y contexto

### 1️⃣ Exploración con `strings`

Comenzamos con un enfoque sencillo: extraer todas las cadenas de texto legibles del PDF usando `strings`. Esta herramienta es útil para obtener una vista rápida del contenido del archivo, incluso de aquello que no está visible a simple vista.

```bash
strings Financial_Report_for_ABC_Labs.pdf

https://ruta/a/tu/captura/strings.png
<details> <summary>📸 Captura de pantalla - Comando strings</summary> <!-- Inserta aquí tu captura del comando strings --> </details>
🧩 Hallazgos interesantes

En la salida de strings, encontramos varias líneas que llaman nuestra atención:

    "Breakdown - Just painted over in MS word."

        Esto nos da una pista crucial: el documento fue redactado simplemente pintando encima en Word.

    "This is not the flag, keep looking"

        Un mensaje que nos confirma que estamos en el camino correcto, pero aún no hemos llegado al objetivo.

    Fragmentos del texto del documento

        Vemos partes del informe financiero, lo que nos confirma que el contenido está ahí.

📌 Conclusión de la Fase 1:
Hemos identificado que:

    El documento fue creado en Word.

    La redacción se hizo de forma superficial (pintando encima).

    Hay contenido textual que podemos extraer.

Esto nos da una dirección de investigación: necesitamos extraer todo el texto del documento para encontrar lo que no se redactó correctamente.
📊 Fase 2: Análisis de metadatos
2️⃣ Inspección con exiftool

Antes de profundizar en el contenido, revisamos los metadatos del PDF para obtener más contexto sobre su origen y posible información oculta:
bash

exiftool Financial_Report_for_ABC_Labs.pdf

https://ruta/a/tu/captura/exiftool.png
<details> <summary>📸 Captura de pantalla - Comando exiftool</summary> <!-- Inserta aquí tu captura del comando exiftool --> </details>
📋 Información relevante de los metadatos
Metadato	Valor
Creator	Word
Producer	macOS Version 11.4 Quartz PDFContext
Title	Microsoft Word - Financial Report for ABC Labs.docx
Create Date	2021:07:17 19:44:11Z
Modify Date	2021:07:17 21:44:49+02:00

📌 Conclusión de la Fase 2:
Los metadatos confirman que:

    El documento fue creado en Microsoft Word (como sospechábamos).

    Fue exportado a PDF desde macOS.

    La redacción se hizo en Word antes de exportar, lo que explica por qué los datos subyacentes permanecen.

Esto valida nuestra hipótesis: el texto redactado aún debe estar en el archivo.
📝 Fase 3: Extracción completa del texto
3️⃣ Conversión con pdftotext

Ahora que sabemos que el texto debería estar presente, utilizamos pdftotext para extraer todo el contenido textual del PDF y guardarlo en un archivo de texto plano:
bash

pdftotext Financial_Report_for_ABC_Labs.pdf

https://ruta/a/tu/captura/pdftotext.png
<details> <summary>📸 Captura de pantalla - Comando pdftotext</summary> <!-- Inserta aquí tu captura del comando pdftotext --> </details>

Verificamos que se haya creado el archivo de salida:
bash

ls

https://ruta/a/tu/captura/ls.png
<details> <summary>📸 Captura de pantalla - Listado de archivos</summary> <!-- Inserta aquí tu captura del ls --> </details>
🔎 Revelación del contenido

Finalmente, examinamos el contenido del archivo extraído:
bash

cat Financial_Report_for_ABC_Labs.txt

https://ruta/a/tu/captura/cat.png
<details> <summary>📸 Captura de pantalla - Contenido del archivo txt</summary> <!-- Inserta aquí tu captura mostrando el contenido del txt --> </details>

El resultado es:
text

Financial Report for ABC Labs, Kigali, Rwanda for the year 2021.
Breakdown - Just painted over in MS word.

Cost Benefit Analysis
Credit Debit
This is not the flag, keep looking
Expenses from the
picoCTF{***************************}
Redacted document.

🎯 ¡Encontramos la flag!

En el texto extraído, aparece la flag completamente legible:
text

picoCTF{****************************}

📌 Conclusión de la Fase 3:
Al extraer todo el texto del PDF, hemos podido recuperar el contenido que fue "redactado" visualmente pero no eliminado del archivo.
⚙️ Explicación técnica del problema
¿Qué salió mal en la redacción?

    Redacción visual vs. redacción real

        El documento se redactó en Word usando formas/rectángulos negros sobre el texto.

        Esto oculta el texto visualmente pero no lo elimina del archivo.

    Exportación a PDF

        Al exportar a PDF, el texto subyacente se mantiene en el archivo.

        El PDF puede contener tanto la capa visual (rectángulos negros) como el texto original.

    Herramientas de extracción

        strings puede encontrar cadenas de texto en el binario.

        pdftotext extrae todo el texto del PDF, ignorando capas visuales.

        exiftool revela metadatos que confirman el origen del documento.

¿Cómo debería haberse hecho?

Para una redacción segura:

    Usar herramientas de redacción permanente (como Adobe Acrobat Pro con "Sanitize Document").

    Eliminar físicamente el texto del archivo.

    Rasterizar el documento (convertir a imágenes) antes de exportar.

    Verificar con strings y pdftotext que no quede información sensible.

🧰 Herramientas utilizadas
Herramienta	Fase	Propósito					Comando
strings		1	Extraer cadenas de texto del binario		strings Financial_Report_for_ABC_Labs.pdf
exiftool	2	Examinar metadatos				exiftool Financial_Report_for_ABC_Labs.pdf
pdftotext	3	Convertir PDF a texto plano			pdftotext Financial_Report_for_ABC_Labs.pdf
ls		3	Listar archivos generados			ls
cat		3	Visualizar contenido del archivo		cat Financial_Report_for_ABC_Labs.txt
