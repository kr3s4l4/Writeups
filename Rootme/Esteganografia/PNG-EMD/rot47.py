from PIL import Image
import re

def extraer_mensaje_final():
    # Abrir imagen en blanco y negro
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print(f"Total píxeles: {len(pixels)}")
    print(f"Primeros 20 píxeles: {pixels[:20]}")
    print(f"Valores únicos: {sorted(set(pixels[:100]))}")
    
    # Extraer LSB de cada píxel
    bits = [p & 1 for p in pixels]
    
    print(f"\nPrimeros 50 bits: {bits[:50]}")
    
    # Agrupar de a 8 bits para formar caracteres
    chars = []
    for i in range(0, min(len(bits), 892 * 8), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            
            # Si es imprimible o espacio, guardar
            if 32 <= byte <= 126:
                chars.append(chr(byte))
            else:
                chars.append('�')
    
    texto = ''.join(chars)
    validos = sum(1 for c in texto if c != '�')
    
    print(f"\nCaracteres válidos: {validos}/{len(texto)}")
    print("\n=== MENSAJE ORIGINAL (primeros 500) ===")
    print(texto[:500])
    
    # Aplicar ROT47
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    texto_rot47 = rot47(texto)
    print("\n=== ROT47 (primeros 500) ===")
    print(texto_rot47[:500])
    
    # Buscar flag
    flags = re.findall(r'rootme\{[^}]+\}', texto_rot47, re.IGNORECASE)
    if flags:
        print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
        return flags[0]
    
    # Buscar palabras clave
    palabras = ['breizh', 'bzh', 'bretagne', 'flag', 'rootme', 'independance', 'liberte']
    for palabra in palabras:
        if palabra.lower() in texto_rot47.lower():
            print(f"\n✅ '{palabra}' encontrada en ROT47!")
            # Mostrar contexto
            pos = texto_rot47.lower().find(palabra.lower())
            print(f"Contexto: ...{texto_rot47[max(0,pos-50):pos+100]}...")
            return texto_rot47
    
    # Guardar resultados
    with open('mensaje_lsb.txt', 'w') as f:
        f.write(texto)
    with open('mensaje_lsb_rot47.txt', 'w') as f:
        f.write(texto_rot47)
    
    print("\n✅ Guardado en 'mensaje_lsb.txt' y 'mensaje_lsb_rot47.txt'")
    
    return texto_rot47

# Ejecutar
extraer_mensaje_final()
