# Writeup: Quizploit
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: Quizploit - ELF Binary Analysis Quiz


En este desafío se presenta un cuestionario interactivo que evalúa conocimientos básicos sobre análisis de binarios ELF, vulnerabilidades de desbordamiento de búfer y técnicas de explotación. Se proporciona un binario vuln y su código fuente vuln.c. A continuación se explica detalladamente cada pregunta y la justificación de las respuestas.

Contexto inicial


Se nos da un binario ELF y su código fuente en C. El programa contiene una función win() que imprime la flag usando system("cat flag.txt"), pero nunca es llamada. La función vuln() declara un búfer de tamaño 0x15 (21 bytes) y lee hasta 0x90 (144 bytes) con fgets, lo que introduce un desbordamiento de búfer.

Pregunta 0x1: Arquitectura del binario



```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# objdump -d vuln           
```


vuln:     formato del fichero elf64-x86-64



Desensamblado de la sección .init:


0000000000401000 <_init>:

```
  401000:       f3 0f 1e fa             endbr64
  401004:       48 83 ec 08             sub    $0x8,%rsp
  401008:       48 8b 05 e9 2f 00 00    mov    0x2fe9(%rip),%rax        # 403ff8 <__gmon_start__@Base>
  40100f:       48 85 c0                test   %rax,%rax
  401012:       74 02                   je     401016 <_init+0x16>
  401014:       ff d0                   call   *%rax
  401016:       48 83 c4 08             add    $0x8,%rsp
  40101a:       c3                      ret

```

Desensamblado de la sección .plt:


0000000000401020 <.plt>:

```
  401020:       ff 35 e2 2f 00 00       push   0x2fe2(%rip)        # 404008 <_GLOBAL_OFFSET_TABLE_+0x8>
  401026:       f2 ff 25 e3 2f 00 00    bnd jmp *0x2fe3(%rip)        # 404010 <_GLOBAL_OFFSET_TABLE_+0x10>
  40102d:       0f 1f 00                nopl   (%rax)
  401030:       f3 0f 1e fa             endbr64
  401034:       68 00 00 00 00          push   $0x0
  401039:       f2 e9 e1 ff ff ff       bnd jmp 401020 <_init+0x20>
  40103f:       90                      nop
  401040:       f3 0f 1e fa             endbr64
  401044:       68 01 00 00 00          push   $0x1
  401049:       f2 e9 d1 ff ff ff       bnd jmp 401020 <_init+0x20>
  40104f:       90                      nop
  401050:       f3 0f 1e fa             endbr64
  401054:       68 02 00 00 00          push   $0x2
  401059:       f2 e9 c1 ff ff ff       bnd jmp 401020 <_init+0x20>
  40105f:       90                      nop

```

Desensamblado de la sección .plt.sec:


0000000000401060 <system@plt>:

```
  401060:       f3 0f 1e fa             endbr64
  401064:       f2 ff 25 ad 2f 00 00    bnd jmp *0x2fad(%rip)        # 404018 <system@GLIBC_2.2.5>
  40106b:       0f 1f 44 00 00          nopl   0x0(%rax,%rax,1)

```

0000000000401070 <fgets@plt>:

```
  401070:       f3 0f 1e fa             endbr64
  401074:       f2 ff 25 a5 2f 00 00    bnd jmp *0x2fa5(%rip)        # 404020 <fgets@GLIBC_2.2.5>
  40107b:       0f 1f 44 00 00          nopl   0x0(%rax,%rax,1)

```

0000000000401080 <fwrite@plt>:

```
  401080:       f3 0f 1e fa             endbr64
  401084:       f2 ff 25 9d 2f 00 00    bnd jmp *0x2f9d(%rip)        # 404028 <fwrite@GLIBC_2.2.5>
  40108b:       0f 1f 44 00 00          nopl   0x0(%rax,%rax,1)

```

Desensamblado de la sección .text:


0000000000401090 <_start>:

```
  401090:       f3 0f 1e fa             endbr64
  401094:       31 ed                   xor    %ebp,%ebp
  401096:       49 89 d1                mov    %rdx,%r9
  401099:       5e                      pop    %rsi
  40109a:       48 89 e2                mov    %rsp,%rdx
  40109d:       48 83 e4 f0             and    $0xfffffffffffffff0,%rsp
  4010a1:       50                      push   %rax
  4010a2:       54                      push   %rsp
  4010a3:       45 31 c0                xor    %r8d,%r8d
  4010a6:       31 c9                   xor    %ecx,%ecx
  4010a8:       48 c7 c7 eb 11 40 00    mov    $0x4011eb,%rdi
  4010af:       ff 15 3b 2f 00 00       call   *0x2f3b(%rip)        # 403ff0 <__libc_start_main@GLIBC_2.34>
  4010b5:       f4                      hlt
  4010b6:       66 2e 0f 1f 84 00 00    cs nopw 0x0(%rax,%rax,1)
  4010bd:       00 00 00 

```

00000000004010c0 <_dl_relocate_static_pie>:

```
  4010c0:       f3 0f 1e fa             endbr64
  4010c4:       c3                      ret
  4010c5:       66 2e 0f 1f 84 00 00    cs nopw 0x0(%rax,%rax,1)
  4010cc:       00 00 00 
  4010cf:       90                      nop

```

00000000004010d0 <deregister_tm_clones>:

```
  4010d0:       b8 40 40 40 00          mov    $0x404040,%eax
  4010d5:       48 3d 40 40 40 00       cmp    $0x404040,%rax
  4010db:       74 13                   je     4010f0 <deregister_tm_clones+0x20>
  4010dd:       b8 00 00 00 00          mov    $0x0,%eax
  4010e2:       48 85 c0                test   %rax,%rax
  4010e5:       74 09                   je     4010f0 <deregister_tm_clones+0x20>
  4010e7:       bf 40 40 40 00          mov    $0x404040,%edi
  4010ec:       ff e0                   jmp    *%rax
  4010ee:       66 90                   xchg   %ax,%ax
  4010f0:       c3                      ret
  4010f1:       66 66 2e 0f 1f 84 00    data16 cs nopw 0x0(%rax,%rax,1)
  4010f8:       00 00 00 00 
  4010fc:       0f 1f 40 00             nopl   0x0(%rax)

```

0000000000401100 <register_tm_clones>:

```
  401100:       be 40 40 40 00          mov    $0x404040,%esi
  401105:       48 81 ee 40 40 40 00    sub    $0x404040,%rsi
  40110c:       48 89 f0                mov    %rsi,%rax
  40110f:       48 c1 ee 3f             shr    $0x3f,%rsi
  401113:       48 c1 f8 03             sar    $0x3,%rax
  401117:       48 01 c6                add    %rax,%rsi
  40111a:       48 d1 fe                sar    $1,%rsi
  40111d:       74 11                   je     401130 <register_tm_clones+0x30>
  40111f:       b8 00 00 00 00          mov    $0x0,%eax
  401124:       48 85 c0                test   %rax,%rax
  401127:       74 07                   je     401130 <register_tm_clones+0x30>
  401129:       bf 40 40 40 00          mov    $0x404040,%edi
  40112e:       ff e0                   jmp    *%rax
  401130:       c3                      ret
  401131:       66 66 2e 0f 1f 84 00    data16 cs nopw 0x0(%rax,%rax,1)
  401138:       00 00 00 00 
  40113c:       0f 1f 40 00             nopl   0x0(%rax)

```

0000000000401140 <__do_global_dtors_aux>:

```
  401140:       f3 0f 1e fa             endbr64
  401144:       80 3d 0d 2f 00 00 00    cmpb   $0x0,0x2f0d(%rip)        # 404058 <completed.0>
  40114b:       75 13                   jne    401160 <__do_global_dtors_aux+0x20>
  40114d:       55                      push   %rbp
  40114e:       48 89 e5                mov    %rsp,%rbp
  401151:       e8 7a ff ff ff          call   4010d0 <deregister_tm_clones>
  401156:       c6 05 fb 2e 00 00 01    movb   $0x1,0x2efb(%rip)        # 404058 <completed.0>
  40115d:       5d                      pop    %rbp
  40115e:       c3                      ret
  40115f:       90                      nop
  401160:       c3                      ret
  401161:       66 66 2e 0f 1f 84 00    data16 cs nopw 0x0(%rax,%rax,1)
  401168:       00 00 00 00 
  40116c:       0f 1f 40 00             nopl   0x0(%rax)

```

0000000000401170 <frame_dummy>:

```
  401170:       f3 0f 1e fa             endbr64
  401174:       eb 8a                   jmp    401100 <register_tm_clones>

```

0000000000401176 <win>:

```
  401176:       f3 0f 1e fa             endbr64
  40117a:       55                      push   %rbp
  40117b:       48 89 e5                mov    %rsp,%rbp
  40117e:       bf 04 20 40 00          mov    $0x402004,%edi
  401183:       e8 d8 fe ff ff          call   401060 <system@plt>
  401188:       90                      nop
  401189:       5d                      pop    %rbp
  40118a:       c3                      ret

```

000000000040118b <vuln>:

```
  40118b:       f3 0f 1e fa             endbr64
  40118f:       55                      push   %rbp
  401190:       48 89 e5                mov    %rsp,%rbp
  401193:       48 83 ec 20             sub    $0x20,%rsp
  401197:       48 c7 45 e0 00 00 00    movq   $0x0,-0x20(%rbp)
  40119e:       00 
  40119f:       48 c7 45 e8 00 00 00    movq   $0x0,-0x18(%rbp)
  4011a6:       00 
  4011a7:       c7 45 f0 00 00 00 00    movl   $0x0,-0x10(%rbp)
  4011ae:       c6 45 f4 00             movb   $0x0,-0xc(%rbp)
  4011b2:       48 8b 05 87 2e 00 00    mov    0x2e87(%rip),%rax        # 404040 <stdout@GLIBC_2.2.5>
  4011b9:       48 89 c1                mov    %rax,%rcx
  4011bc:       ba 10 00 00 00          mov    $0x10,%edx
  4011c1:       be 01 00 00 00          mov    $0x1,%esi
  4011c6:       bf 11 20 40 00          mov    $0x402011,%edi
  4011cb:       e8 b0 fe ff ff          call   401080 <fwrite@plt>
  4011d0:       48 8b 15 79 2e 00 00    mov    0x2e79(%rip),%rdx        # 404050 <stdin@GLIBC_2.2.5>
  4011d7:       48 8d 45 e0             lea    -0x20(%rbp),%rax
  4011db:       be 90 00 00 00          mov    $0x90,%esi
  4011e0:       48 89 c7                mov    %rax,%rdi
  4011e3:       e8 88 fe ff ff          call   401070 <fgets@plt>
  4011e8:       90                      nop
  4011e9:       c9                      leave
  4011ea:       c3                      ret

```

00000000004011eb <main>:

```
  4011eb:       f3 0f 1e fa             endbr64
  4011ef:       55                      push   %rbp
  4011f0:       48 89 e5                mov    %rsp,%rbp
  4011f3:       b8 00 00 00 00          mov    $0x0,%eax
  4011f8:       e8 8e ff ff ff          call   40118b <vuln>
  4011fd:       90                      nop
  4011fe:       5d                      pop    %rbp
  4011ff:       c3                      ret

```

Desensamblado de la sección .fini:


0000000000401200 <_fini>:

```
  401200:       f3 0f 1e fa             endbr64
  401204:       48 83 ec 08             sub    $0x8,%rsp
  401208:       48 83 c4 08             add    $0x8,%rsp
  40120c:       c3                      ret

```

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# cat vuln.c 
```

```bash
#include <stdio.h>
```

```bash
#include <stdlib.h>
```


/*

This is not the challenge, just a template to answer the questions.

To get the flag, answer all the questions. 

There are no bugs in the quiz.

There are 0xD questions in total.


*/


void win(){

```
        system("cat flag.txt");
```

}


void vuln(){

```
        char buffer[0x15] = {0};
        fprintf(stdout, "\nEnter payload: ");
        fgets(buffer, 0x90, stdin);
```

}


void main(){

```
        vuln();
```

}


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# objdump -d vuln | grep win
```

0000000000401176 <win>:

```
                                                                                                
```

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# gdb -batch -ex "print win" ./vuln
```

```bash
$1 = {<text variable, no debug info>} 0x401176 <win>
```

```
                                                                                                
```

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# checksec vuln             
```

[*] '/home/kr3s4l4/picoctf/easy/Quizploit/vuln'

```
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No

```

----------------------------------------------------------------------------------------------

Pregunta: ¿Es un ELF de 32 bits o 64 bits?

Respuesta: 64-bit


### Explicación:

Al inspeccionar el binario con file vuln o simplemente observando la cadena /lib64/ld-linux-x86-64.so.2 en su contenido,

se confirma que es un ejecutable de 64 bits.

Además, el código fuente no especifica flags de compilación,

por lo que por defecto el compilador genera un binario para la arquitectura del sistema (x86_64).

Pregunta 0x2: Tipo de enlace (linking)


Pregunta: ¿El binario es estático o dinámico?

Respuesta: dynamic


### Explicación:

El programa utiliza funciones de la biblioteca estándar como fprintf, fgets y system.

Estas dependencias se resuelven en tiempo de ejecución mediante bibliotecas compartidas (.so). Al ejecutar file vuln se observa algo como dynamically linked,

y en el contenido del binario aparecen nombres como libc.so.6.

Pregunta 0x3: Símbolos de depuración


Pregunta: ¿El binario está "stripped" o "not stripped"?

Respuesta: not stripped


### Explicación:

El binario conserva información de símbolos, como se aprecia en la salida de cat vuln

donde aparecen nombres de funciones (main, vuln, win) y secciones como .symtab.

Por defecto, si no se usa la opción -s al compilar, se incluyen los símbolos.

El comando file vuln lo confirma con not stripped.

Pregunta 0x4: Tamaño del búfer en vuln()


Pregunta: ¿Cuál es el tamaño del búfer en bytes?

Respuesta: 0x15


### Explicación:

En el código fuente, dentro de vuln(), se declara:

c


char buffer[0x15] = {0};


Por lo tanto, el búfer tiene 0x15 bytes (21 en decimal).

Pregunta 0x5: Bytes leídos por fgets


Pregunta: ¿Cuántos bytes se leen en el búfer?

Respuesta: 0x90


### Explicación:

La llamada a fgets es:



fgets(buffer, 0x90, stdin);


El segundo argumento indica el máximo número de bytes a leer,

incluyendo el carácter nulo terminador.

Por tanto, se intentan leer 0x90 bytes.

Pregunta 0x6: ¿Existe vulnerabilidad de desbordamiento de búfer?


Pregunta: ¿Hay vulnerabilidad de buffer overflow?

Respuesta: yes


### Explicación:

El búfer tiene capacidad para 0x15 bytes, pero fgets permite leer hasta 0x90 bytes.

Esto permite escribir datos más allá del límite del arreglo,

sobrescribiendo la memoria adyacente (incluyendo la dirección de retorno).

Pregunta 0x7: Función C que causa el desbordamiento


Pregunta: Nombra una función estándar de C que pueda causar un buffer overflow en el código.

Respuesta: fgets


### Explicación:

Aunque fgets normalmente es segura porque limita la entrada, en este caso se le pasa un tamaño mayor al del búfer,

provocando el desbordamiento.

La función en sí misma no es insegura, pero su uso incorrecto sí lo es.

Pregunta 0x8: Función que no es llamada en ningún lugar


Pregunta: ¿Cuál es el nombre de la función que no se llama en ninguna parte del programa?

Respuesta: win


### Explicación:

La función win() está definida pero nunca es invocada desde main() ni desde otra función.

Es el objetivo clásico de un ataque de redirección de flujo.

Pregunta 0x9: Tipo de ataque que explota esta vulnerabilidad


Pregunta: ¿Qué tipo de ataque podría explotar esta vulnerabilidad?

Respuesta: buffer overflow


### Explicación:

La vulnerabilidad identificada es un desbordamiento de búfer,

que permite sobrescribir la dirección de retorno y redirigir la ejecución a la función win().

Pregunta 0xa: Bytes de desbordamiento posibles


Pregunta: ¿Cuántos bytes de desbordamiento son posibles?

Respuesta: 0x7B


### Explicación:

Se leen 0x90 bytes en un búfer de 0x15. El desbordamiento es la diferencia:

0x90 - 0x15 = 0x7B (123 bytes).

Estos bytes extra pueden sobrescribir la dirección de retorno y otras variables locales.

Pregunta 0xb: Protección habilitada en el binario


Pregunta: ¿Qué protección está habilitada?

Respuesta: NX


### Explicación:

Al ejecutar checksec vuln (herramienta que forma parte de pwntools o gdb-peda) se observa que NX (No-eXecute) está activado.

Esto impide la ejecución de código en regiones de memoria como el stack.

Otras protecciones como PIE o Canary no están activadas en este binario.

Pregunta 0xc: Técnica para evadir NX


Pregunta: ¿Qué técnica de explotación puede evadir NX?

Respuesta: ROP (Return-Oriented Programming)


### Explicación:

Con NX activado, no se puede ejecutar shellcode en el stack.

En su lugar, se utiliza ROP, que encadena pequeños fragmentos de código existentes en el binario (gadgets) terminados en ret, para lograr una ejecución arbitraria.

En este caso, se puede redirigir a win() directamente sin necesidad de shellcode, pero ROP es la técnica general para bypass NX.

Pregunta 0xd: Dirección de win()


Pregunta: ¿Cuál es la dirección de win() en hex?

Respuesta: 0x401176


### Explicación:

Usando

objdump -d vuln | grep win o gdb -batch -ex "print win" ./vuln

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# objdump -d vuln | grep win
```

0000000000401176 <win>:

```
                                                                                                
```

```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Quizploit]
```

```bash
└─# gdb -batch -ex "print win" ./vuln
```

```bash
$1 = {<text variable, no debug info>} 0x401176 <win>
```

se obtiene la dirección exacta:

text


0000000000401176 <win>:


Por lo tanto, la dirección es 0x401176.

Resumen y obtención de la flag


Al responder correctamente las 13 preguntas, el servidor muestra la **flag**:

text


picoCTF{***************}


Conclusión


Este ejercicio demuestra la importancia de comprender las características de un binario ELF, identificar vulnerabilidades básicas y conocer las técnicas de explotación más comunes.

A través del análisis estático y el uso de herramientas como file, objdump y gdb, se pudo caracterizar el binario y responder con precisión a todas las preguntas.

