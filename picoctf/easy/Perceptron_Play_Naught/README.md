Writeup: Perceptron Play Naught
Descripción del Reto

El reto consiste en conectarse a un servidor que ejecuta un simulador de perceptrón. Hay que ajustar los pesos (w1, w2) y el sesgo (b) para clasificar correctamente 7 puntos etiquetados como clase 0 o clase 1.

Conexión:
bash

nc aureolin-pixie.cylabacademy.net 54993

Estado Inicial

Al conectarnos, vemos el siguiente estado:

Pesos iniciales: w1 = 1, w2 = -1, b = 0

Puntos y su clasificación:
Punto	Label	Perceptrón	Activación
(-4,-1)	0	0	-3
(-1,+2)	1	0	-3
(0,-1)	0	1	1
(0,+2)	1	0	-2
(2,-1)	0	1	3
(3,+1)	1	1	2
(4,+2)	1	1	2

Gráfico inicial:
text

+4         |       /
+3         |     /  
+2       x x   /   1
+1         | /   1  
+0 - - - - / - - - -
-1 0     / x   x    
-2     /   |        
-3   /     |        
-4 /       |        
   -4-3-2-1+0+1+2+3+4

Las x indican puntos mal clasificados. Hay varios errores.
Pruebas Realizadas
Prueba 1: SET -2 2 1
text

> set -2 2 1

Resultado:

    Pesos: w1=-2, w2=2, b=1

    Puntos mal clasificados: (-4,-1) predice 1 (debería 0), (3,1) predice 0 (debería 1), (4,2) predice 0 (debería 1)

Gráfico:
text

+4         |       /
+3         |       /
+2       1 1   / / x
+1         |   / x  
+0 - - - - / / - - -
-1 x       0   0    
-2     / / |        
-3     /   |        
-4 / /     |        
   -4-3-2-1+0+1+2+3+4

Peor que el inicial.
Prueba 2: SET 2 2 0
text

> set 2 2 0

Resultado:

    Pesos: w1=2, w2=2, b=0

    Solo (2,-1) mal clasificado (predice 1, debería 0)

Gráfico:
text

+4 /       |        
+3   /     |        
+2     / 1 1       1
+1       / |     1  
+0 - - - - / - - - -
-1 0       0 / x    
-2         |   /    
-3         |     /  
-4         |       /
   -4-3-2-1+0+1+2+3+4

Mejoró mucho, solo un error.
Prueba 3: SET 2 2 -1
text

> set 2 2 -1

Resultado:

    Pesos: w1=2, w2=2, b=-1

    Sigue fallando en (2,-1)

Gráfico:
text

+4 / /     |        
+3     /   |        
+2     / 1 1       1
+1         /     1  
+0 - - - - / / - - -
-1 0       0   x    
-2         |   / /  
-3         |       /
-4         |       /
   -4-3-2-1+0+1+2+3+4

Prueba 4: SET 2 2 1
text

> set 2 2 1

Resultado:

    Pesos: w1=2, w2=2, b=1

    Sigue fallando en (2,-1)

Gráfico:
text

+4 /       |        
+3 /       |        
+2   / / 1 1       1
+1     /   |     1  
+0 - - - / / - - - -
-1 0       0   x    
-2         | / /    
-3         |   /    
-4         |     / /
   -4-3-2-1+0+1+2+3+4

Prueba 5: SET 2 -2 0
text

> set 2 -2 0

Resultado:

    Pesos: w1=2, w2=-2, b=0

    Varios errores: (-1,2) predice 0 (debería 1), (0,2) predice 0 (debería 1)

Gráfico:
text

+4         |       /
+3         |     /  
+2       x x   /   1
+1         | /   1  
+0 - - - - / - - - -
-1 0     / x   x    
-2     /   |        
-3   /     |        
-4 /       |        
   -4-3-2-1+0+1+2+3+4

Prueba 6: SET -2 2 0
text

> set -2 2 0

Resultado:

    Pesos: w1=-2, w2=2, b=0

    Errores: (3,1) predice 0, (4,2) predice 0

Gráfico:
text

+4         |       /
+3         |     /  
+2       1 1   /   x
+1         | /   x  
+0 - - - - / - - - -
-1 x     / 0   0    
-2     /   |        
-3   /     |        
-4 /       |        
   -4-3-2-1+0+1+2+3+4

Prueba 7: SET 1 1 0
text

> set 1 1 0

Resultado:

    Pesos: w1=1, w2=1, b=0

    Falla en (2,-1) y (-4,-1) da activación -5 (bien), (0,-1) da -1 (bien)

Gráfico:
text

+4 /       |        
+3   /     |        
+2     / 1 1       1
+1       / |     1  
+0 - - - - / - - - -
-1 0       0 / x    
-2         |   /    
-3         |     /  
-4         |       /
   -4-3-2-1+0+1+2+3+4

Prueba 8: SET 3 3 0
text

> set 3 3 0

Resultado:

    Pesos: w1=3, w2=3, b=0

    Sigue fallando en (2,-1)

Gráfico:
text

+4 /       |        
+3   /     |        
+2     / 1 1       1
+1       / |     1  
+0 - - - - / - - - -
-1 0       0 / x    
-2         |   /    
-3         |     /  
-4         |       /
   -4-3-2-1+0+1+2+3+4

Prueba 9: SET 2 0 0
text

> set 2 0 0

Resultado:

    Pesos: w1=2, w2=0, b=0

    Frontera vertical x=0

    Errores en (-4,-1), (-1,2) y (2,-1)

Gráfico:
text

+4         /        
+3         /        
+2       x 1       1
+1         /     1  
+0 - - - - / - - - -
-1 0       x   x    
-2         /        
-3         /        
-4         /        
   -4-3-2-1+0+1+2+3+4

Prueba 10: SET 0 2 0 - ¡SOLUCIÓN!
text

> set 0 2 0

Resultado:

    Pesos: w1=0, w2=2, b=0

    Frontera horizontal y=0

Todos los puntos bien clasificados:
Punto	Label	Perceptrón	Activación
(-4,-1)	0	0	-2
(-1,+2)	1	1	4
(0,-1)	0	0	-2
(0,+2)	1	1	4
(2,-1)	0	0	-2
(3,+1)	1	1	2
(4,+2)	1	1	4

Gráfico final:
text

+4         |        
+3         |        
+2       1 1       1
+1         |     1  
+0 / / / / / / / / /
-1 0       0   0    
-2         |        
-3         |        
-4         |        
   -4-3-2-1+0+1+2+3+4

Obtención de la Flag
text

> check
Perfect! All points are classified correctly.
academy{*******************************}

Explicación de la Solución

Al analizar los datos, todos los puntos de clase 0 tienen y < 0 y todos los de clase 1 tienen y > 0. Por tanto, una línea horizontal que separe en y = 0 es suficiente.

Configuración:

    w1 = 0 (ignora la coordenada x)

    w2 = 2 (valora la coordenada y)

    b = 0 (sin sesgo)

La activación es 2y, que es negativa para y < 0 (clase 0) y positiva para y > 0 (clase 1).
Flag
text

academy{****************************}
