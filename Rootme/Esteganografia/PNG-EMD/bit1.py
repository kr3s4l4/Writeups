from PIL import Image
import re

def probar_bit1():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== BIT 1 SOLO ===")
    print(f"Total píxeles: {len(pixels)}")
    
    # Extraer bit 1 de cada píxel
    bits = [(p >> 1) & 1 for p in pixels]
    
    print(f"Primeros 20 bits: {bits[:20]}")
    
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
    
    if validos > 100:
        print("\n=== TEXTO ORIGINAL (primeros 300) ===")
        print(texto[:300])
        
        def rot47(t):
            return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
        
        rot = rot47(texto)
        print("\n=== ROT47 (primeros 300) ===")
        print(rot[:300])
        
        # Buscar palabras en inglés
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
        encontradas = [p for p in palabras if p in rot.lower()]
        if encontradas:
            print(f"\n✅ Palabras en inglés encontradas: {', '.join(encontradas[:10])}")
        
        # Buscar palabras en francés
        palabras_fr = ['le', 'la', 'les', 'des', 'pour', 'avec', 'dans', 'par', 'sur', 'que', 'qui', 'est', 'sont', 'ont', 'fait', 'breizh', 'bretagne', 'bzh']
        encontradas_fr = [p for p in palabras_fr if p.lower() in rot.lower()]
        if encontradas_fr:
            print(f"✅ Palabras en francés encontradas: {', '.join(encontradas_fr[:10])}")
        
        # Buscar flag
        flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
        if flags:
            print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
            return flags[0]
        
        # Guardar
        with open('mensaje_bit1.txt', 'w') as f:
            f.write(rot)
        print("\n✅ Guardado como 'mensaje_bit1.txt'")
        
        return rot

# Ejecutar
probar_bit1()
