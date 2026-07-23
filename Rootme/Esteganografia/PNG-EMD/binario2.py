from PIL import Image
import re
import zlib

def extraer_bit2_emd():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print("=== BIT 2 EMD ===")
    print(f"Total píxeles: {len(pixels)}")
    
    # Extraer el bit 2 de cada píxel y agrupar de a 8
    bytes_data = bytearray()
    bits = []
    
    for p in pixels:
        bits.append((p >> 2) & 1)
    
    print(f"Bits extraídos: {len(bits)}")
    
    for i in range(0, min(len(bits), 892 * 8), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            bytes_data.append(byte)
    
    print(f"Bytes extraídos: {len(bytes_data)}")
    print(f"Primeros 50 bytes (hex): {bytes_data[:50].hex()}")
    print(f"Primeros 50 bytes (decimal): {list(bytes_data[:50])}")
    
    # Guardar
    with open('bit2_emd.bin', 'wb') as f:
        f.write(bytes_data)
    print("✅ Guardado como 'bit2_emd.bin'")
    
    # Intentar leer como texto con diferentes codificaciones
    codificaciones = ['latin-1', 'utf-8', 'cp1252', 'iso-8859-15']
    
    for encoding in codificaciones:
        try:
            texto = bytes_data.decode(encoding, errors='ignore')
            print(f"\n=== {encoding} ===")
            print(f"Primeros 500 caracteres:")
            print(texto[:500])
            
            # Buscar flag
            flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA en {encoding}!: {flags[0]}")
                return flags[0]
        except:
            pass
    
    # Intentar XOR con valores comunes
    print("\n=== PROBANDO XOR ===")
    for key in range(256):
        xor_data = bytes([b ^ key for b in bytes_data[:100]])
        try:
            texto = xor_data.decode('latin-1', errors='ignore')
            # Buscar palabras comunes
            if any(word in texto.lower() for word in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']):
                print(f"✅ XOR key {key} (0x{key:02x}) parece funcionar!")
                # Aplicar a todo
                xor_full = bytes([b ^ key for b in bytes_data])
                texto_full = xor_full.decode('latin-1', errors='ignore')
                print(f"\nPrimeros 500 caracteres con XOR {key}:")
                print(texto_full[:500])
                
                # Buscar flag
                flags = re.findall(r'rootme\{[^}]+\}', texto_full, re.IGNORECASE)
                if flags:
                    print(f"🚩 ¡FLAG ENCONTRADA! XOR {key}: {flags[0]}")
                    return flags[0]
                
                # Guardar
                with open(f'xor_{key:02x}.txt', 'w') as f:
                    f.write(texto_full)
                break
        except:
            pass
    
    # Intentar ROT47
    print("\n=== PROBANDO ROT47 ===")
    def rot47(t):
        return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)
    
    texto = bytes_data.decode('latin-1', errors='ignore')
    rot = rot47(texto)
    print(f"Primeros 500 caracteres ROT47:")
    print(rot[:500])
    
    flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
    if flags:
        print(f"🚩 ¡FLAG ENCONTRADA en ROT47!: {flags[0]}")
        return flags[0]
    
    return None

# Ejecutar
extraer_bit2_emd()
