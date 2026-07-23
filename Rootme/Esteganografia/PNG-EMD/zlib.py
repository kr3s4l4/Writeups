import zlib
import re
from PIL import Image

def extraer_y_reconstruir_mensaje():
    # Leer el archivo zlib extraído con binwalk
    with open('_ch26.png.extracted/1B9.zlib', 'rb') as f:
        data = f.read()
    
    print(f"📊 Datos zlib: {len(data)} bytes")
    
    # Descomprimir
    try:
        decomp = zlib.decompress(data)
        print(f"✅ Descomprimido: {len(decomp)} bytes")
        
        # Guardar descomprimido
        with open('mensaje_descomprimido.bin', 'wb') as f:
            f.write(decomp)
        print("✅ Guardado como 'mensaje_descomprimido.bin'")
        
        # Intentar leer como texto
        texto = decomp.decode('latin-1', errors='ignore')
        print("\n=== PRIMEROS 500 CARACTERES ===")
        print(texto[:500])
        
        # Buscar flag
        flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
        if flags:
            print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
            return flags[0]
        
        # Buscar cualquier texto que parezca mensaje
        # El mensaje son 892 caracteres, buscar cadenas largas
        cadenas = re.findall(r'[A-Za-z0-9\s\.\,\;\:\!\?\-_]{50,}', texto)
        if cadenas:
            print(f"\n📝 Cadenas largas encontradas ({len(cadenas)}):")
            for i, cadena in enumerate(cadenas[:5]):
                print(f"  {i}: {len(cadena)} caracteres")
                if len(cadena) > 100:
                    print(f"    {cadena[:200]}...")
                    
                # Si encontramos una de 892, es el mensaje
                if len(cadena) >= 892:
                    print(f"\n✅ ¡MENSAJE DE {len(cadena)} CARACTERES ENCONTRADO!")
                    print(cadena)
                    with open('mensaje_final.txt', 'w', encoding='utf-8') as f:
                        f.write(cadena)
                    return cadena
        
        # Si no, buscar en las líneas
        lineas = texto.split('\n')
        print(f"\n📝 Líneas: {len(lineas)}")
        
        for i, linea in enumerate(lineas):
            if len(linea.strip()) > 50 and linea.strip().isprintable():
                print(f"  Línea {i}: {len(linea.strip())} caracteres")
                if len(linea.strip()) >= 892:
                    print(f"✅ ¡LÍNEA DE {len(linea.strip())} CARACTERES!")
                    print(linea.strip())
                    with open('mensaje_final.txt', 'w', encoding='utf-8') as f:
                        f.write(linea.strip())
                    return linea.strip()
        
        # Si nada funciona, el mensaje puede estar en binario
        print("\n🔍 Buscando en binario...")
        
        # Buscar patrones de flag en hex
        hex_data = decomp.hex()
        if '726f6f746d65' in hex_data:  # rootme
            print("✅ 'rootme' encontrado en hex!")
            pos = hex_data.find('726f6f746d65')
            # Extraer el contexto alrededor
            start = max(0, pos - 20)
            end = min(len(hex_data), pos + 60)
            print(f"Contexto: {hex_data[start:end]}")
        
    except zlib.error as e:
        print(f"❌ Error descomprimiendo: {e}")

# Ejecutar
extraer_y_reconstruir_mensaje()
