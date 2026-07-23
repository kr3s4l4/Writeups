def probar_combinacion_bits():
    from PIL import Image
    import re
    
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== PROBANDO DIFERENTES COMBINACIONES DE BITS 0 Y 1 ===")
    
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    # Probar diferentes formas de combinar los 2 bits por píxel
    combinaciones = [
        ('bit0 primero', lambda p: [(p & 1), ((p >> 1) & 1)]),
        ('bit1 primero', lambda p: [((p >> 1) & 1), (p & 1)]),
        ('xor', lambda p: [(p & 1) ^ ((p >> 1) & 1)]),
        ('and', lambda p: [(p & 1) & ((p >> 1) & 1)]),
        ('or', lambda p: [(p & 1) | ((p >> 1) & 1)]),
    ]
    
    for nombre, func in combinaciones:
        print(f"\n{'='*60}")
        print(f"Combinación: {nombre}")
        print('='*60)
        
        # Extraer bits según la combinación
        bits = []
        for p in pixels:
            bits.extend(func(p))
        
        # Agrupar de a 8 bits
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
        print(f"Caracteres válidos: {validos}/{len(texto)}")
        
        if validos > 200:
            print("\nROT47 (primeros 300):")
            rot = rot47(texto)
            print(rot[:300])
            
            # Buscar palabras
            palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
            encontradas = [p for p in palabras if p in rot.lower()]
            if encontradas:
                print(f"✅ Palabras encontradas: {', '.join(encontradas)}")
                with open(f'mensaje_{nombre}.txt', 'w') as f:
                    f.write(rot)

# Ejecutar
probar_combinacion_bits()
