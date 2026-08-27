📡 Writeup: TELNET - Authentication (Reto 0x0)

Campo		Detalle
Plataforma	Reto CTF (Análisis de Captura)
Autor		g0uZ
Fecha		30 de agosto de 2010
Dificultad	Baja (5 Puntos)
Consigna	Encuentra la contraseña de usuario en esta captura de sesión de TELNET.

1. Descripción del Desafío

Se nos proporciona un archivo de captura de paquetes (.pcap) que contiene una sesión de red. El protocolo utilizado es TELNET, famoso por ser uno de los protocolos más inseguros, ya que transmite toda la información (incluyendo credenciales) en texto plano.

Nuestro objetivo es inspeccionar el tráfico, localizar el momento del inicio de sesión y extraer la contraseña del usuario.

2. Metodología de Análisis

Para resolverlo, debemos reconstruir la conversación entre el cliente y el servidor. Aunque podríamos usar herramientas como strings o tshark en terminal, la forma más gráfica y rápida es mediante Wireshark.

2.1. Filtrado del tráfico TELNET

El protocolo TELNET opera por defecto en el puerto 23. Al abrir la captura, aplicamos el siguiente filtro para limpiar el ruido de otros paquetes:
wireshark

tcp.port == 23

o simplemente:
wireshark

telnet

2.2. Reconstrucción de la sesión (Follow TCP Stream)

Haciendo clic derecho sobre cualquier paquete de la sesión y seleccionando Follow → TCP Stream, Wireshark nos muestra todo el diálogo en orden cronológico, eliminando los headers de red y mostrando únicamente la carga útil (payload) de ambos lados de la comunicación.

3. Extracción de las Credenciales

Al observar el stream proporcionado, podemos identificar claramente la secuencia de autenticación. Voy a desglosar el fragmento clave extraído de tu stream:
text

OpenBSD/i386 (oof) (ttyp1)

login: 
.."...
....."
f
f
a
a
k
k
e
e

.

Password:
*************
.

Last login: Thu Dec  2 21:32:59 on ttyp1 from bam.zing.org
...

Análisis paso a paso:

    Prompt de Usuario: El servidor envía la cadena login: .

    Ingreso del usuario: El cliente escribe fake. Aunque en el stream vemos caracteres sueltos (f, a, k, e) y puntos suspensivos, esto se debe a que el protocolo TELNET envía cada pulsación de tecla de forma individual (modo echo local). Concatenando las letras obtenemos el usuario: fake.

    Prompt de Contraseña: El servidor envía Password: .

    Ingreso de la contraseña: A continuación, vemos claramente la secuencia *, *, *, *, *, *, *. Aunque no se vea en pantalla por seguridad (el echo suele estar desactivado para contraseñas), el paquete de red sí contiene los caracteres en texto plano. La concatenación nos da la clave:*********.

4. Resultado Final (Flag)

La contraseña del usuario fake para acceder al sistema OpenBSD es:
text

*******************

5. Contexto adicional de la sesión

Una vez autenticado, el usuario ejecutó algunos comandos de forma remota:

    ls (listar archivos).

    ls -a (listar archivos ocultos, mostrando .cshrc, .login, .profile).

    ping www.yahoo.com (prueba de conectividad).

    exit (cierre de sesión).

Esto confirma que la captura es legítima y que hemos extraído las credenciales correctas del flujo de datos.

📘 Anexo: ¿Qué es Wireshark y cómo usar "Follow TCP Stream"?

Para aquellos que estén empezando en el mundo del análisis de paquetes, aquí va una pequeña guía sobre la herramienta estrella que usamos para resolver este reto.
¿Qué es Wireshark?

Wireshark es un analizador de protocolos de red (o sniffer) de código abierto. Permite capturar y examinar el tráfico que viaja por una interfaz de red en tiempo real, o abrir archivos de captura previos (.pcap, .cap, etc.). Es la navaja suiza del administrador de sistemas y del experto en seguridad ofensiva/defensiva.
¿Por qué es útil "Follow TCP Stream" (Seguir Flujo TCP)?

El tráfico de red se divide en pequeños fragmentos llamados paquetes. Cuando envías un mensaje, este se parte en múltiples paquetes que viajan por rutas diferentes y se reensamblan al llegar.

La función Follow TCP Stream en Wireshark hace precisamente eso: reensambla todos los paquetes de una conexión TCP específica y los muestra en orden secuencial, tal como los vería el usuario final, pero mostrando ambos lados de la conversación (cliente ➡️ servidor y servidor ➡️ cliente).
¿Cómo se usa?

    Abre tu archivo .pcap en Wireshark.

    Aplica un filtro para encontrar el protocolo deseado (ej. telnet, http, ftp).

    Selecciona cualquier paquete de la conversación que te interese.

    Haz clic derecho → Follow → TCP Stream.

    Se abrirá una ventana emergente con todo el diálogo.

        Color azul: Datos enviados desde el cliente (tu IP) al servidor.

        Color rojo: Datos enviados desde el servidor hacia el cliente.

    Puedes cambiar la vista a diferentes formatos (ASCII, HEX, etc.). Para contraseñas en TELNET, usamos ASCII.

    Cuando encuentres lo que buscas, puedes cerrar la ventana o guardar el stream en un archivo.

¿Para qué sirve en ciberseguridad?

    Auditorías: Revisar si alguien está enviando contraseñas en claro (TELNET, FTP, HTTP básico).

    Depuración: Entender por qué falla una aplicación al intercambiar datos.

    Análisis forense: Reconstruir exactamente lo que hizo un atacante durante una sesión comprometida.

    Reverse Engineering: Entender protocolos propietarios o personalizados.

Conclusión final

El reto es sumamente sencillo una vez que conoces la técnica de seguimiento de flujo. La contraseña es user, demostrando una vez más por qué TELNET debe ser evitado en entornos productivos en favor de SSH, que cifra todo el tráfico
