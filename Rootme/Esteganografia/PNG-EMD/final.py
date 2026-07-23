from PIL import Image
import re

def extraer_mensaje_grises():
    # Abrir imagen en blanco y negro
    img = Image.open('ch26.png')
    # Convertir a escala de grises si es necesario
    if img.mode != 'L':
        img = img.convert('L')
    
    pixels = list(img.getdata())
    
    print(f"Dimensiones: {img.size}")
    print(f"Modo: {img.mode}")
    print(f"Total píxeles: {len(pixels)}")
    
    # Las pistas dicen:
    # - Grupos de 2 píxeles en el eje X
    # - 892 caracteres
    # - Sin cifrado
    
    mensaje = []
    
    # Tomar exactamente 892 * 2 = 1784 píxeles
    total = 892 * 2
    
    for i in range(0, min(len(pixels), total), 2):
        if i + 1 < len(pixels):
            p1 = pixels[i]
            p2 = pixels[i + 1]
            
            # En escala de grises, p1 y p2 son valores 0-255
            
            # Probar diferentes métodos de extracción
            metodos = {
                'diferencia': (p2 - p1) % 256,
                'suma': (p1 + p2) % 256,
                'promedio': (p1 + p2) // 2,
                'xor': p1 ^ p2,
                'lsb_p1': p1 & 1,
                'lsb_p2': p2 & 1,
                'lsb_combinado': ((p1 & 1) << 1) | (p2 & 1),
                'bit1_p1': (p1 >> 1) & 1,
                'bit2_p1': (p1 >> 2) & 1,
                'diferencia_simple': p2 - p1,
            }
            
            # Guardar los valores para cada método
            for nombre, valor in metodos.items():
                if nombre not in locals():
                    locals()[nombre] = []
                if 32 <= valor <= 126:
                    locals()[nombre].append(chr(valor))
                else:
                    locals()[nombre].append('�')
    
    # Mostrar resultados de cada método
    for nombre in metodos.keys():
        texto = ''.join(locals()[nombre])
        imprimibles = sum(1 for c in texto if c != '�')
        print(f"\n=== {nombre} ===")
        print(f"Caracteres válidos: {imprimibles}/{len(texto)}")
        
        if imprimibles > 800:  # Si casi todos son imprimibles
            print(f"✅ ¡{nombre} parece funcionar!")
            print(f"\nPrimeros 300 caracteres:")
            print(texto[:300])
            
            # Guardar
            with open(f'mensaje_{nombre}.txt', 'w', encoding='utf-8') as f:
                f.write(texto)
            
            # Buscar flag
            flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
            if flags:
                print(f"\n🚩 ¡FLAG ENCONTRADA en {nombre}!: {flags[0]}")
                return flags[0]
            
            # Si no hay flag, probar ROT47
            print(f"\n🔍 Probando ROT47 en {nombre}...")
            def rot47(t):
                return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
            
            rot47_texto = rot47(texto)
            flags = re.findall(r'rootme\{[^}]+\}', rot47_texto, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA en ROT47!: {flags[0]}")
                return flags[0]
    
    return None

# Ejecutar
extraer_mensaje_grises()
