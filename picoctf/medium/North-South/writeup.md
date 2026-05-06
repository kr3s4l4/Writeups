# Writeup: North-South
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

WRITEUP de North-South


1. Descripción del reto

El enunciado dice:


```
    He configurado enrutamiento basado en geolocalización. ¿Puedes engañarlo? Intentas obtener la flag, pero hay una trampa: el acceso al servicio real está restringido según tu ubicación geográfica. Solo las peticiones desde una región específica se enrutan al servidor que tiene la flag. El resto son enviados a algún sitio… menos interesante.

```

Se nos proporciona un archivo de configuración de Nginx (nginx.conf) y una dirección web:

http://lonely-island.picoctf.net:65305/


El objetivo es conseguir la flag.

2. Análisis del fichero nginx.conf

El contenido es:

nginx


load_module /usr/lib/nginx/modules/ngx_http_geoip2_module.so;


worker_processes 1;

events { worker_connections 1024; }


http {

```
    include       mime.types;
    default_type  application/octet-stream;

    geoip2 /etc/nginx/GeoLite2-Country.mmdb {
        auto_reload 5m;
        $geoip2_data_country_code default=ZZ country iso_code;
    }

    upstream north {
        server 127.0.0.1:8000;
    }

    upstream south {
        server 127.0.0.1:9000;
    }

    server {
        listen 80;

        location / {
            if ($geoip2_data_country_code = IS) {
                proxy_pass http://south;
            }

            proxy_pass http://north;
        }
    }
```

}


Interpretación:


```
    Se carga el módulo ngx_http_geoip2_module para determinar el país de la IP del cliente usando la base de datos GeoLite2-Country.mmdb.

    La variable $geoip2_data_country_code contiene el código de país de dos letras (ej. US, ES, IS). Si no se puede determinar, se asigna ZZ.

    Hay dos upstream:

        north: escucha en el puerto 8000 (local).

        south: escucha en el puerto 9000 (local).

    En el bloque location /:

        Si el país es IS (Islandia), redirige el tráfico al upstream south.

        En caso contrario (cualquier otro país), redirige al upstream north.

```

Por tanto, solo las peticiones originadas desde una IP islandesa obtendrán la respuesta del servidor south (que es el que contiene la flag). El resto de los visitantes ven el contenido del north, que probablemente es un señuelo o una página sin flag.

3. Verificación inicial

Sin ningún truco, accedemos desde nuestra IP real (por ejemplo, EE.UU.):

bash


curl -v http://lonely-island.picoctf.net:65305/


Obtenemos una página HTML normal, sin flag. O incluso un mensaje como "Welcome from the North". No hay flag.


Podemos confirmar el país de nuestra IP usando servicios como ifconfig.co.

4. Estrategia para resolver el reto

Necesitamos hacer que nuestra petición parezca provenir de Islandia (código IS). Hay varias formas:


```
    Usar una VPN con servidores en Islandia.

    Usar un proxy SOCKS/HTTP situado en Islandia.

    Usar la red Tor forzando un nodo de salida islandés.

```

Dado que Tor es gratuito y fácil de configurar, lo elegimos.

5. Configuración de Tor
5.1. Instalar e iniciar Tor

bash


sudo apt update

sudo apt install tor -y

sudo systemctl start tor


5.2. Forzar salida en Islandia


Editamos el archivo de configuración /etc/tor/torrc (o añadimos las líneas al final):

bash


echo -e "ExitNodes {IS}\nStrictNodes 1" | sudo tee -a /etc/tor/torrc


```
    ExitNodes {IS}: indica a Tor que el nodo de salida debe estar en Islandia.

    StrictNodes 1: fuerza que se cumpla estrictamente, sin permitir otros países si no hay nodos islandeses disponibles.

```

5.3. Reiniciar Tor

bash


sudo systemctl restart tor


5.4. Verificar que la IP de salida es islandesa

bash


torsocks curl ifconfig.me


Podemos comprobar la IP resultante en ipinfo.io o similar. Si no es islandesa, esperar unos segundos o reiniciar Tor de nuevo.

6. Obtener la flag

Con Tor activo y configurado, hacemos la petición al servicio:

bash


torsocks curl http://lonely-island.picoctf.net:65305/


Respuesta obtenida:

html


<!DOCTYPE html>

<html>

```
    <head>
        <meta charset="utf-8" />
        <title>North-South</title>
        ...
    </head>
    <body>
        ...
        <h1>Welcome!!</h1>
        <p>picoCTF{g30_b453d_r0u71n9_da3971e1}</p>
        ...
    </body>
```

</html>


La flag aparece directamente en el HTML.

7. Explicación del éxito

Al enviar la petición a través de Tor, la IP de origen que ve el servidor Nginx es la del nodo de salida (ubicado en Islandia). La regla if ($geoip2_data_country_code = IS) se cumple, y el proxy_pass redirige la conexión al upstream south (puerto 9000), que es el servidor que contiene la flag. El upstream north (puerto 8000) nunca es alcanzado.

8. Alternativas posibles

```
    Proxy HTTP/SOCKS de Islandia: buscar una lista de proxies públicos (ej. spys.one) y usar curl -x http://ip:puerto <URL>.

    VPN gratuita con servidor en Islandia: algunas como ProtonVPN (versión gratuita limitada) o Windscribe.

    Servidor en la nube: lanzar una instancia en AWS eu-north-1 (Estocolmo, aunque no es Islandia, pero a veces la base de datos GeoIP lo asigna como SE; no serviría). Mejor usar una VPS en Islandia real, pero es más costoso.

```

Tor es la opción más rápida y económica.

9. Flag final
text


picoCTF{***********}


10. Lecciones aprendidas

```
    El enrutamiento basado en geolocalización es frágil si el atacante puede controlar su IP de origen.

    Herramientas como Tor permiten evadir fácilmente estas restricciones si se permite la salida a cualquier país.

    La configuración de Nginx no debe confiar únicamente en la IP remota para proteger recursos sensibles; se necesitan mecanismos adicionales como autenticación o tokens.
```

