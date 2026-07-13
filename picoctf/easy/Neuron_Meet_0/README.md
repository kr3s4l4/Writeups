Writeup: Neuron Meet 0 - PicoCTF Challenge
📋 Descripción del Desafío

Este desafío es una versión más simple del anterior: un perceptrón 1D donde solo necesitamos ingresar un número (x) para ver si el perceptrón "dispara" (1) o se queda "quieto" (0). El objetivo es generar la secuencia binaria 01110000 (ASCII de 'p').
🧠 ¿Qué es un Perceptrón 1D?

En una dimensión, el perceptrón es aún más simple:
text

Salida = 1 si (w·x + b) ≥ 0
Salida = 0 si (w·x + b) < 0

Donde:

    w = peso (pendiente)

    b = sesgo (desplazamiento)

    x = entrada (un solo número)

Visualización 1D

En 1D, la "frontera de decisión" es simplemente un punto en la recta numérica:
text

← Región 0 (No dispara) | Región 1 (Dispara) →
                         |
---|-----|-----|-----|--●--|-----|-----|-----|---→ x
  -5    -2     0     1  2.0  3     5     7    10
                         ↑
                    Frontera (umbral)

Todo número menor que el umbral → No dispara (0)
Todo número mayor o igual que el umbral → Dispara (1)
🔍 Exploración del Sistema
Primeras Pruebas (Pasos 4-7)
text

x=1  → 0 (No dispara)
x=2  → 1 (Dispara)  ← ¡Aquí está la frontera!
x=3  → 1 (Dispara)
x=4  → 1 (Dispara)

Análisis Inmediato

¡El umbral está entre 1 y 2!
text

    No dispara     |     Dispara
                   |
---|-----|-----|--●--|-----|-----|----→ x
  0     1     1.5  2.0  3     4
                   ↑
              Umbral ≈ 1.5

🎯 Objetivo: ASCII 'p' = 01110000

Necesitamos generar 8 salidas:
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
Paso 1: Encontrar el Umbral Exacto

Para generar la secuencia, necesitamos números que caigan en zonas específicas. De las primeras pruebas:
x	Salida	Análisis
1	0	x < umbral
2	1	x ≥ umbral
3	1	x ≥ umbral
4	1	x ≥ umbral

Conclusión: El umbral está en el intervalo (1, 2]
Paso 2: Refinar el Umbral

Para generar el patrón, necesitamos números justo alrededor del umbral:
text

[8/128] x=0   → 0  ✓ (Bit 1: 0)
[9/128] x=0.5 → 0  ✓ (Bit 5: 0, pero aún no importa)
[10/128] x=1.2 → 0 ✓ (Bit 6: 0)
[11/128] x=1.9 → 0 ✓ (Bit 7: 0)

Espera... ¡1.9 debería disparar si el umbral es 1.5! Pero dio 0.
Paso 3: ¡Ajuste de Hipótesis!

Si x=1.9 da 0, entonces el umbral es mayor que 1.9, pero x=2 dispara.
text

    No dispara     |     Dispara
                   |
---|-----|-----|--●--|-----|-----|----→ x
  0     1    1.9  2.0  3     4
                   ↑
              Umbral ≈ 1.95

Paso 4: Generar la Secuencia Correcta

Ahora podemos generar exactamente el patrón:
text

[4/128]  x=1    → 0  ← Bit 1: 0 ✓
[5/128]  x=2    → 1  ← Bit 2: 1 ✓
[6/128]  x=3    → 1  ← Bit 3: 1 ✓
[7/128]  x=4    → 1  ← Bit 4: 1 ✓
[8/128]  x=0    → 0  ← Bit 5: 0 ✓
[9/128]  x=0.5  → 0  ← Bit 6: 0 ✓
[10/128] x=1.2  → 0  ← Bit 7: 0 ✓
[11/128] x=1.9  → 0  ← Bit 8: 0 ✓

🔬 ¿Por qué funcionó exactamente?
Visualización de la Secuencia
text

Salida
  ↑
1 |     ●(2) ●(3) ●(4)
  |     
  |     Región de Disparo (1)
  |     
0 | ●(1) ●(0) ●(0.5) ●(1.2) ●(1.9)
  |________________________________→ x
  0    1    2    3    4
       ↑    ↑
       |    |
   Umbral ≈ 1.95

Mapeo de la Secuencia en la Recta Numérica
text

Valores elegidos:    0    0.5  1.0  1.2  1.9  2.0  3.0  4.0
                     |    |    |    |    |    |    |    |
Salidas:             0    0    0    0    0    1    1    1
                     |         |              |
                     └─────────┘              └──────┘
                     Todos 0          Todos 1
                          
                     Umbral ≈ 1.95

📐 Determinando los Pesos Reales

Aunque no es necesario para resolverlo, podemos deducir los parámetros:

Si asumimos que el umbral está en 1.95:
text

w·x + b = 0 cuando x = 1.95

Por ejemplo, si w = 1, entonces:
text

1·1.95 + b = 0
b = -1.95

Verificación:
text

x=1:  1·1 + (-1.95) = -0.95 < 0 → 0 ✓
x=2:  1·2 + (-1.95) = 0.05 ≥ 0 → 1 ✓
x=1.9: 1·1.9 + (-1.95) = -0.05 < 0 → 0 ✓

¡Perfecto!
🏆 La Solución Final

La secuencia que generó el patrón fue:
text

[4/128]  x=1    → 0
[5/128]  x=2    → 1
[6/128]  x=3    → 1
[7/128]  x=4    → 1
[8/128]  x=0    → 0
[9/128]  x=0.5  → 0
[10/128] x=1.2  → 0
[11/128] x=1.9  → 0

Patrón: 0 1 1 1 0 0 0 0 = 01110000 = 'p' en ASCII

🎁 La Recompensa
text

academy{*************************}

📊 Diagrama Final
Visualización del Perceptrón 1D
text

                    Salida
                      ↑
                  1   |     ●   ●   ●
                      |     2   3   4
                      |   Región de
                      |   Disparo (1)
                      |
                  0   | ●   ●   ●   ●   ●
                      | 0   0.5 1.0 1.2 1.9
                      |   Región de
                      |   Silencio (0)
                      |
                      └────────────────────────→ x
                       0   1   2   3   4   5
                           ↑
                     Umbral ≈ 1.95

Comparativa: 1D vs 2D
Aspecto	Neuron Meet 0 (1D)	Neuron Meet 2D-0 (2D)
Entrada	Un número (x)	Dos números (x, y)
Frontera	Un punto en la recta	Una línea en el plano
Visualización	Recta numérica	Plano cartesiano
Complejidad	Baja	Media
Umbral	~1.95	w₁·x + w₂·y + b = 0
💡 Conceptos Clave Aprendidos

    Perceptrón 1D: Clasificador más simple posible

    Umbral de Decisión: Punto que separa las dos clases

    Ingeniería de Precisión: Usar números decimales para ajustar finamente

    Binario a ASCII: 01110000 = 'p'

    Caja Negra: Deducción de parámetros sin acceso interno

🔑 Reflexión Final

Este desafío es una excelente introducción a los conceptos de redes neuronales:

    Un perceptrón es solo un clasificador lineal que separa datos en dos grupos

    En 1D, la decisión se reduce a un solo umbral

    Podemos "engañar" al perceptrón para generar secuencias específicas

    La precisión decimal es clave para ajustar el comportamiento

A diferencia del desafío 2D, aquí la solución es mucho más directa: solo necesitas encontrar el umbral y luego elegir números que estén estratégicamente ubicados a ambos lados para generar el patrón binario deseado.
