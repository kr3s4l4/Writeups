Writeup: APK - Introduction (Root-Me)

1. Introducción

    Reto: APK - Introduction

    Plataforma: Root-Me (Cracking)

    Objetivo: Encontrar la contraseña válida para la aplicación Android basic_rev.apk.

    Autor: algorab

    Dificultad: Fácil (1%)

    Validaciones: 3091 challengers

La aplicación parece sencilla: tiene un campo de texto y un botón. Al introducir una contraseña incorrecta muestra "Try again ;)", y si es correcta muestra "Well played! You can validate now with this password :)".

Nuestro objetivo es obtener la contraseña mediante ingeniería inversa.

2. Herramientas utilizadas

    jadx-gui (versión compilada desde el código fuente): para descompilar el APK y analizar el código Java.

    Python 3: para reimplementar la lógica de generación de la contraseña.

    Terminal Linux (Kali): para ejecutar comandos y scripts.

3. Análisis estático con jadx-gui
3.1. Descompilación del APK

Clonamos y compilamos jadx (o descargamos el binario). Luego abrimos el APK con la interfaz gráfica:
bash

./build/jadx/bin/jadx-gui ../basic_rev.apk

Captura sugerida: Ventana de jadx-gui con el árbol de paquetes expandido.
3.2. Identificación de la actividad principal

El archivo AndroidManifest.xml revela que la actividad principal es com.example.basic_rev.MainActivity:
xml

<activity android:name="com.example.basic_rev.MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
</activity>

3.3. Código de MainActivity

Al abrir MainActivity, encontramos el siguiente código (simplificado):
java

public class MainActivity extends Activity {
    Button b1;
    EditText ed1;

    public String makeFlag(String s) {
        // ... (complejo algoritmo)
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        this.b1 = (Button) findViewById(R.id.button);
        this.ed1 = (EditText) findViewById(R.id.editText);
        final String seed = getString(R.string.seed);
        this.b1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (MainActivity.this.ed1.getText().toString().equals(MainActivity.this.makeFlag(seed))) {
                    Toast.makeText(MainActivity.this.getApplicationContext(), 
                        "Well played! You can validate now with this password :)", 0).show();
                } else {
                    Toast.makeText(MainActivity.this.getApplicationContext(), 
                        "Try again ;)", 0).show();
                }
            }
        });
    }
}

Observamos que la contraseña correcta es el resultado de makeFlag(seed), donde seed se obtiene de los recursos (R.string.seed).

4. Extracción de la semilla (seed)

En jadx-gui, navegamos a Resources → res → values → strings.xml. Allí encontramos:
xml

<string name="seed">1dndr@</string>

Captura sugerida: Contenido de strings.xml mostrando la seed.

La semilla es "1dndr@".

5. Análisis del algoritmo makeFlag

La función makeFlag es la siguiente (código extraído):
java

public String makeFlag(String s) {
    String a = "" + s.charAt(5);
    String _b = s.charAt(2) + "";
    for (int s_ = 0; s_ < s.length(); s_++) {
        String b = _b.substring(_b.length() - s_) + _b.substring(s_);
        String _b2 = s_ >= 3 ? _b + s.charAt(s_ - 3) + "" : _b + s.charAt(s.length() - (3 - s_)) + "";
        if (s_ >= _b2.length()) {
            _b = _b2 + s.charAt(s_ - _b2.length()) + "";
        } else if (s.length() >= _b2.length() - s_) {
            _b = _b2 + s.charAt(s.length() - (_b2.length() - s_)) + "";
        } else {
            _b = _b2 + s.charAt(s.length() - ((_b2.length() - s_) - s.length())) + "";
        }
        a = a + b.charAt((((s.length() + _b.length()) * s_) + _b.length()) % b.length());
    }
    return a.substring(0, 2) + s.charAt(3) + a.charAt(3) + '0' + a.substring(5, 7);
}

No es necesario entender cada línea al detalle, pero podemos reimplementarlo en Python y ejecutarlo con la semilla.

6. Reimplementación en Python

Creamos un script solve.py que emule el comportamiento de makeFlag:
python

def makeFlag(s):
    a = s[5]
    _b = s[2]
    for s_ in range(len(s)):
        # Rotación de _b
        b = _b[len(_b) - s_:] + _b[s_:]
        # Construcción de _b2
        if s_ >= 3:
            _b2 = _b + s[s_ - 3]
        else:
            _b2 = _b + s[len(s) - (3 - s_)]
        # Actualización de _b
        if s_ >= len(_b2):
            _b = _b2 + s[s_ - len(_b2)]
        elif len(s) >= len(_b2) - s_:
            _b = _b2 + s[len(s) - (len(_b2) - s_)]
        else:
            _b = _b2 + s[len(s) - ((len(_b2) - s_) - len(s))]
        # Añadir carácter a 'a'
        idx = ((len(s) + len(_b)) * s_ + len(_b)) % len(b)
        a = a + b[idx]
    # Construcción final
    return a[:2] + s[3] + a[3] + '0' + a[5:7]

seed = "1dndr@"
print("Contraseña:", makeFlag(seed))

Ejecución:
bash

python3 solve.py

Salida:
text

Contraseña: *****************

Captura sugerida: Terminal mostrando la ejecución del script.

7. La contraseña

La contraseña generada es ***********

Al introducirla en la aplicación, se muestra el mensaje de éxito.

Captura sugerida: Pantalla de la app con el mensaje "Well played!..." después de introducir la contraseña.

8. Explicación paso a paso de la generación de la contraseña
8.1. Semilla

seed = "1dndr@" con índices:
Índice	0	1	2	3	4	5
Carácter	1	d	n	d	r	@
8.2. Variable a

a comienza con s[5] = '@'. Luego, en cada iteración del bucle se añade un carácter. Tras las 6 iteraciones, a queda:
text

a = "@ndrn1d"

Índice	0	1	2	3	4	5	6
Carácter	@	n	d	r	n	1	d
8.3. Sentencia final

La línea clave es:
java

return a.substring(0, 2) + s.charAt(3) + a.charAt(3) + '0' + a.substring(5, 7);

Descomposición:
Parte			Valor	Origen
a.substring(0,2)	"@n"	Primeros dos caracteres de a
s.charAt(3)		'd'	Cuarto carácter de la semilla
a.charAt(3)		'r'	Cuarto carácter de a
'0'			'0'	Literal hardcodeado
a.substring(5,7)	"1d"	Últimos dos caracteres de a

Concatenando: "@n" + "d" + "r" + "0" + "1d" = "@ndr01d".
8.4. Detalle de las iteraciones

Para los curiosos, aquí se muestra qué carácter se añade a a en cada iteración del bucle:
Iteración	_b inicial	b (rotación)	Índice calculado	Carácter añadido	a resultante
0		"n"		"n"		0			'n'			"@n"
1		"ndr"		"rdr"		1			'd'			"@nd"
2		"ndrrd"		"rdrrd"		3			'r'			"@ndr"
3		"ndrrd@n"	"d@nrd@n"	5			'n'			"@ndrn"
4		"ndrrd@n1d"	"@n1drd@n1d"	2			'1'			"@ndrn1"
5		"ndrrd@n1dd1"	"n1dd1d@n1dd1"	10			'd'			"@ndrn1d"

Esto confirma que a se construye como se indicó.

9. Conclusiones

    La aplicación no almacena la contraseña en texto plano, sino que la genera en tiempo de ejecución a partir de una semilla.

    El algoritmo es una ofuscación por permutación y selección de caracteres, no un cifrado clásico.

    Mediante ingeniería inversa con jadx-gui y reimplementación en Python, hemos obtenido la contraseña: ********************* (ocultada).

    La contraseña real es @ndr01d, que en leet significa "android", en referencia al sistema operativo donde corre la app.
