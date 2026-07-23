📸 EXIF - Metadata | Root-Me Writeup
🎯 Información del Challenge
text

╔══════════════════════════════════════════════════════════════╗
║                    EXIF - Metadata                          ║
╠══════════════════════════════════════════════════════════════╣
║  Categoría    : Esteganografía                              ║
║  Puntos       : 5                                          ║
║  Nivel        : 1/10                                       ║
║  Validaciones : 24,247                                     ║
║  Tasa éxito   : 7%                                         ║
║  Nota         : 3.9/5 (1,119 votos)                       ║
║  Autor        : Isis                                       ║
║  Fecha        : 28 marzo 2022                             ║
╚══════════════════════════════════════════════════════════════╝

📋 Declaración
text

┌─────────────────────────────────────────────────────────────┐
│  "¡Nuestro triste amigo pepo se ha perdido!                │
│   ¿Puedes encontrar dónde está?                            │
│   La contraseña es la ciudad en la que se encuentra pepo." │
└─────────────────────────────────────────────────────────────┘

🖥️ Entorno de Trabajo
text

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# 

Sistema: Kali Linux
Herramientas: exiftool, strings, binwalk
🔍 FASE 1: Análisis con ExifTool
Comando Ejecutado
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# exiftool ch1.png

📊 Salida del Análisis
text

╔═══════════════════════════════════════════════════════════════════════════╗
║                         METADATOS EXIF - ch1.png                          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ExifTool Version Number         : 13.55                                  ║
║  File Name                       : ch1.png                                ║
║  File Size                       : 13 kB                                  ║
║  File Type                       : PNG                                    ║
║  Image Width                     : 96                                     ║
║  Image Height                    : 96                                     ║
║  Bit Depth                       : 8                                      ║
║  Color Type                      : RGB with Alpha                         ║
║                                                                           ║
║  ╔═════════════════════════════════════════════════════════════════════╗  ║
║  ║  🗺️  DATOS DE GEOLOCALIZACIÓN - ¡INFORMACIÓN CRÍTICA!                ║  ║
║  ╠═════════════════════════════════════════════════════════════════════╣  ║
║  ║  GPS Latitude Ref                : North                            ║  ║
║  ║  GPS Longitude Ref               : East                             ║  ║
║  ║  GPS Latitude                    : ** deg **' **.27" N              ║  ║
║  ║  GPS Longitude                   : * deg **' **.38" E               ║  ║
║  ║  GPS Position                    : **°**'**.27"N, *°**'**.38"E      ║  ║
║  ╚═════════════════════════════════════════════════════════════════════╝  ║
║                                                                           ║
║  ╔═════════════════════════════════════════════════════════════════════╗  ║
║  ║  📝  OTROS METADATOS                                                ║  ║
║  ╠═════════════════════════════════════════════════════════════════════╣  ║
║  ║  Image Description     : S0rry_N0_Gu3ss1ng_Gh1zm0!                  ║  ║
║  ║  Owner Name            : ISISTM                                     ║  ║
║  ║  Exif Version          : 0232                                       ║  ║
║  ║  Flashpix Version      : 0100                                       ║  ║
║  ╚═════════════════════════════════════════════════════════════════════╝  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📝 FASE 2: Guardar Resultados
Comandos Ejecutados
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# exiftool ch1.png > exifch1.txt

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# strings ch1.png >> exifch1.txt

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# cat exifch1.txt

📄 Contenido del Archivo
text

ExifTool Version Number         : 13.55
File Name                       : ch1.png
Directory                       : .
File Size                       : 13 kB
File Modification Date/Time     : 2026:07:15 20:50:40+02:00
File Access Date/Time           : 2026:07:22 17:38:33+02:00
File Inode Change Date/Time     : 2026:07:15 20:52:26+02:00
File Permissions                : -rwxrwx---
File Type                       : PNG
File Type Extension             : png
MIME Type                       : image/png
Image Width                     : 96
Image Height                    : 96
Bit Depth                       : 8
Color Type                      : RGB with Alpha
Compression                     : Deflate/Inflate
Filter                          : Adaptive
Interlace                       : Noninterlaced
SRGB Rendering                  : Perceptual
Gamma                           : 2.2
Pixels Per Unit X               : 3779
Pixels Per Unit Y               : 3779
Pixel Units                     : meters
Exif Byte Order                 : Big-endian (Motorola, MM)
Image Description               : S0rry_N0_Gu3ss1ng_Gh1zm0!
Resolution Unit                 : inches
Y Cb Cr Positioning             : Centered
Exif Version                    : 0232
Components Configuration        : Y, Cb, Cr, -
Flashpix Version                : 0100
Owner Name                      : ISISTM
GPS Latitude Ref                : North
GPS Longitude Ref               : East
Image Size                      : 96x96
Megapixels                      : 0.009
GPS Latitude                    : ** deg **' **.27" N
GPS Longitude                   : * deg **' **.38" E
GPS Position                    : ** deg **' **.27" N, * deg **' **.38" E

🔍 FASE 4: Análisis con Binwalk
Comando Ejecutado
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# binwalk ch1.png

📊 Resultados
text

╔═══════════════════════════════════════════════════════════════════════════╗
║                     ANÁLISIS BINWALK - ch1.png                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  DECIMAL    HEXADECIMAL     DESCRIPTION                                   ║
║  ═══════════════════════════════════════════════════════════════════════  ║
║                                                                           ║
║  0          0x0             PNG image, 96 x 96, 8-bit/color RGBA,       ║
║                              non-interlaced                              ║
║                                                                           ║
║  91         0x5B            TIFF image data, big-endian,                ║
║                              offset of first image directory: 8          ║
║                                                                           ║
║  367        0x16F           Zlib compressed data, compressed            ║
║                                                                           ║
║  ╔═════════════════════════════════════════════════════════════════════╗  ║
║  ║  ✅  CONCLUSIÓN: No hay archivos ocultos adicionales               ║  ║
║  ║  La información está en los metadatos EXIF                         ║  ║
║  ╚═════════════════════════════════════════════════════════════════════╝  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Guardar Resultados
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# binwalk ch1.png >> exifch1.txt

🔍 FASE 5: Verificación con ch2.png
Comandos Ejecutados
bash

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# exiftool ch2.png > exifch2.txt

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# strings ch2.png >> exifch2.txt

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# binwalk ch2.png >> exifch2.txt

┌──(root㉿kali)-[/home/…/Writeups/Rootme/Steganography/EXIF-Metadata]
└─# firefox "https://www.google.com/maps?q=43.29896,5.37372"

🗺️ Ubicación Encontrada
text

╔═══════════════════════════════════════════════════════════════════════════╗
║                         UBICACIÓN ENCONTRADA                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                     │  ║
║  │                        🌍  Google Maps                              │  ║
║  │                                                                     │  ║
║  │     ╔═══════════════════════════════════════════════════════════╗   │  ║
║  │     ║                                                           ║   │  ║
║  │     ║              📍 **.*****, *.*****                        ║   │  ║
║  │     ║                                                           ║   │  ║
║  │     ║    ┌─────────────────────────────────────────────────┐    ║   │  ║
║  │     ║    │                                                 │    ║   │  ║
║  │     ║    │     🏛️  **************************               │    ║   │  ║
║  │     ║    │                                                 │    ║   │  ║
║  │     ║    │     *********************                       │    ║   │  ║
║  │     ║    │                                                 │    ║   │  ║
║  │     ║    └─────────────────────────────────────────────────┘    ║   │  ║
║  │     ║                                                           ║   │  ║
║  │     ╚═══════════════════════════════════════════════════════════╝   │  ║
║  │                                                                     │  ║
║  └─────────────────────────────────────────────────────────────────────┘  ║
║                                                                           ║
║  ╔═════════════════════════════════════════════════════════════════════╗  ║
║  ║  🌆  CIUDAD: **********************                                 ║  ║
║  ╚═════════════════════════════════════════════════════════════════════╝  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

🏆 FLAG
text

╔═════════════════════════════════════════════════════════════════════════╗
║                                                                         ║
║                          🏆  FLAG OBTENIDA                              ║
║                                                                         ║
║                      ╔════════════════════════════╗                     ║
║                      ║                            ║                     ║
║                      ║      *****************     ║                     ║
║                      ║                            ║                     ║
║                      ╚════════════════════════════╝                     ║
║                                                                         ║
║                       ✅  Challenge Completado                          ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝

📊 RESUMEN TÉCNICO
Flujo de Trabajo
text

┌────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE ANÁLISIS                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌──────────┐                                                         │
│   │  ch1.png │                                                         │
│   └────┬─────┘                                                         │
│        │                                                               │
│        ├─────────────────┬─────────────────┬───────────────────────────┤
│        │                 │                 │                           │
│        ▼                 ▼                 ▼                           │
│   ┌─────────┐      ┌─────────┐      ┌──────────┐                       │
│   │exiftool │      │ strings │      │ binwalk  │                       │
│   └────┬────┘      └────┬────┘      └────┬─────┘                       │
│        │                │                │                             │
│        ▼                ▼                ▼                             │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │           Extracción de datos                               │      │
│   ├─────────────────────────────────────────────────────────────┤      │
│   │  ✅ exiftool → GPS: **°**'**.27"N, *°**'**.38"E             │      │
│   │  ✅ strings → Mensaje: S0rry_N0_Gu3ss1ng_Gh1zm0!            │      │
│   │  ✅ exiftool → Autor: ISISTM                                │      │
│   │  ✅ binwalk → Sin archivos ocultos                          │      │
│   └─────────────────────────────────────────────────────────────┘      │
│        │                                                               │
│        ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │           Georreferenciación                                │      │
│   ├─────────────────────────────────────────────────────────────┤      │
│   │  N, E → Google Maps                                         │      │
│   │  ↓                                                          │      │
│   │  *****************************                              │      │
│   └─────────────────────────────────────────────────────────────┘      │
│        │                                                               │
│        ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │           Verificación con ch2.png                          │      │
│   ├─────────────────────────────────────────────────────────────┤      │
│   │  ✅ Mismos metadatos GPS                                    │      │
│   │  ✅ Mismo mensaje con strings                               │      │
│   │  ✅ Mismo autor                                             │      │
│   └─────────────────────────────────────────────────────────────┘      │
│        │                                                               │
│        ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │           🏆 FLAG: *********                                │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
