import subprocess
import re
import zlib
import base64

def decodificar_mensaje():
    # Leer los datos extraídos
    with open('pgp_data.bin', 'rb') as f:
        data = f.read()
    
    print(f"📊 Datos: {len(data)} bytes")
    print(f"Primeros 50 bytes (hex): {data[:50].hex()}")
    print(f"Primeros 50 bytes (ASCII): {data[:50]}")
    
    # 1. Probar XOR con valores comunes
    print("\n=== PROBANDO XOR ===")
    for key in range(256):
        try:
            xor_data = bytes([b ^ key for b in data[:1000]])
            xor_texto = xor_data.decode('latin-1', errors='ignore')
            
            # Buscar palabras clave
            if 'flag' in xor_texto.lower() or 'rootme' in xor_texto.lower():
                print(f"\n✅ XOR con {key} (0x{key:02x}) funciona!")
                # Aplicar a todo el archivo
                xor_full = bytes([b ^ key for b in data])
                texto = xor_full.decode('latin-1', errors='ignore')
                print(texto[:500])
                
                # Buscar flag
                flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
                if flags:
                    print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
                    return flags[0]
                    
        except:
            pass
    
    # 2. Probar ROT47
    print("\n=== PROBANDO ROT47 ===")
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    texto = data.decode('latin-1', errors='ignore')
    rot47_texto = rot47(texto)
    print(rot47_texto[:500])
    
    flags = re.findall(r'rootme\{[^}]+\}', rot47_texto, re.IGNORECASE)
    if flags:
        print(f"\n🚩 ¡FLAG ENCONTRADA en ROT47!: {flags[0]}")
        return flags[0]
    
    # 3. Probar inversión de bits
    print("\n=== PROBANDO INVERSIÓN DE BITS ===")
    inverted = bytes([~b & 0xFF for b in data])
    texto = inverted.decode('latin-1', errors='ignore')
    print(texto[:500])
    
    flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
    if flags:
        print(f"\n🚩 ¡FLAG ENCONTRADA en inversión de bits!: {flags[0]}")
        return flags[0]
    
    # 4. Probar Base64
    print("\n=== PROBANDO BASE64 ===")
    try:
        # Buscar cadenas base64
        b64_pattern = r'[A-Za-z0-9+/=]{20,}'
        texto = data.decode('latin-1', errors='ignore')
        matches = re.findall(b64_pattern, texto)
        
        for match in matches[:5]:
            try:
                # Añadir padding si es necesario
                padding = 4 - (len(match) % 4)
                if padding != 4:
                    match += '=' * padding
                decoded = base64.b64decode(match)
                print(f"Base64 decodificado: {decoded[:200]}")
                
                flags = re.findall(r'rootme\{[^}]+\}', decoded.decode('latin-1', errors='ignore'), re.IGNORECASE)
                if flags:
                    print(f"\n🚩 ¡FLAG ENCONTRADA en Base64!: {flags[0]}")
                    return flags[0]
            except:
                pass
    except:
        pass
    
    # 5. Probar zlib (descompresión)
    print("\n=== PROBANDO ZLIB ===")
    try:
        decomp = zlib.decompress(data)
        texto = decomp.decode('latin-1', errors='ignore')
        print(texto[:500])
        
        flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
        if flags:
            print(f"\n🚩 ¡FLAG ENCONTRADA en zlib!: {flags[0]}")
            return flags[0]
    except:
        print("No es zlib")
    
    print("\n❌ No se encontró la flag")
    return None

# Ejecutar
decodificar_mensaje()
