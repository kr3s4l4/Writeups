🔐 Writeup: NTLM - Authentication (Root-Me)

Autor: nuts.
Nivel: 1% de resolución.
Categoría: Network / Forense.
Técnicas: Análisis de tráfico SMB, extracción de hashes NetNTLMv2, cracking con Hashcat.

🎯 Objetivo

Recuperar la contraseña de un usuario a partir de una captura de red que contiene una autenticación NTLM sobre SMB.
Formato de la bandera: RM{userPrincipalName:password}
🛠️ Herramientas

    Wireshark – para inspeccionar los paquetes.

    Hashcat (v7.1.2) – para el cracking del hash NetNTLMv2 (modo 5600).

    Diccionario rockyou.txt.

📄 Análisis de los frames clave

El intercambio NTLM consta de tres mensajes; los dos que nos interesan son:

    Frame 49 – Respuesta del servidor con el desafío (NTLMSSP_CHALLENGE).

    Frame 51 – Respuesta del cliente con la autenticación (NTLMSSP_AUTH).

🔹 Frame 49 – Desafío del servidor

En este frame, el servidor envía su Server Challenge de 8 bytes.
A continuación se reproduce el fragmento esencial del frame, señalando el campo exacto donde aparece.
text

SMB2 (Server Message Block Protocol version 2), STATUS_MORE_PROCESSING_REQUIRED, Session Setup Response, MessageId 2
    SMB2 Header
        ...
        Session Id: 0x0000100000000029 Acct:*** Domain:*** Host:   <-- (aquí ya se ve el usuario y dominio, pero los ocultamos)
    Session Setup Response
        ...
        Security Blob […]
            GSS-API ...
                NTLM Secure Service Provider
                    NTLMSSP identifier: NTLMSSP
                    NTLM Message Type: NTLMSSP_CHALLENGE (0x00000002)
                    Target Name: CATCORP
                    Negotiate Flags: 0xe2898235
                    ⬇️⬇️⬇️ CAMPO CLAVE ⬇️⬇️⬇️
                    NTLM Server Challenge: ****************   <--- 8 bytes (16 hex)
                    Reserved: 0000000000000000
                    Target Info ...
                    Version 10.0 ...

Extracción:
NTLM Server Challenge → **************** (lo usaremos en el hash).
🔹 Frame 51 – Autenticación del cliente

Este frame contiene la respuesta del cliente. En él encontramos:

    El nombre de usuario y dominio.

    El NTProofStr (primeros 16 bytes de la respuesta).

    El bloque NTLMv2 completo (el resto de la respuesta).

a) Usuario y dominio

Dentro de la cabecera SMB2 y también en los campos del NTLMSSP_AUTH:
text

SMB2 (Server Message Block Protocol version 2), Session Setup Request, MessageId 3
    SMB2 Header
        ...
        ⬇️⬇️⬇️ CAMPO CLAVE ⬇️⬇️⬇️
        Session Id: 0x0000100000000029 Acct:*** Domain:*** Host:   <-- Usuario y dominio (ocultos)

Y más abajo, dentro del blob NTLM:
text

NTLM Secure Service Provider
    NTLMSSP identifier: NTLMSSP
    NTLM Message Type: NTLMSSP_AUTH (0x00000003)
    ...
    Domain name: ***
        Length: 26
        Maxlen: 26
        Offset: 64
    User name: ***
        Length: 16
        Maxlen: 16
        Offset: 90

Extracción:

    User name → ***

    Domain name → ***

b) NTProofStr y NTLMv2 Response

Dentro del campo NTLM Response, Wireshark desglosa la estructura NTLMv2 Response:
text

NTLM Response […]
    Length: 216
    Maxlen: 216
    Offset: 130
        ⬇️⬇️⬇️ CAMPO CLAVE ⬇️⬇️⬇️
    NTLMv2 Response […]: **********************************************************
        ⬇️⬇️⬇️ CAMPO CLAVE ⬇️⬇️⬇️
        NTProofStr: ****************   <--- 16 bytes (32 hex)
        Response Version: 1
        Hi Response Version: 1
        Z: 000000000000
        Time: Feb 19, 2024 15:48:01.113269800 UTC
        NTLMv2 Client Challenge: ****************
        Z: 00000000
        Attribute: NetBIOS domain name: CATCORP
        Attribute: NetBIOS computer name: DC01
        Attribute: DNS domain name: ***
        Attribute: DNS computer name: DC01.***
        Attribute: DNS tree name: ***
        Attribute: Timestamp
        Attribute: Target Name: cifs/DC01
        Attribute: End of list
        padding: 00000000

Extracción:

    NTProofStr → ****************

    NTLMv2 Response (blob completo) → comienza justo después del NTProofStr, es decir, desde 0101000000000000... hasta el final.
    (En la captura original el blob era largo; lo representamos como **********************************************************).

🧩 Construcción del hash para Hashcat

El modo de hashcat para NetNTLMv2 es el 5600 y el formato es:
text

Usuario::Dominio:Desafío_Servidor:NTProofStr:NTLMv2Response

Sustituyendo con los valores extraídos (todos ocultos):
text

***::***:****************:****************:**********************************************************

⚡ Ataque con Hashcat

Guardamos el hash en un archivo, por ejemplo hashcat.txt, y lanzamos el siguiente comando (el mismo que se ejecutó en la salida proporcionada):
bash

hashcat -m 5600 -a 0 hashcat.txt ../../../../../SecLists-master/Passwords/rockyou.txt

Salida de Hashcat (censurada):
text

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: ***::***:****************:****************:**********************************************************
Time.Started.....: Wed Aug 26 17:36:31 2026 (0 secs)
Time.Estimated...: Wed Aug 26 17:36:31 2026 (0 secs)
Speed.#01........: 262.4 kH/s
Recovered........: 1/1 (100.00%) Digests (total)
Candidate........: *********   <--- Contraseña recuperada

La contraseña recuperada fue: *********.
🏁 Bandera final

El userPrincipalName se construye como usuario@dominio, por lo tanto la bandera es:
text

RM{***@***:*********}

📌 Conclusión

Hemos extraído todos los campos necesarios directamente de los frames 49 y 51:

    Desafío del servidor (Frame 49 → NTLM Server Challenge).

    Usuario y dominio (Frame 51 → User name y Domain name).

    NTProofStr y NTLMv2 Response (Frame 51 → dentro de NTLM Response).
