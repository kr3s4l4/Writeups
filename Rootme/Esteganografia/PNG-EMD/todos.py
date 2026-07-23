from PIL import Image
import re

def probar_todos_los_bits_sistematicamente():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print(f"Total píxeles: {len(pixels)}")
    print(f"Primeros 10 píxeles: {pixels[:10]}")
    print("Valores de píxeles son 29-31, lo que significa que los bits superiores son 0")
    
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    # Probar bits 0-7
    for bit in range(8):
        print(f"\n{'='*60}")
        print(f"BIT {bit} (valor: {1 << bit})")
        print('='*60)
        
        # Extraer el bit de cada píxel
        bits = [(p >> bit) & 1 for p in pixels]
        
        # Mostrar primeros 20 bits
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
            print(f"\nTexto original (primeros 200):")
            print(texto[:200])
            
            rot = rot47(texto)
            print(f"\nROT47 (primeros 200):")
            print(rot[:200])
            
            # Buscar palabras en francés/inglés
            palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
            encontradas = [p for p in palabras if p in rot.lower()]
            if encontradas:
                print(f"\n✅ Palabras en inglés encontradas: {', '.join(encontradas[:10])}")
            
            # Buscar palabras en francés
            palabras_fr = ['le', 'la', 'les', 'des', 'pour', 'avec', 'dans', 'par', 'sur', 'que', 'qui', 'est', 'sont', 'ont', 'fait', 'breizh', 'bretagne']
            encontradas_fr = [p for p in palabras_fr if p.lower() in rot.lower()]
            if encontradas_fr:
                print(f"✅ Palabras en francés encontradas: {', '.join(encontradas_fr[:10])}")
            
            # Si hay palabras, guardar
            if encontradas or encontradas_fr:
                with open(f'mensaje_bit{bit}.txt', 'w') as f:
                    f.write(rot)
                print(f"✅ Guardado como mensaje_bit{bit}.txt")

# Ejecutar
probar_todos_los_bits_sistematicamente()
