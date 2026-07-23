from PIL import Image
import re

def extraer_mensaje_emd_binario():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print(f"Total píxeles: {len(pixels)}")
    
    # Extraer usando EMD (diferencia de píxeles)
    bytes_data = bytearray()
    
    for i in range(0, min(len(pixels), 892 * 2), 2):
        if i + 1 < len(pixels):
            p1 = pixels[i]
            p2 = pixels[i + 1]
            
            # Diferencia
            diff = (p2 - p1) % 256
            bytes_data.append(diff)
    
    print(f"Bytes extraídos: {len(bytes_data)}")
    print(f"Primeros 50 bytes (hex): {bytes_data[:50].hex()}")
    print(f"Primeros 50 bytes (decimal): {list(bytes_data[:50])}")
    
    # Guardar los bytes crudos
    with open('mensaje_emd.bin', 'wb') as f:
        f.write(bytes_data)
    print("✅ Guardado como 'mensaje_emd.bin'")
    
    # Intentar diferentes codificaciones
    codificaciones = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-15']
    
    for encoding in codificaciones:
        try:
            texto = bytes_data.decode(encoding, errors='ignore')
            print(f"\n=== {encoding} ===")
            print(texto[:500])
            
            # Buscar flag
            flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA en {encoding}!: {flags[0]}")
                return flags[0]
        except:
            pass
    
    # Si no es texto, intentar descomprimir con zlib
    print("\n=== INTENTANDO ZLIB ===")
    import zlib
    try:
        decomp = zlib.decompress(bytes_data)
        print(f"✅ Descomprimido: {len(decomp)} bytes")
        try:
            texto = decomp.decode('latin-1')
            print(texto[:500])
            flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
            if flags:
                print(f"🚩 ¡FLAG ENCONTRADA en zlib!: {flags[0]}")
                return flags[0]
        except:
            pass
    except zlib.error as e:
        print(f"❌ No es zlib: {e}")
    
    # Si no, probar XOR con valores comunes
    print("\n=== PROBANDO XOR ===")
    for key in range(256):
        xor_data = bytes([b ^ key for b in bytes_data[:100]])
        # Ver si el texto es legible
        try:
            texto = xor_data.decode('latin-1')
            if any(word in texto.lower() for word in ['the', 'and', 'for', 'are', 'but', 'not', 'you']):
                print(f"✅ XOR key {key} (0x{key:02x}) funciona!")
                # Aplicar a todo
                xor_full = bytes([b ^ key for b in bytes_data])
                texto_full = xor_full.decode('latin-1', errors='ignore')
                print(texto_full[:500])
                
                flags = re.findall(r'rootme\{[^}]+\}', texto_full, re.IGNORECASE)
                if flags:
                    print(f"🚩 ¡FLAG ENCONTRADA! XOR {key}: {flags[0]}")
                    return flags[0]
                break
        except:
            pass
    
    return None

# Ejecutar
extraer_mensaje_emd_binario()
