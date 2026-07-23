from PIL import Image
import re

def extraer_emd_correcto():
    img = Image.open('ch26.png').convert('L')
    pixels = list(img.getdata())
    
    print(f"Total píxeles: {len(pixels)}")
    print(f"Primeros 20 píxeles: {pixels[:20]}")
    
    # EMD: Usar grupos de 2 píxeles
    # El mensaje está en la diferencia (p2 - p1) mod 256
    # Pero necesitamos tomar los primeros 892 caracteres
    
    mensaje_bytes = bytearray()
    
    for i in range(0, min(len(pixels), 892 * 2), 2):
        if i + 1 < len(pixels):
            p1 = pixels[i]
            p2 = pixels[i + 1]
            
            # EMD: el valor oculto es la diferencia
            # Pero como los píxeles son 29-31, la diferencia es pequeña
            # Probamos con (p1 + p2) mod 256 también
            diff = (p2 - p1) % 256
            mensaje_bytes.append(diff)
    
    print(f"Bytes extraídos: {len(mensaje_bytes)}")
    print(f"Primeros 50 bytes (hex): {mensaje_bytes[:50].hex()}")
    print(f"Primeros 50 bytes (decimal): {list(mensaje_bytes[:50])}")
    
    # Guardar los bytes
    with open('emd_bytes.bin', 'wb') as f:
        f.write(mensaje_bytes)
    
    # Intentar diferentes codificaciones
    for encoding in ['latin-1', 'utf-8', 'cp1252']:
        try:
            texto = mensaje_bytes.decode(encoding, errors='ignore')
            print(f"\n=== {encoding} ===")
            print(texto[:300])
        except:
            pass
    
    # Probar XOR con diferentes claves
    print("\n=== PROBANDO XOR ===")
    for key in range(256):
        xor_data = bytes([b ^ key for b in mensaje_bytes])
        try:
            texto = xor_data.decode('latin-1', errors='ignore')
            # Buscar palabras comunes
            if 'the' in texto.lower() or 'and' in texto.lower() or 'le' in texto.lower():
                print(f"\n✅ XOR key {key} (0x{key:02x})")
                print(f"Primeros 200 caracteres:")
                print(texto[:200])
                
                # Guardar
                with open(f'emd_xor_{key:02x}.txt', 'w') as f:
                    f.write(texto)
                
                # Si encontramos muchas palabras, parar
                palabras = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
                encontradas = sum(1 for p in palabras if p in texto.lower())
                if encontradas > 3:
                    print(f"✅ {encontradas} palabras encontradas")
                    break
        except:
            pass
    
    return mensaje_bytes

# Ejecutar
extraer_emd_correcto()
