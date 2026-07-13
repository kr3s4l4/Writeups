Writeup: Neuron Meet 2D-0 - PicoCTF Challenge
📋 Descripción del Desafío

El desafío nos presenta un perceptrón 2D que actúa como una caja negra. Debemos encontrar pares de coordenadas (x, y) que hagan que el perceptrón genere una secuencia de 8 bits que corresponda al código ASCII de la letra 'p' (01110000).
🧠 ¿Qué es un Perceptrón?

Un perceptrón es el bloque más básico de una red neuronal. En 2D, funciona así:
text

Salida = 1 si (w₁·x + w₂·y + b) ≥ 0
Salida = 0 si (w₁·x + w₂·y + b) < 0

Donde:

    w₁, w₂ = pesos (inclinación de la línea)

    b = sesgo (desplazamiento de la línea)

    (x, y) = coordenadas de entrada

Visualización Conceptual

El perceptrón dibuja una línea recta en el plano 2D que separa dos regiones:
text

                    y
                    ↑
                    |
     Región 0       |       Región 1
   (No dispara)     |     (Dispara)
                    |
    ----------------|----------------→ x
                    |
                    |

La ecuación w₁·x + w₂·y + b = 0 es la línea frontera.
🔍 Exploración del Sistema
Primeras Pruebas (Pasos 1-10)
text

(1,1) → 0  (No dispara)
(2,2) → 1  (Dispara)  ← Aquí cruza la frontera
(3,3) → 1
(4,4) → 1
(5,5) → 1
(6,6) → 1
(7,7) → 1
(8,8) → 1
(9,9) → 1
(10,10) → 1

Análisis de la Frontera

De las primeras pruebas podemos deducir:
text

Cuando x=y:
(1,1) → 0
(2,2) → 1

Esto significa que la línea frontera cruza la diagonal entre (1,1) y (2,2).
Visualización de la Frontera
text

y
↑
|         Región 1 (Dispara)
|         ●(10,10)
|         ●(9,9)
|         ●(8,8)
|         ●(7,7)
|         ●(6,6)
|         ●(5,5)
|         ●(4,4)
|         ●(3,3)
|    ─────●───── Línea frontera (entre 1 y 2)
|         ●(2,2)
|         ●(1,1)  ← Región 0
|    ●(0,0)
|
└────────────────────────────────→ x

🎯 Objetivo: ASCII 'p'

El código ASCII para 'p' es 01110000 (8 bits).

Necesitamos generar esta secuencia exacta:
text

Bit 1: 0
Bit 2: 1
Bit 3: 1
Bit 4: 1
Bit 5: 0
Bit 6: 0
Bit 7: 0
Bit 8: 0

🧩 Estrategia de Resolución
Paso 1: Resetear y Empezar de Nuevo

En el paso 39, reseteamos el historial para comenzar con una pizarra limpia.
Paso 2: Encontrar la Secuencia

Ensayamos diferentes combinaciones hasta encontrar la secuencia correcta:
text

(0,0) → 0  ← Bit 1
(2,2) → 1  ← Bit 2
(3,3) → 1  ← Bit 3
(4,4) → 1  ← Bit 4
(1,1) → 0  ← Bit 5
(2,0) → 0  ← Bit 6
(3,0) → 0  ← Bit 7
(0,0) → 0  ← Bit 8

Visualización de los Puntos Usados
text

y
↑
|         Región 1 (Dispara)
|         ●(4,4)
|         ●(3,3)
|         ●(2,2)
|    ─────●───── Línea frontera
|         ●(1,1)  ← No dispara
|    ●(3,0)      ← No dispara
|    ●(2,0)      ← No dispara
|    ●(0,0)      ← No dispara (usado dos veces)
|
└────────────────────────────────→ x

🔬 ¿Por qué funcionó esta secuencia?

El perceptrón tiene pesos y sesgo desconocidos, pero basado en las respuestas, podemos deducir que:

    Puntos en la diagonal: A partir de (2,2), todos los puntos con x=y≥2 disparan

    Puntos en el eje x: (2,0) y (3,0) no disparan, pero (4,0) sí (visto en paso 38)

    Comportamiento asimétrico: (3,1) dispara (paso 20), pero (1,1) no

Esto sugiere que la línea frontera tiene una pendiente específica, probablemente cerca de:
text

w₁ = 1, w₂ = 1, b = -2.5

Verificación de la Hipótesis

Si w₁=1, w₂=1, b=-2.5:
text

(0,0): 0 + 0 - 2.5 = -2.5 < 0 → 0 ✓
(1,1): 1 + 1 - 2.5 = -0.5 < 0 → 0 ✓
(2,2): 2 + 2 - 2.5 = 1.5 ≥ 0 → 1 ✓
(3,3): 3 + 3 - 2.5 = 3.5 ≥ 0 → 1 ✓
(4,4): 4 + 4 - 2.5 = 5.5 ≥ 0 → 1 ✓
(2,0): 2 + 0 - 2.5 = -0.5 < 0 → 0 ✓
(3,0): 3 + 0 - 2.5 = 0.5 ≥ 0 → 1 ✗ (aquí fallaría)

Ajuste de Hipótesis

Probablemente los pesos reales son diferentes. Por ejemplo:
text

w₁ = 1.5, w₂ = 0.5, b = -2.0

text

(0,0): 0 - 2.0 = -2.0 < 0 → 0 ✓
(1,1): 1.5 + 0.5 - 2.0 = 0 ≥ 0 → 1 ✗ (no coincide)

La belleza de este desafío es que no necesitamos conocer los valores exactos; solo necesitamos encontrar puntos que produzcan la secuencia deseada.
🏆 La Solución Final

Después de 50 intentos, encontramos la secuencia correcta:
text

[50/128] (0,0) → 0 
[51/128] (2,2) → 1 
[52/128] (3,3) → 1 
[53/128] (4,4) → 1 
[54/128] (1,1) → 0 
[55/128] (2,0) → 0 
[56/128] (3,0) → 0 
[57/128] (0,0) → 0 

Patrón: 0 1 1 1 0 0 0 0 = 01110000 = 'p' en ASCII

🎁 La Recompensa
text

academy{*************************}

📊 Diagrama Final del Perceptrón
text

                    y
                    ↑
                    |         Región de Disparo (1)
                    |         ●(4,4) ●(3,3) ●(2,2)
                    |         ╲
                    |          ╲ Línea frontera
                    |           ╲
                    |     ●(1,1) ╲
                    |            ╲
                    |             ╲
                    |    ●(3,0)   ╲
                    |    ●(2,0)    ╲
                    |    ●(0,0)─────╲──────→ x
                    |
        Región de Silencio (0)

🔑 Conceptos Clave Aprendidos

    Perceptrón 2D: Clasificador lineal que separa puntos en dos categorías

    Frontera de Decisión: Línea (o hiperplano) que separa las regiones

    Ingeniería de Entradas: Manipular cuidadosamente las entradas para obtener salidas deseadas

    Codificación Binaria: Usar salidas de perceptrón para codificar información (ASCII)

    Resolución de Caja Negra: Deducción del comportamiento sin conocer los parámetros internos

💡 Reflexión Final

Este desafío demuestra cómo un simple perceptrón puede ser usado como un mecanismo de codificación. Aunque no conozcamos los pesos exactos, podemos "sondear" el sistema con diferentes entradas para mapear su comportamiento y lograr el resultado deseado.

Es un excelente ejemplo de cómo las redes neuronales, incluso en su forma más simple, pueden ser utilizadas para tareas complejas de procesamiento de información.
