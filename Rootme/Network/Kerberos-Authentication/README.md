Writeup: Kerberos Authentication – Pre-Auth Cracking
1. Enunciado

    El equipo SOC de Cat Corporation le ha pedido que recupere la contraseña de un usuario vinculada a una conexión Kerberos sospechosa.
    Formato de bandera: RM{userPrincipalName:password}
    El userPrincipalName debe escribirse en minúsculas.

2. Análisis del tráfico con Wireshark

Abrimos el archivo pcapng con Wireshark. Para localizar la solicitud de autenticación, utilizamos el filtro de búsqueda as-req en la barra de filtros (o bien escribimos kerberos.msg_type == 10). El paquete que contiene toda la información necesaria es el Frame 60.

A continuación, desglosamos el paquete campo por campo, señalando los elementos clave para el ataque.
2.1. Fragmento del Frame 60 con anotaciones
text

Frame 60: Packet, 327 bytes on wire (2616 bits), 327 bytes captured (2616 bits) on interface virbr0, id 0
Ethernet II, Src: 54:54:01:97:49:54 (54:54:01:97:49:54), Dst: 52:54:00:65:4c:4d (52:54:00:65:4c:4d)
Internet Protocol Version 4, Src: 192.168.122.1, Dst: 192.168.122.100
Transmission Control Protocol, Src Port: 55282, Dst Port: 88, Seq: 1, Ack: 1, Len: 273
Kerberos
    Record Mark: 269 bytes                      ← Longitud del mensaje Kerberos
        0... .... .... .... .... .... .... .... = Reserved: Not set
        .000 0000 0000 0000 0000 0001 0000 1101 = Record Length: 269
    as-req                                      ← Mensaje de solicitud de autenticación
        pvno: 5                                 ← Versión del protocolo (Kerberos 5)
        msg-type: krb-as-req (10)               ← Tipo de mensaje (AS-REQ)
        padata: 2 items                         ← Datos de preautenticación
            PA-DATA pA-ENC-TIMESTAMP            ← Timestamp cifrado (preautenticación)
                padata-type: pA-ENC-TIMESTAMP (2)
                    padata-value: 3041a003020112a23a0438fc8bbe22b2c967b222ed73dd7616ea71b2ae0c1b0c3688bfff7fecffdebd4054471350cb6e36d3b55ba3420be6c0210b2d978d3f51d1eb4f
                        etype: eTYPE-AES256-CTS-HMAC-SHA1-96 (18)   ← Algoritmo de cifrado (AES256)
                        cipher: fc8bbe22b2c967b222ed73dd7616ea71b2ae0c1b0c3688bfff7fecffdebd4054471350cb6e36d3b55ba3420be6c0210b2d978d3f51d1eb4f   ← HASH a crackear
            PA-DATA pA-PAC-REQUEST              ← Solicitud de PAC (no relevante)
                padata-type: pA-PAC-REQUEST (128)
                    padata-value: 3005a0030101ff
                        include-pac: True
        req-body                                ← Cuerpo de la solicitud
            Padding: 0
            kdc-options: 50800000
            cname                               ← Nombre del cliente (usuario)
                name-type: kRB5-NT-PRINCIPAL (1)
                cname-string: 1 item
                    CNameString: **********     ← USUARIO (ofuscado)
            realm: **********                   ← DOMINIO Kerberos (REALM) (ofuscado)
            sname                               ← Nombre del servidor (vacío para TGT)
            till: Feb 20, 2024 17:00:48.000000000 CET
            rtime: Feb 20, 2024 17:00:48.000000000 CET
            nonce: 498314083
            etype: 1 item
    [Response in: 61]                           ← Paquete de respuesta (AS-REP)

2.2. Resumen de los datos extraídos
Campo	Valor (ofuscado)	Uso
CNameString	**********	Usuario para el hash y la bandera
realm	**********	Dominio para el hash y la bandera
etype	18 (AES256)	Algoritmo de cifrado (determina el modo de hashcat)
cipher	fc8bbe22...	Hash del timestamp cifrado con la contraseña
3. Extracción del hash (modo 19900)

El campo cipher dentro de PA-ENC-TIMESTAMP contiene el timestamp del cliente cifrado con la contraseña del usuario. Este tipo de hash se puede crackear con hashcat utilizando el modo 19900 (Kerberos 5, etype 18, Pre-Auth).
3.1. Formato del hash para hashcat

El formato esperado es:
text

$krb5pa$18$usuario$realm$cipher

    18 es el etype (AES256).

    usuario es el nombre del principal (sin el dominio).

    realm es el dominio Kerberos.

    cipher es el valor hexadecimal extraído.

Importante: hashcat espera que el usuario y el realm estén separados por un $, no por una @. Si usamos @, aparece el error Separator unmatched.
3.2. Construcción del hash

Extraemos el cipher del paquete. Para evitar truncamientos, lo copiamos desde Wireshark haciendo clic derecho sobre el valor → Copy → … as Hex Stream.

El hash resultante (con valores ofuscados) es:
text

$krb5pa$18$**********$**********$fc8bbe22b2c967b222ed73dd7616ea71b2ae0c1b0c3688bfff7fecffdebd4054471350cb6e36d3b55ba3420be6c0210b2d978d3f51d1eb4f

Guardamos esta línea en un archivo, por ejemplo pa_hash.txt.
4. Cracking con hashcat

Usamos la wordlist rockyou.txt (descomprimida si está en .gz). El comando es:
bash

hashcat -m 19900 -a 0 -D 1 --force pa_hash.txt /usr/share/wordlists/rockyou.txt

    -m 19900: modo Pre-Auth Kerberos AES256.

    -a 0: ataque de diccionario.

    -D 1: forzar el uso de CPU (opcional, útil si no hay GPU compatible).

    --force: omitir advertencias de OpenCL.

4.1. Resultado

Tras unos segundos, hashcat muestra que el hash ha sido crackeado:
text

$krb5pa$18$**********$**********$fc8bbe...:**********

La contraseña recuperada es ********** (ofuscada).
5. Construcción de la bandera

El formato de la bandera es RM{userPrincipalName:password}. El userPrincipalName debe ir en minúsculas y tiene la forma usuario@dominio.

    userPrincipalName = **********@**********.local (en minúsculas)

    password = **********

Bandera final (ofuscada):
text

RM{**********@**********.local:**********}

6. Lecciones aprendidas

    Identificar el tipo de hash correcto: no todos los hashes Kerberos son iguales. En este caso, el ataque se centró en el timestamp de preautenticación (modo 19900), no en AS-REP Roasting (18200) ni Kerberoasting (13100).

    Formato exacto: hashcat es muy sensible a los separadores. En el modo 19900, el usuario y el realm se separan con $, no con @. Un error en esto provoca el famoso Separator unmatched.

    Extracción cuidadosa: copiar el cipher como "Hex Stream" desde Wireshark garantiza que no se trunque ni se añadan caracteres no deseados.

    Uso de herramientas: si hashcat falla por problemas de OpenCL, se puede usar --force o recurrir a John the Ripper como alternativa.

7. Anexo: Comandos utilizados
bash

# Extraer el hash (ya hecho manualmente)
echo '$krb5pa$18$**********$**********$fc8bbe22b2c967b222ed73dd7616ea71b2ae0c1b0c3688bfff7fecffdebd4054471350cb6e36d3b55ba3420be6c0210b2d978d3f51d1eb4f' > pa_hash.txt

# Crackear con hashcat
hashcat -m 19900 -a 0 -D 1 --force pa_hash.txt /usr/share/wordlists/rockyou.txt

# Mostrar resultado
hashcat -m 19900 pa_hash.txt --show

8. Conclusión

Hemos logrado recuperar la contraseña del usuario mediante el cracking del timestamp de preautenticación Kerberos. Este tipo de ataque es efectivo cuando se dispone de tráfico de red y la contraseña es débil o está en un diccionario común. El reto ha permitido practicar la identificación de flujos Kerberos, la extracción de hashes y el uso de herramientas de cracking, además de comprender la importancia de los formatos correctos.
