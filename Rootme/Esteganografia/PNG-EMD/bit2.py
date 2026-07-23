def probar_bit2_especifico():
    from PIL import Image
    import re
    
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== BIT 2 ESPECÍFICO (como detectó zsteg) ===")
    
    # Extraer bit 2
    bits = [(p >> 2) & 1 for p in pixels]
    
    # Probar diferentes formas de agrupar
    for offset in range(8):
        print(f"\nOffset: {offset}")
        chars = []
        for i in range(offset, min(len(bits), 892 * 8 + offset), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    if i + j < len(bits):
                        byte = (byte << 1) | bits[i + j]
                if 32 <= byte <= 126:
                    chars.append(chr(byte))
                else:
                    chars.append('�')
        
        texto = ''.join(chars)
        validos = sum(1 for c in texto if c != '�')
        print(f"Válidos: {validos}/{len(texto)}")
        
        if validos > 100:
            print(f"Primeros 200:")
            print(texto[:200])
            
            # Probar ROT47
            def rot47(t):
                return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
            
            rot = rot47(texto)
            print(f"ROT47:")
            print(rot[:200])
            
            # Buscar palabras
            palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
            encontradas = [p for p in palabras if p in rot.lower()]
            if encontradas:
                print(f"✅ Palabras encontradas: {', '.join(encontradas)}")

# Ejecutar
probar_bit2_especifico()
