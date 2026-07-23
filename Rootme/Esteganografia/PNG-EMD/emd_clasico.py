from PIL import Image
import re

def extraer_emd_clasico():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== MÉTODO EMD CLÁSICO ===")
    print(f"Píxeles: {len(pixels)}")
    
    # EMD usa grupos de 2 píxeles
    chars = []
    for i in range(0, min(len(pixels), 892 * 2), 2):
        if i + 1 < len(pixels):
            p1 = pixels[i]
            p2 = pixels[i + 1]
            
            # Diferencia normalizada
            diff = (p2 - p1) % 256
            if 32 <= diff <= 126:
                chars.append(chr(diff))
            else:
                # Si no es imprimible, probar con XOR
                xor_val = p1 ^ p2
                if 32 <= xor_val <= 126:
                    chars.append(chr(xor_val))
                else:
                    chars.append('�')
    
    texto = ''.join(chars)
    validos = sum(1 for c in texto if c != '�')
    print(f"Válidos: {validos}/{len(texto)}")
    
    if validos > 100:
        print("Primeros 300:")
        print(texto[:300])
        
        # Probar ROT47
        def rot47(t):
            return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
        
        rot = rot47(texto)
        print("\nROT47:")
        print(rot[:300])
        
        flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
        if flags:
            print(f"🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
            return flags[0]

# Ejecutar
extraer_emd_clasico()
