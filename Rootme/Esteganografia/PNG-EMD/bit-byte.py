from PIL import Image
import re

def probar_ordenes_bits():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== PROBANDO DIFERENTES ÓRDENES DE BITS ===")
    
    # Probar diferentes órdenes de bits dentro de cada byte
    ordenes = [
        ('normal', [0,1,2,3,4,5,6,7]),
        ('invertido', [7,6,5,4,3,2,1,0]),
        ('par-impar', [0,2,4,6,1,3,5,7]),
        ('impar-par', [1,3,5,7,0,2,4,6]),
        ('mitad', [0,1,2,3,7,6,5,4]),
        ('mitad_inv', [4,5,6,7,0,1,2,3]),
    ]
    
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    # Extraer bit 0 y bit 1 combinados (2 bits por píxel)
    bits_2 = []
    for p in pixels:
        bits_2.append(p & 1)
        bits_2.append((p >> 1) & 1)
    
    # Probar cada orden
    for nombre, orden in ordenes:
        print(f"\n{'='*60}")
        print(f"Orden: {nombre}")
        print('='*60)
        
        chars = []
        for i in range(0, min(len(bits_2), 892 * 8), 8):
            if i + 8 <= len(bits_2):
                byte = 0
                for j in range(8):
                    bit_index = orden[j]
                    if i + bit_index < len(bits_2):
                        byte = (byte << 1) | bits_2[i + bit_index]
                if 32 <= byte <= 126:
                    chars.append(chr(byte))
                else:
                    chars.append('�')
        
        texto = ''.join(chars)
        validos = sum(1 for c in texto if c != '�')
        print(f"Caracteres válidos: {validos}/{len(texto)}")
        
        if validos > 200:
            print("\nOriginal (primeros 200):")
            print(texto[:200])
            
            rot = rot47(texto)
            print("\nROT47 (primeros 200):")
            print(rot[:200])
            
            # Buscar palabras
            palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'breizh', 'bzh', 'bretagne']
            encontradas = [p for p in palabras if p in rot.lower()]
            if encontradas:
                print(f"\n✅ Palabras encontradas: {', '.join(encontradas)}")
                with open(f'mensaje_orden_{nombre}.txt', 'w') as f:
                    f.write(rot)

# Ejecutar
probar_ordenes_bits()
