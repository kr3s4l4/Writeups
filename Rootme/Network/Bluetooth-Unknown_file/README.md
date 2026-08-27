Writeup: Bluetooth - Unknown File (Root-Me)
📌 Introducción

El reto "Bluetooth - Unknown File" de Root-Me consiste en extraer información de una captura de tráfico Bluetooth para construir una cadena compuesta por la dirección MAC del dispositivo (en mayúsculas y con dos puntos) y el nombre del teléfono. La respuesta final es el hash SHA‑1 de esa concatenación.

    Objetivo: Obtener el SHA‑1 de MAC:NOMBRE_DISPOSITIVO.

🛠️ Herramientas utilizadas

    Kali Linux (o cualquier distribución con Wireshark y herramientas CLI)

    Wireshark – análisis de paquetes

    file, strings, sha1sum – utilidades de línea de comandos

🔍 Paso 1: Identificar el formato del archivo

El archivo proporcionado se llama ch18.bin. Lo primero es determinar su naturaleza:
bash

file ch18.bin

Salida:
text

ch18.bin: BTSnoop version 1, HCI UART (H4)

Se trata de una captura en formato BTSnoop, el estándar para registrar paquetes Bluetooth HCI (Host Controller Interface). Esto indica que podemos abrirlo directamente con Wireshark.
📝 Paso 2: Extraer el nombre del teléfono

El nombre del dispositivo suele aparecer en texto plano dentro de la captura. Usamos strings para buscar cadenas que parezcan un modelo de teléfono. Para acotar la búsqueda, filtramos por un prefijo común como "GT-":
bash

strings ch18.bin | grep -i "GT-"

Salida (ofuscada):
text

GT-SXXXXX
GT-SXXXXX

Encontramos dos ocurrencias del mismo nombre. Lo anotamos como NOMBRE_DISPOSITIVO (en nuestro caso, era un modelo Samsung, pero lo ocultamos para no spoilear).
📡 Paso 3: Obtener la dirección MAC en Wireshark

Abrimos la captura en Wireshark:
bash

wireshark ch18.bin

3.1 Filtros relevantes

Para localizar paquetes que contengan información del dispositivo, podemos aplicar los siguientes filtros:

    Para ver eventos de conexión:
    bthci_evt.code == 0x03 (Connect Complete)

    Para ver respuestas de nombre remoto:
    bthci_evt.code == 0x07 (Remote Name Request Complete)

3.2 Frames clave
🔹 Frame 3 – Connect Complete

Este paquete confirma el establecimiento de la conexión ACL y contiene la dirección MAC del dispositivo remoto.
text

Frame 3: Packet, 14 bytes on wire (112 bits), 14 bytes captured (112 bits)
    Encapsulation type: Bluetooth H4 with linux header (99)
    Arrival Time: Mar 28, 2017 21:02:36.818084000 CEST
    UTC Arrival Time: Mar 28, 2017 19:02:36.818084000 UTC
    Epoch Arrival Time: 1490727756.818084000
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 150.006000 milliseconds]
    [Time delta from previous displayed frame: 150.006000 milliseconds]
    [Time since reference or first frame: 151.001000 milliseconds]
    Frame Number: 3
    Frame Length: 14 bytes (112 bits)
    Capture Length: 14 bytes (112 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    Point-to-Point Direction: Received (1)
    [Protocols in frame: bluetooth:hci_h4:bthci_evt]
    Character encoding: ASCII (0)
Bluetooth
    [Source: controller]
    [Destination: host]
Bluetooth HCI H4
    [Direction: Rcvd (0x01)]
    HCI Packet Type: HCI Event (0x04)
Bluetooth HCI Event - Connect Complete
    Event Code: Connect Complete (0x03)
    Parameter Total Length: 11
    Status: Success (0x00)
    Connection Handle: 0x0100
    BD_ADDR: SamsungElect_xx:xx:xx (XX:XX:XX:XX:XX:XX)   <--- MAC del dispositivo
    Link Type: ACL connection (Data Channels) (0x01)
    Encryption Mode: Encryption Disabled (0x00)

    Dato relevante: El campo BD_ADDR contiene la dirección MAC del teléfono. En este caso, es XX:XX:XX:XX:XX:XX (ofuscado).

🔹 Frame 9 – Remote Name Request Complete

Este paquete devuelve el nombre legible del dispositivo remoto, junto con su MAC, confirmando así ambos datos.
text

Frame 9: Packet, 258 bytes on wire (2064 bits), 258 bytes captured (2064 bits)
    Encapsulation type: Bluetooth H4 with linux header (99)
    Arrival Time: Mar 28, 2017 21:02:36.852073000 CEST
    UTC Arrival Time: Mar 28, 2017 19:02:36.852073000 UTC
    Epoch Arrival Time: 1490727756.852073000
    [Time shift for this packet: 0.000000000 seconds]
    [Time delta from previous captured frame: 18.978000 milliseconds]
    [Time delta from previous displayed frame: 18.978000 milliseconds]
    [Time since reference or first frame: 184.990000 milliseconds]
    Frame Number: 9
    Frame Length: 258 bytes (2064 bits)
    Capture Length: 258 bytes (2064 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    Point-to-Point Direction: Received (1)
    [Protocols in frame: bluetooth:hci_h4:bthci_evt]
    Character encoding: ASCII (0)
Bluetooth
    [Source: controller]
    [Destination: host]
Bluetooth HCI H4
    [Direction: Rcvd (0x01)]
    HCI Packet Type: HCI Event (0x04)
Bluetooth HCI Event - Remote Name Request Complete
    Event Code: Remote Name Request Complete (0x07)
    Parameter Total Length: 255
    Status: Success (0x00)
    BD_ADDR: SamsungElect_xx:xx:xx (XX:XX:XX:XX:XX:XX)   <--- MAC (coincide con Frame 3)
    Remote Name: NOMBRE_DISPOSITIVO                        <--- Nombre del teléfono

    Datos relevantes:

        BD_ADDR: XX:XX:XX:XX:XX:XX (dirección MAC)

        Remote Name: NOMBRE_DISPOSITIVO (nombre del dispositivo)

🔗 Paso 4: Construir la cadena final

Según el enunciado, la cadena a hashear es la concatenación directa de la MAC (en mayúsculas y con dos puntos) y el nombre, sin ningún separador adicional.

Para nuestro caso:
text

XX:XX:XX:XX:XX:XXNOMBRE_DISPOSITIVO

(Ejemplo real: 0C:B3:19:B9:4F:C6GT-S7390G)
🔐 Paso 5: Calcular el SHA‑1

Usamos echo -n para evitar el salto de línea final y sha1sum para obtener el hash:
bash

echo -n "XX:XX:XX:XX:XX:XXNOMBRE_DISPOSITIVO" | sha1sum | cut -d' ' -f1

Salida esperada (hash real, ofuscado):
text

<HASH_REAL>

    💡 Nota: El hash real se obtiene al ejecutar el comando con los datos correctos. En este writeup se muestra un ejemplo genérico.

✅ Conclusión

Hemos extraído exitosamente:

    Nombre: NOMBRE_DISPOSITIVO

    MAC: XX:XX:XX:XX:XX:XX

    Hash SHA‑1: <HASH_REAL>

El reto está completado.
📎 Anexo: Comandos resumen
bash

# Identificar archivo
file ch18.bin

# Extraer nombre
strings ch18.bin | grep "GT-"

# Abrir en Wireshark
wireshark ch18.bin

# Calcular hash
echo -n "XX:XX:XX:XX:XX:XXNOMBRE_DISPOSITIVO" | sha1sum | cut -d' ' -f1
