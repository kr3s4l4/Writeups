from PIL import Image
import re

def extraer_dos_bits():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== EXTRAYENDO BITS 0 Y 1 COMBINADOS ===")
    print(f"Total píxeles: {len(pixels)}")
    print(f"Primeros 10 píxeles: {pixels[:10]}")
    
    # Extraer 2 bits por píxel (bits 0 y 1)
    bits = []
    for p in pixels:
        # Extraer bit 0 y bit 1
        b0 = p & 1
        b1 = (p >> 1) & 1
        bits.append(b0)
        bits.append(b1)
    
    print(f"Total bits: {len(bits)}")
    print(f"Primeros 20 bits: {bits[:20]}")
    
    # Probar diferentes formas de agrupar
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    # Método 1: Agrupar de a 8 bits (4 píxeles por carácter)
    print("\n=== MÉTODO 1: 8 bits por carácter ===")
    chars = []
    for i in range(0, min(len(bits), 892 * 8), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            if 32 <= byte <= 126:
                chars.append(chr(byte))
            else:
                chars.append('�')
    
    texto = ''.join(chars)
    validos = sum(1 for c in texto if c != '�')
    print(f"Válidos: {validos}/{len(texto)}")
    
    if validos > 100:
        print("\nOriginal (primeros 300):")
        print(texto[:300])
        
        rot = rot47(texto)
        print("\nROT47 (primeros 300):")
        print(rot[:300])
        
        # Buscar palabras
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
        encontradas = [p for p in palabras if p in rot.lower()]
        if encontradas:
            print(f"\n✅ Palabras en inglés encontradas: {', '.join(encontradas[:10])}")
            with open('mensaje_2bits_metodo1.txt', 'w') as f:
                f.write(rot)
            return rot
    
    # Método 2: Agrupar de a 8 bits pero con orden invertido
    print("\n=== MÉTODO 2: 8 bits por carácter (orden invertido) ===")
    chars = []
    for i in range(0, min(len(bits), 892 * 8), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j in range(7, -1, -1):
                byte = (byte << 1) | bits[i + j]
            if 32 <= byte <= 126:
                chars.append(chr(byte))
            else:
                chars.append('�')
    
    texto = ''.join(chars)
    validos = sum(1 for c in texto if c != '�')
    print(f"Válidos: {validos}/{len(texto)}")
    
    if validos > 100:
        print("\nOriginal (primeros 300):")
        print(texto[:300])
        
        rot = rot47(texto)
        print("\nROT47 (primeros 300):")
        print(rot[:300])
        
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
        encontradas = [p for p in palabras if p in rot.lower()]
        if encontradas:
            print(f"\n✅ Palabras en inglés encontradas: {', '.join(encontradas[:10])}")
            with open('mensaje_2bits_metodo2.txt', 'w') as f:
                f.write(rot)
            return rot
    
    # Método 3: Usar los 2 bits como valor (0-3) y agrupar 4 de ellos para formar un byte
    print("\n=== MÉTODO 3: 2 bits por píxel, 4 píxeles por carácter ===")
    chars = []
    for i in range(0, min(len(pixels), 892 * 4), 4):
        if i + 4 <= len(pixels):
            valor = 0
            for j in range(4):
                # Tomar los 2 bits de cada píxel
                p = pixels[i + j]
                b0 = p & 1
                b1 = (p >> 1) & 1
                valor = (valor << 2) | (b1 << 1) | b0
            if 32 <= valor <= 126:
                chars.append(chr(valor))
            else:
                chars.append('�')
    
    texto = ''.join(chars)
    validos = sum(1 for c in texto if c != '�')
    print(f"Válidos: {validos}/{len(texto)}")
    
    if validos > 100:
        print("\nOriginal (primeros 300):")
        print(texto[:300])
        
        rot = rot47(texto)
        print("\nROT47 (primeros 300):")
        print(rot[:300])
        
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
        encontradas = [p for p in palabras if p in rot.lower()]
        if encontradas:
            print(f"\n✅ Palabras en inglés encontradas: {', '.join(encontradas[:10])}")
            with open('mensaje_2bits_metodo3.txt', 'w') as f:
                f.write(rot)
            return rot

# Ejecutar
extraer_dos_bits()
