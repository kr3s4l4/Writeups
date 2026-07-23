import zlib
import re
import binascii

def extraer_mensaje_zlib():
    # Intentar diferentes formas de leer el zlib
    with open('_ch26.png.extracted/1B9.zlib', 'rb') as f:
        data = f.read()
    
    print(f"Tamaño del archivo: {len(data)} bytes")
    print(f"Primeros 50 bytes (hex): {data[:50].hex()}")
    
    # El zlib tiene header 0x78 0x9C (zlib estándar)
    # Pero los datos pueden estar incompletos o corruptos
    
    # Intentar descomprimir con diferentes wbits
    for wbits in [15, -15, 31, 47]:
        try:
            decomp = zlib.decompress(data, wbits=wbits)
            print(f"\n✅ Descomprimido con wbits={wbits}: {len(decomp)} bytes")
            
            # Guardar el descomprimido
            with open(f'descomprimido_wbits{wbits}.bin', 'wb') as f:
                f.write(decomp)
            
            # Intentar leer como texto
            try:
                texto = decomp.decode('latin-1', errors='ignore')
                print(f"\nPrimeros 500 caracteres (latin-1):")
                print(texto[:500])
                
                # Buscar flag
                flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
                if flags:
                    print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
                    return flags[0]
                
                # Buscar el mensaje de 892 caracteres
                # El mensaje podría ser una cadena larga
                cadenas = re.findall(r'[A-Za-z0-9\s\.\,\;\:\!\?\-]{50,}', texto)
                for cadena in cadenas:
                    if 800 <= len(cadena) <= 920:
                        print(f"\n✅ Mensaje de {len(cadena)} caracteres encontrado!")
                        print(cadena)
                        with open('mensaje_892.txt', 'w', encoding='utf-8') as f:
                            f.write(cadena)
                        return cadena
                
            except:
                print("No es texto latin-1")
                
        except zlib.error as e:
            print(f"❌ wbits={wbits}: {e}")
    
    # Si no se descomprime, intentar con los chunks IDAT del PNG
    print("\n=== BUSCANDO EN LOS CHUNKS DEL PNG ===")
    
    with open('ch26.png', 'rb') as f:
        png_data = f.read()
    
    # Buscar chunks IDAT
    idat_chunks = []
    pos = 0
    while True:
        # Buscar IDAT
        idat_pos = png_data.find(b'IDAT', pos)
        if idat_pos == -1:
            break
        # Extraer el chunk
        length = int.from_bytes(png_data[idat_pos-4:idat_pos], 'big')
        chunk_data = png_data[idat_pos+4:idat_pos+4+length]
        idat_chunks.append(chunk_data)
        pos = idat_pos + 4 + length
    
    print(f"Encontrados {len(idat_chunks)} chunks IDAT")
    
    # Combinar todos los chunks IDAT
    all_idat = b''.join(idat_chunks)
    print(f"Tamaño total IDAT: {len(all_idat)} bytes")
    
    # Intentar descomprimir los datos IDAT (son zlib comprimidos)
    try:
        decomp = zlib.decompress(all_idat)
        print(f"✅ IDAT descomprimido: {len(decomp)} bytes")
        
        # Guardar
        with open('idat_decompressed.bin', 'wb') as f:
            f.write(decomp)
        
        # Buscar texto
        texto = decomp.decode('latin-1', errors='ignore')
        print("\nPrimeros 500 caracteres:")
        print(texto[:500])
        
        flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
        if flags:
            print(f"\n🚩 ¡FLAG ENCONTRADA en IDAT!: {flags[0]}")
            return flags[0]
            
    except zlib.error as e:
        print(f"❌ Error descomprimiendo IDAT: {e}")
    
    return None

# Ejecutar
extraer_mensaje_zlib()
