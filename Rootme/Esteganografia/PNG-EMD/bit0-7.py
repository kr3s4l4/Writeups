from PIL import Image
import re

def probar_todos_los_bits_con_ordenes():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== PROBANDO TODOS LOS BITS CON DIFERENTES ÓRDENES ===")
    
    # Definir órdenes de bits
    ordenes = [
        ('normal', list(range(8))),
        ('invertido', list(range(7, -1, -1))),
        ('par_impar', [0,2,4,6,1,3,5,7]),
        ('impar_par', [1,3,5,7,0,2,4,6]),
    ]
    
    # Para cada bit (0-7)
    for bit in range(8):
        print(f"\n{'='*60}")
        print(f"BIT {bit}")
        print('='*60)
        
        # Extraer el bit de cada píxel
        bits = [(p >> bit) & 1 for p in pixels]
        
        # Probar cada orden
        for nombre_orden, orden in ordenes:
            chars = []
            for i in range(0, min(len(bits), 892 * 8), 8):
                if i + 8 <= len(bits):
                    byte = 0
                    for j in range(8):
                        idx = i + orden[j]
                        if idx < len(bits):
                            byte = (byte << 1) | bits[idx]
                    if 32 <= byte <= 126:
                        chars.append(chr(byte))
                    else:
                        chars.append('�')
            
            texto = ''.join(chars)
            validos = sum(1 for c in texto if c != '�')
            
            if validos > 200:
                print(f"Orden {nombre_orden}: {validos}/{len(texto)} caracteres válidos")
                print(f"Primeros 100 caracteres:")
                print(texto[:100])
                
                # Probar ROT47
                def rot47(t):
                    return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
                
                rot = rot47(texto)
                print(f"ROT47 (primeros 100):")
                print(rot[:100])
                
                # Buscar palabras
                palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'breizh', 'bzh', 'bretagne']
                encontradas = [p for p in palabras if p in rot.lower()]
                if encontradas:
                    print(f"✅ Palabras encontradas: {', '.join(encontradas)}")
                    with open(f'mensaje_bit{bit}_{nombre_orden}.txt', 'w') as f:
                        f.write(rot)

# Ejecutar
probar_todos_los_bits_con_ordenes()
