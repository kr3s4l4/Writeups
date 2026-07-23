from PIL import Image
import re
import zlib
import base64
import binascii

def probar_todas_transformaciones():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    # Extraer 2 bits por píxel
    all_bits = []
    for p in pixels:
        all_bits.append(p & 1)
        all_bits.append((p >> 1) & 1)
    
    # Agrupar 4 píxeles (8 bits) por carácter
    bytes_data = bytearray()
    for i in range(0, min(len(all_bits), 892 * 8), 8):
        if i + 8 <= len(all_bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | all_bits[i + j]
            bytes_data.append(byte)
    
    print(f"Bytes extraídos: {len(bytes_data)}")
    print(f"Primeros 50 bytes (hex): {bytes_data[:50].hex()}")
    print(f"Primeros 50 bytes (decimal): {list(bytes_data[:50])}")
    
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    def rot13(t):
        return ''.join(chr(((ord(c) - 65 + 13) % 26) + 65) if 65 <= ord(c) <= 90 else
                      chr(((ord(c) - 97 + 13) % 26) + 97) if 97 <= ord(c) <= 122 else c for c in t)
    
    # Probar diferentes transformaciones
    transformaciones = [
        ('ROT47', rot47),
        ('ROT13', rot13),
        ('ROT47+ROT13', lambda t: rot13(rot47(t))),
        ('ROT13+ROT47', lambda t: rot47(rot13(t))),
    ]
    
    for nombre, func in transformaciones:
        print(f"\n{'='*60}")
        print(f"Transformación: {nombre}")
        print('='*60)
        
        texto = bytes_data.decode('latin-1', errors='ignore')
        transformado = func(texto)
        
        print(f"Primeros 300 caracteres:")
        print(transformado[:300])
        
        # Buscar palabras en inglés
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
        encontradas = [p for p in palabras if p in transformado.lower()]
        
        if encontradas:
            print(f"\n✅ Palabras en inglés encontradas: {', '.join(encontradas[:10])}")
        
        # Buscar palabras en francés
        palabras_fr = ['le', 'la', 'les', 'des', 'pour', 'avec', 'dans', 'par', 'sur', 'que', 'qui', 'est', 'sont', 'ont', 'fait', 'breizh', 'bretagne', 'bzh']
        encontradas_fr = [p for p in palabras_fr if p in transformado.lower()]
        if encontradas_fr:
            print(f"✅ Palabras en francés encontradas: {', '.join(encontradas_fr[:10])}")
        
        # Buscar flag
        flags = re.findall(r'rootme\{[^}]+\}', transformado, re.IGNORECASE)
        if flags:
            print(f"\n🚩 ¡FLAG ENCONTRADA en {nombre}!: {flags[0]}")
            return flags[0]
        
        # Guardar
        with open(f'mensaje_{nombre}.txt', 'w') as f:
            f.write(transformado)
    
    # Probar inversión de bits
    print("\n=== INVERSIÓN DE BITS ===")
    inverted = bytes([~b & 0xFF for b in bytes_data])
    texto = inverted.decode('latin-1', errors='ignore')
    print(texto[:300])
    
    # Probar ROT47 en la inversión
    rot = rot47(texto)
    print(f"\nROT47 de inversión:")
    print(rot[:300])
    
    # Probar XOR con valores comunes en el texto original
    print("\n=== XOR CON VALORES COMUNES (directo) ===")
    claves = [0x55, 0xAA, 0xFF, 0x00, 0x7F, 0x80, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40]
    
    for key in claves:
        xor_data = bytes([b ^ key for b in bytes_data])
        texto = xor_data.decode('latin-1', errors='ignore')
        rot = rot47(texto)
        
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
        encontradas = [p for p in palabras if p in rot.lower()]
        
        if encontradas:
            print(f"\n✅ XOR 0x{key:02x} + ROT47")
            print(f"Palabras: {', '.join(encontradas[:5])}")
            print(f"ROT47 (primeros 200):")
            print(rot[:200])
            
            flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA! XOR 0x{key:02x}: {flags[0]}")
                return flags[0]
    
    # Si nada funciona, mostrar el texto original en bruto
    print("\n=== TEXTO ORIGINAL (latin-1) ===")
    texto = bytes_data.decode('latin-1', errors='ignore')
    print(texto[:500])
    
    return None

# Ejecutar
probar_todas_transformaciones()
