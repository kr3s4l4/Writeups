# Writeup: Perceptron Play Alpha

**Categoría:** Artificial Intelligence  
**Dificultad:** Easy  
**Autor:** LT 'syreal' Jones  
**Plataforma:** picoCTF / Cylab Academy  

## Objetivo del reto

El reto consiste en jugar con los pesos (`w1`, `w2`) y el sesgo (`b`) de un perceptrón simple de 2 dimensiones. El objetivo es encontrar una combinación de parámetros que consiga separar correctamente todos los puntos etiquetados del conjunto de entrenamiento.

## Conexión inicial

```bash
nc aureolin-pixie.cylabacademy.net 53815

Al conectarnos, vemos un menú interactivo que nos permite modificar los parámetros del perceptrón y comprobar si la clasificación es correcta.
Análisis del problema

El perceptrón es un clasificador lineal que toma una entrada (x, y) y calcula la activación:
a=w1⋅x+w2⋅y+b
a=w1⋅x+w2⋅y+b

Si a >= 0, la salida del perceptrón es 1 (clase positiva). Si a < 0, la salida es 0 (clase negativa).

La frontera de decisión es una línea recta definida por:
w1⋅x+w2⋅y+b=0
w1⋅x+w2⋅y+b=0

Es decir:
Conjunto de datos

Los puntos dados son:
Punto	Etiqueta
(-3,-2)	0
(-1,-1)	0
(-4,-2)	0
(3,1)	1
(2,2)	1
(1,3)	1

Se puede ver que los puntos positivos están en la parte superior derecha y los negativos en la inferior izquierda. Esto sugiere que los datos son linealmente separables, es decir, existe al menos una línea recta que los separa completamente.
Estrategia de resolución
Primer intento: set 0 2 0

Este comando establece w1=0, w2=2, b=0. La ecuación de la frontera es:
0⋅x+2⋅y+0=0⇒y=0
0⋅x+2⋅y+0=0⇒y=0

Es decir, el eje X. Esta línea separa correctamente los puntos positivos (y > 0) de los negativos (y < 0). Al ejecutar CHECK, vemos que todos los puntos están bien clasificados.
text

> set 0 2 0
...
> check
Perfect! All points are classified correctly.
academy{11n34r1y_53p4r4813_a4f2a27b}

Segundo intento: set 2 0 -2

Este comando establece w1=2, w2=0, b=-2. La ecuación de la frontera es:
2⋅x+0⋅y−2=0⇒x=1
2⋅x+0⋅y−2=0⇒x=1

Es decir, una línea vertical en x = 1. Esta línea también separa correctamente los puntos positivos (x > 1) de los negativos (x < 1). Al ejecutar CHECK, también obtenemos la flag.
text

> set 2 0 -2
...
> check
Perfect! All points are classified correctly.
academy{***********************}

¿Por qué hay múltiples soluciones?

Este problema tiene infinitas soluciones porque los datos son linealmente separables y el perceptrón solo necesita encontrar una línea que los separe, no la única.

Cualquier combinación de pesos y sesgo que defina una línea que deje todos los puntos negativos a un lado y todos los positivos al otro es válida.
Ejemplos de soluciones válidas:
w1	w2	b	Frontera	¿Separa?
0	2	0	y = 0	Sí
2	0	-2	x = 1	Sí
1	1	-3	x + y = 3	Sí
1	2	-5	x + 2y = 5	Sí
-1	1	2	-x + y = -2	Sí

Todas estas líneas separan el conjunto de puntos correctamente. De hecho, cualquier línea que pase entre los puntos negativos y positivos funcionará.
Visualización de la separabilidad

Los puntos negativos están en la región:

    x < 1 aproximadamente

    y < 0 aproximadamente

Los puntos positivos están en:

    x > 1 aproximadamente

    y > 0 aproximadamente

Esto forma dos clústeres separados por una línea diagonal o incluso por ejes. Por eso, cualquier recta que separe ambos clústeres es una solución válida.
Conclusión

Este reto demuestra un concepto fundamental del aprendizaje automático: cuando los datos son linealmente separables, hay múltiples soluciones (de hecho, infinitas) para un clasificador lineal como el perceptrón. Todas ellas son correctas desde el punto de vista del entrenamiento, aunque no todas generalicen igual de bien a nuevos datos (sesgo inductivo).

La flag se obtiene simplemente encontrando una de esas soluciones y ejecutando CHECK.
Flag
text

academy{*************************}

text


---

Este writeup explica de forma clara y educativa el motivo por el cual hay varias combinaciones de parámetros que resuelven el reto, haciendo hincapié en el concepto de separabilidad lineal y la existencia de múltiples hiperplanos separadores.
