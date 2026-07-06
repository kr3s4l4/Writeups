# Writeup: SQL_Direct
**Categoría:** Medium
**Fecha de conversión:** 2026-05-04

---

Writeup: SQL Direct (picoCTF)

Descripción del reto


```
    Conéctate a este servidor PostgreSQL y encuentra la flag.
    psql -h saturn.picoctf.net -p 50438 -U postgres pico
    Contraseña: postgres

```

Objetivo: Obtener la flag que se encuentra dentro de la base de datos.

### Análisis


Nos dan una línea de conexión a un servidor PostgreSQL remoto. El usuario es postgres, la base de datos se llama pico y la contraseña es postgres. Una vez conectados, debemos explorar la base de datos y extraer la flag.

### Solución paso a paso

1. Conexión al servidor

Abrimos una terminal y ejecutamos el comando proporcionado:

bash


psql -h saturn.picoctf.net -p 50438 -U postgres pico


Nos pide la **contraseña**: introducimos postgres.

text


psql (18.3, servidor 15.2)

Digite «help» para obtener ayuda.

pico=#


2. Exploración inicial

Dentro de psql los comandos empiezan con \ (comandos internos del cliente). Para listar las tablas del esquema public:

sql


\dt


Salida:

text


```
          Listado de tablas
 Esquema | Nombre | Tipo  |  Dueño   
```

---------+--------+-------+----------

```
 public  | flags  | tabla | postgres
```

(1 fila)


Encontramos una tabla llamada flags.

3. Consultar el contenido de la tabla

Usamos una sentencia SQL estándar:

sql


SELECT * FROM flags;


Resultado:

text


```
 id | firstname | lastname  |                address                 
```

----+-----------+-----------+----------------------------------------

```
  1 | Luke      | Skywalker | picoCTF{******************************}
  2 | Leia      | Organa    | Alderaan
  3 | Han       | Solo      | Corellia
```

(3 filas)


La flag está en la columna address de la primera fila.


Lecciones aprendidas


```
    Uso básico del cliente psql de PostgreSQL.

    Comandos internos como \dt para listar tablas.

    Consulta SQL para extraer datos.

    Las flags a veces se ocultan en columnas con nombres no obvios (address en este caso).
```

