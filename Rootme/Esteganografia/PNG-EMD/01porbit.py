from PIL import Image
import re
import zlib

def extraer_2_bits_por_pixel():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print(f"Total píxeles: {len(pixels)}")
    print(f"Primeros 20 píxeles: {pixels[:20]}")
    
    # Extraer 2 bits por píxel (bit0 y bit1)
    all_bits = []
    for p in pixels:
        # Extraer bit0 y bit1
        b0 = p & 1
        b1 = (p >> 1) & 1
        all_bits.append(b0)
        all_bits.append(b1)
    
    print(f"Bits totales: {len(all_bits)}")
    print(f"Primeros 30 bits: {all_bits[:30]}")
    
    # Probar diferentes formas de agrupar los bits
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    resultados = []
    
    # Método 1: Agrupar 4 píxeles (8 bits) por carácter
    print("\n=== MÉTODO 1: 4 píxeles por carácter (8 bits) ===")
    bytes_data = bytearray()
    for i in range(0, min(len(all_bits), 892 * 8), 8):
        if i + 8 <= len(all_bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | all_bits[i + j]
            bytes_data.append(byte)
    
    print(f"Bytes: {len(bytes_data)}")
    print(f"Primeros 50 bytes (hex): {bytes_data[:50].hex()}")
    
    # Guardar
    with open('mensaje_2bits.bin', 'wb') as f:
        f.write(bytes_data)
    
    # Probar codificaciones
    for encoding in ['latin-1', 'utf-8', 'cp1252']:
        try:
            texto = bytes_data.decode(encoding, errors='ignore')
            print(f"\n=== {encoding} ===")
            print(texto[:300])
            
            # Buscar flag
            flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA en {encoding}!: {flags[0]}")
                return flags[0]
            
            # Buscar palabras
            palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
            encontradas = [p for p in palabras if p in texto.lower()]
            if encontradas:
                print(f"✅ Palabras encontradas: {', '.join(encontradas)}")
                resultados.append((encoding, texto, encontradas))
        except:
            pass
    
    # Probar ROT47
    print("\n=== ROT47 ===")
    texto = bytes_data.decode('latin-1', errors='ignore')
    rot = rot47(texto)
    print(rot[:300])
    
    flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
    if flags:
        print(f"🚩 ¡FLAG ENCONTRADA en ROT47!: {flags[0]}")
        return flags[0]
    
    # Buscar palabras en ROT47
    palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'breizh', 'bzh']
    encontradas = [p for p in palabras if p in rot.lower()]
    if encontradas:
        print(f"✅ Palabras en ROT47: {', '.join(encontradas)}")
        with open('mensaje_rot47.txt', 'w') as f:
            f.write(rot)
    
    # Método 2: Usar el valor de 2 bits (0-3) directamente
    print("\n=== MÉTODO 2: Valor de 2 bits (0-3) ===")
    valores = []
    for i in range(0, len(pixels), 1):
        if i < len(pixels):
            b0 = pixels[i] & 1
            b1 = (pixels[i] >> 1) & 1
            valor = (b1 << 1) | b0
            valores.append(valor)
    
    # Agrupar 4 valores (8 bits) por carácter
    bytes_data2 = bytearray()
    for i in range(0, min(len(valores), 892 * 4), 4):
        if i + 4 <= len(valores):
            byte = 0
            for j in range(4):
                byte = (byte << 2) | valores[i + j]
            bytes_data2.append(byte)
    
    print(f"Bytes: {len(bytes_data2)}")
    texto = bytes_data2.decode('latin-1', errors='ignore')
    print(texto[:300])
    
    rot = rot47(texto)
    print(f"\nROT47:")
    print(rot[:300])
    
    flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
    if flags:
        print(f"🚩 ¡FLAG ENCONTRADA en método 2!: {flags[0]}")
        return flags[0]
    
    return None

# Ejecutar
extraer_2_bits_por_pixel()
