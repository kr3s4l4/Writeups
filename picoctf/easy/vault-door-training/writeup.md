# Writeup: vault-door-training
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

Writeup: VaultDoorTraining

Descripción del desafío


Se nos proporciona el código fuente de un programa Java que simula una bóveda de entrenamiento. El programa solicita una contraseña y la valida. Nuestro objetivo es encontrar la contraseña correcta para abrir la bóveda.

### Análisis del código fuente


El archivo VaultDoorTraining.java contiene lo siguiente:

java


import java.util.*;


class VaultDoorTraining {

```
    public static void main(String args[]) {
        VaultDoorTraining vaultDoor = new VaultDoorTraining();
        Scanner scanner = new Scanner(System.in); 
        System.out.print("Enter vault password: ");
        String userInput = scanner.next();
        String input = userInput.substring("picoCTF{".length(), userInput.length()-1);
        if (vaultDoor.checkPassword(input)) {
            System.out.println("Access granted.");
        } else {
            System.out.println("Access denied!");
        }
   }

    public boolean checkPassword(String password) {
        return password.equals("w4rm1ng_Up_w1tH_jAv4_000wYdiGTvt");
    }
```

}


¿Qué hace el programa?


```
    Pide al usuario que introduzca una contraseña.

    Toma la entrada del usuario y extrae una subcadena: desde la posición "picoCTF{".length() (que es 8, porque "picoCTF{" tiene 8 caracteres) hasta el penúltimo carácter (userInput.length()-1). Esto elimina el prefijo picoCTF{ y el sufijo }.

    Llama al método checkPassword con esa subcadena.

    El método checkPassword simplemente compara la subcadena con la cadena "w4rm1ng_Up_w1tH_jAv4_000wYdiGTvt".

```

Observación importante


El programa asume que la entrada del usuario tendrá el formato picoCTF{...}. Si no es así, substring lanzará una excepción, pero en el contexto del desafío se espera que el usuario introduzca una contraseña válida en ese formato.

Vulnerabilidad


La contraseña está escrita en texto plano dentro del código fuente. Cualquier persona que pueda leer el archivo VaultDoorTraining.java (por ejemplo, si el código está alojado en un servidor accesible o si se obtiene mediante ingeniería inversa) puede obtener la contraseña inmediatamente.


El comentario en el código lo reconoce irónicamente:


```
    "Is it safe to put the password in the source code? What if somebody stole our source code? Then they would know what our password is."

```

Extracción de la contraseña


La cadena que se compara es:

text


w4rm1ng_Up_w1tH_jAv4_000wYdiGTvt


Por lo tanto, la entrada completa que debemos proporcionar al programa es:

text


picoCTF{w4rm1ng_Up_w1tH_jAv4_000wYdiGTvt}


Comprobación


Si ejecutamos el programa e introducimos esa contraseña,

el programa extraerá el contenido entre las llaves (w4rm1ng_Up_w1tH_jAv4_000wYdiGTvt),

lo comparará con la cadena hardcodeada, y como son iguales, mostrará "Access granted.".


Lección aprendida


Nunca se deben almacenar contraseñas o secretos en texto plano dentro del código fuente, especialmente si el código es distribuido o accesible de alguna forma. Para entornos reales se utilizan técnicas como hash + salt, variables de entorno, o sistemas de gestión de secretos.

