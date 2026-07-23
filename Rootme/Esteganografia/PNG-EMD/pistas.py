from PIL import Image

def extraer_mensaje_pistas():
    # Abrir imagen
    img = Image.open('ch26.png')
    pixels = list(img.getdata())
    
    print(f"Dimensiones: {img.size}")
    print(f"Total píxeles: {len(pixels)}")
    
    # Las pistas dicen:
    # - Grupos de 2 píxeles
    # - 892 caracteres
    # - Eje X (uno tras otro)
    # - Sin cifrado
    
    mensaje = []
    
    # Tomar exactamente 892 * 2 = 1784 píxeles
    total_pixeles_necesarios = 892 * 2
    
    for i in range(0, min(len(pixels), total_pixeles_necesarios), 2):
        if i + 1 < len(pixels):
            p1 = pixels[i]
            p2 = pixels[i + 1]
            
            # Para escala de grises
            if isinstance(p1, int):
                val1, val2 = p1, p2
            else:
                # Tomar canal rojo (o el que sea)
                val1, val2 = p1[0], p2[0]
            
            # Extraer el carácter de los 2 píxeles
            # Método: usar la diferencia (p2 - p1) como dice EMD
            diff = (val2 - val1) % 256
            
            # Solo guardar si es imprimible
            if 32 <= diff <= 126:
                mensaje.append(chr(diff))
            else:
                # Si no es imprimible, guardar como marcador
                mensaje.append('�')
    
    texto = ''.join(mensaje)
    
    print(f"\nMensaje extraído: {len(texto)} caracteres")
    print("\n=== PRIMEROS 500 CARACTERES ===")
    print(texto[:500])
    
    # Guardar
    with open('mensaje_pistas.txt', 'w', encoding='utf-8') as f:
        f.write(texto)
    print("\n✅ Guardado como 'mensaje_pistas.txt'")
    
    # Buscar flag
    import re
    flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
    if flags:
        print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
        return flags[0]
    
    # Si no, probar ROT47
    print("\n🔍 Probando ROT47...")
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    rot47_texto = rot47(texto)
    print(rot47_texto[:500])
    
    flags = re.findall(r'rootme\{[^}]+\}', rot47_texto, re.IGNORECASE)
    if flags:
        print(f"\n🚩 ¡FLAG ENCONTRADA en ROT47!: {flags[0]}")
        return flags[0]
    
    return texto

# Ejecutar
extraer_mensaje_pistas()
