# Writeup: Transformation
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---


Writeup: Transformation (picoCTF)


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Transformation]
```

```bash
└─# cat enc            
```

灩捯䍔䙻ㄶ形楴獟楮獴㌴摟潦弸形㝦㘲捡㕽                                                                                                


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Transformation]
```

```bash
└─# nano decode_unicode.py   
```


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Transformation]
```

```bash
└─# cat decode_unicode.py 
```

```bash
# decode.py
```

with open('enc', 'r', encoding='utf-8') as f:

```
    enc = f.read().strip()

```

### flag = ''

for ch in enc:

```
    code = ord(ch)
    high = code >> 8
    low = code & 0xFF
    flag += chr(high) + chr(low)

```

print(flag)


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Transformation]
```

```bash
└─# python3 decode_unicode.py 
```

picoCTF{******************}


-----------------------------------------------------------------------


```bash
┌──(root㉿kr3s4l4-PC)-[/home/kr3s4l4/picoctf/easy/Transformation]
```

```bash
└─# python3 -c "import sys; enc = sys.stdin.read().strip(); print(''.join([chr(ord(c) >> 8) + chr(ord(c) & 0xFF) for c in enc]))" < enc
```

picoCTF{******************}


-----------------------------------------------------------------------


1. Descripción del reto

Se proporciona el siguiente código Python:

python


enc = ''.join([chr((ord(flag[i]) << 8) + ord(flag[i + 1])) for i in range(0, len(flag), 2)])


Además, nos dan un archivo llamado enc cuyo contenido es una cadena de caracteres Unicode:

text


灩捯䍔䙻ㄶ形楴獟楮獴㌴摟潦弸形㝦㘲捡㕽


El objetivo es recuperar la flag original.

2. Entendiendo la transformación

El código original recorre la flag de dos en dos caracteres. Por cada par (flag[i], flag[i+1]):


```
    Obtiene el valor numérico (código Unicode) de cada carácter con ord().

    Desplaza el primer valor 8 bits a la izquierda: ord(flag[i]) << 8 (equivale a multiplicar por 256).

    Suma el segundo valor: (ord(flag[i]) << 8) + ord(flag[i+1]).

    Convierte ese número entero en un carácter Unicode con chr().

```

Ejemplo: Si flag = "AB" → ord('A')=65, ord('B')=66 → (65<<8)+66 = 16640+66 = 16706 → chr(16706) que es '䀂'.


Como resultado, la cadena transformada tiene la mitad de longitud que la original (cada dos caracteres se convierten en uno).

3. Proceso inverso (de la cadena enc a la flag)

Dado un carácter c de enc:


```
    code = ord(c) → obtenemos el número entero.

    El carácter original de la primera posición del par es el byte alto: high = code >> 8 (desplazamiento a la derecha 8 bits, equivale a dividir entre 256 y quedarse con la parte entera).

    El carácter original de la segunda posición del par es el byte bajo: low = code & 0xFF (máscara para quedarse con los 8 bits menos significativos).

    Luego se reconstruye el par: chr(high) + chr(low).

```

Al aplicar esto a todos los caracteres de enc y concatenar los resultados, obtenemos la flag original.

4. Solución manual paso a paso (opcional)

Podemos calcularlo con ayuda de una tabla Unicode o manualmente:

```bash
#	Carácter enc	Código Unicode (hex)	Byte alto (hex → ASCII)	Byte bajo (hex → ASCII)	Par reconstruido
```

1	灩		0x7069	0x70 → 'p'	0x69 → 'i'		pi

2	捯		0x636F	0x63 → 'c'	0x6F → 'o'		co

3	䍔		0x4354	0x43 → 'C'	0x54 → 'T'		CT

4	䙻		0x467B	0x46 → 'F'	0x7B → '{'		F{

5	ㄶ		0x3136	0x31 → '1'	0x36 → '6'		16

6	形		0x5F62	0x5F → '_'	0x62 → 'b'		_b

7	楴		0x6974	0x69 → 'i'	0x74 → 't'		it

8	獟		0x735F	0x73 → 's'	0x5F → '_'		s_

9	楮		0x696E	0x69 → 'i'	0x6E → 'n'		in

10	獴		0x7374	0x73 → 's'	0x74 → 't'		st

11	㌴		0x3334	0x33 → '3'	0x34 → '4'		34

12	摟		0x645F	0x64 → 'd'	0x5F → '_'		d_

13	潦		0x6F66	0x6F → 'o'	0x66 → 'f'		of

14	弸		0x5F38	0x5F → '_'	0x38 → '8'		_8

15	形		0x5F62	0x5F → '_'	0x62 → 'b'		_b

16	㝦		0x3766	0x37 → '7'	0x66 → 'f'		7f

17	㘲		0x3632	0x36 → '6'	0x32 → '2'		62

18	捡		0x6361	0x63 → 'c'	0x61 → 'a'		ca

19	㕽		0x357D	0x35 → '5'	0x7D → '}'		5}


Uniendo todos los pares:

picoCTF{16_bits_inst34d_of_8_b7f62ca5}

5. Solución automática con script

Podemos usar Python para hacer la decodificación de forma inmediata:

python


```bash
# decode.py
```

with open('enc', 'r', encoding='utf-8') as f:

```
    enc = f.read().strip()

```

### flag = ''

for ch in enc:

```
    code = ord(ch)
    high = code >> 8
    low = code & 0xFF
    flag += chr(high) + chr(low)

```

print(flag)


Ejecución:

bash


python3 decode.py


Salida:

text


picoCTF{******************}


También se puede hacer en una línea:

bash


python3 -c "import sys; enc = sys.stdin.read().strip(); print(''.join([chr(ord(c)>>8)+chr(ord(c)&0xFF) for c in enc]))" < enc

}


Conclusión:

El reto enseña cómo se pueden empaquetar dos caracteres en uno mediante desplazamiento de bits y cómo revertir el proceso.

Es un buen ejemplo de codificación simple y manipulación de datos a bajo nivel.

