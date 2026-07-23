from PIL import Image
import re

def extraer_y_descifrar_xor():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    # Extraer 2 bits por píxel (bit0 y bit1)
    all_bits = []
    for p in pixels:
        all_bits.append(p & 1)
        all_bits.append((p >> 1) & 1)
    
    # Agrupar 4 píxeles (8 bits) por carácter
    bytes_data = bytearray()
    for i in range(0, min(len(all_bits), 892 * 8), 8):
        if i + 8 <= len(all_bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | all_bits[i + j]
            bytes_data.append(byte)
    
    print(f"Bytes extraídos: {len(bytes_data)}")
    print(f"Primeros 50 bytes (hex): {bytes_data[:50].hex()}")
    
    # Guardar
    with open('mensaje_cifrado.bin', 'wb') as f:
        f.write(bytes_data)
    
    # Probar XOR con todas las claves (0-255)
    print("\n=== BUSCANDO CLAVE XOR ===")
    
    for key in range(256):
        # Aplicar XOR
        xor_data = bytes([b ^ key for b in bytes_data])
        
        # Intentar decodificar como latin-1
        try:
            texto = xor_data.decode('latin-1', errors='ignore')
            
            # Buscar palabras en inglés
            palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has', 'his', 'its', 'may', 'she', 'who', 'use', 'any', 'see', 'new', 'day', 'get', 'way', 'man', 'say']
            encontradas = [p for p in palabras if p in texto.lower()]
            
            if len(encontradas) > 5:
                print(f"\n✅ XOR key {key} (0x{key:02x})")
                print(f"Palabras encontradas: {', '.join(encontradas[:10])}")
                print(f"Texto (primeros 300):")
                print(texto[:300])
                
                # Buscar flag
                flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
                if flags:
                    print(f"\n🚩 ¡FLAG ENCONTRADA! XOR {key}: {flags[0]}")
                    return flags[0]
                
                # Guardar
                with open(f'xor_{key:02x}.txt', 'w') as f:
                    f.write(texto)
                
                # Si encontramos muchas palabras, probablemente es la clave correcta
                if len(encontradas) > 10:
                    return texto
                    
        except:
            pass
    
    # Si no encuentra XOR, probar ROT47 sobre el XOR
    print("\n=== PROBANDO XOR + ROT47 ===")
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    for key in range(256):
        xor_data = bytes([b ^ key for b in bytes_data])
        texto = xor_data.decode('latin-1', errors='ignore')
        rot = rot47(texto)
        
        palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
        encontradas = [p for p in palabras if p in rot.lower()]
        
        if len(encontradas) > 5:
            print(f"\n✅ XOR {key} + ROT47 funciona!")
            print(f"Palabras: {', '.join(encontradas[:10])}")
            print(f"ROT47 (primeros 300):")
            print(rot[:300])
            
            flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA! XOR {key} + ROT47: {flags[0]}")
                return flags[0]
    
    return None

# Ejecutar
extraer_y_descifrar_xor()
