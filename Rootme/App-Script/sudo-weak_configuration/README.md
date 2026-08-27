Writeup: sudo - weak configuration (Root Me)

Campo	Valor
Plataforma	Root-Me
Categoría	Escalada de Privilegios
Nivel	Fácil (5 puntos)
Usuario inicial	app-script-ch1

🎯 Objetivo

Leer el archivo oculto .passwd que se encuentra en:
/challenge/app-script/ch1/ch1cracked/

1. Primer Contacto (Intentos Directos)

Al iniciar, vemos que el archivo objetivo pertenece al usuario app-script-ch1-cracked y su grupo. Nosotros somos app-script-ch1 y no tenemos permisos de lectura.
Comprobación rápida:
bash

cat /challenge/app-script/ch1/ch1cracked/.passwd
# Resultado: Permission denied

2. Vectores Descartados (Ahorro de Tiempo)

Antes de dar con la solución, probamos las vías típicas sin éxito:
Vector	Comando	Resultado
Cambio de usuario	su app-script-ch1-cracked	Fallo de autenticación
Lectura con Python	python3 -c "open(...)"	PermissionError
Lectura con Perl	perl -e 'open(...)'	Sin permisos
Binarios SUID	find / -perm -4000	Solo binarios del sistema
Escapando con os.setuid()	python3 -c "import os; os.setuid(1401)"	Operation not permitted
Reglas de otros usuarios	sudo -u app-script-ch14-8 ...	Sorry, user is not allowed

Conclusión: No podemos leer el archivo directamente ni cambiar de usuario. Necesitamos encontrar un comando que se ejecute con los permisos del propietario (app-script-ch1-cracked).

3. El Hallazgo Clave: sudo -l

Muchos usuarios evitan sudo -l porque creen que no saben la contraseña.
Pero en este reto, la contraseña de sudo es la misma que la de login del usuario app-script-ch1 (la que usamos para conectarnos). Así que podemos ejecutarlo sin problemas.
bash

sudo -l

Salida relevante:
text

User app-script-ch1 may run the following commands on challenge02:
    (app-script-ch1-cracked) /bin/cat /challenge/app-script/ch1/notes/*

4. Análisis de la Regla (La Vulnerabilidad)

Desglosemos la regla:

    Usuario ejecutor: app-script-ch1 (nosotros).

    Usuario objetivo (RunAs): app-script-ch1-cracked (el dueño del .passwd).

    Comando permitido: /bin/cat /challenge/app-script/ch1/notes/*

🔴 El error del administrador:

El administrador usó el comodín * para permitir leer todos los archivos dentro de notes/.
Sin embargo, el comodín no impide el uso de .. (path traversal).

Es decir, podemos hacer que cat lea cualquier archivo del sistema, siempre que la ruta comience con /challenge/app-script/ch1/notes/ y luego usemos .. para salir del directorio.

5. Explotación (Path Traversal)

Queremos leer .passwd, que está en:
text

/challenge/app-script/ch1/ch1cracked/.passwd

Partimos de la ruta base permitida:
text

/challenge/app-script/ch1/notes/

Si añadimos ../ch1cracked/.passwd, la ruta final queda:
text

/challenge/app-script/ch1/notes/../ch1cracked/.passwd

    notes/.. sube un nivel → nos deja en /challenge/app-script/ch1/.

    Luego entramos a ch1cracked/.passwd.

Comando final:
bash

sudo -u app-script-ch1-cracked /bin/cat /challenge/app-script/ch1/notes/../ch1cracked/.passwd

¿Por qué funciona?
El comando se ejecuta como app-script-ch1-cracked, que sí tiene permisos de lectura sobre su propio archivo .passwd. El sistema solo verifica que el comando empiece por /bin/cat y la ruta base, pero no valida si realmente estamos dentro de notes/.
6. Resultado

Al ejecutar el comando, obtenemos la flag (la contraseña del reto). 🎉
********************

7. Lección Aprendida (Cómo se soluciona)

La configuración del archivo /etc/sudoers era débil:
sudoers

# Configuración vulnerable (NO hacer esto)
app-script-ch1 challenge02=(app-script-ch1-cracked) /bin/cat /challenge/app-script/ch1/notes/*

🔒 Configuración segura:
sudoers

# Especificar la ruta EXACTA del archivo
app-script-ch1 challenge02=(app-script-ch1-cracked) /bin/cat /challenge/app-script/ch1/notes/shared_notes

Regla de oro:
Nunca uses comodines (*) en sudoers a menos que sea estrictamente necesario y estés 100% seguro de que no se puede escapar del directorio. Siempre es mejor especificar rutas absolutas y archivos concretos.

📊 Resumen Rápido del Ataque
Paso	Acción	Clave del éxito
1	Ejecutar sudo -l	Usar la contraseña de login de app-script-ch1
2	Identificar regla con *	Notar que permite ejecutar cat como app-script-ch1-cracked
3	Construir ruta maliciosa	Usar ../ para salir del directorio notes/
4	Ejecutar	sudo -u app-script-ch1-cracked /bin/cat /challenge/app-script/ch1/notes/../ch1cracked/.passwd
5	Leer la flag	¡Objetivo completado!
