import zlib
import re

def extraer_mensaje_del_zlib():
    # Leer el archivo zlib
    with open('_ch26.png.extracted/1B9.zlib', 'rb') as f:
        data = f.read()
    
    print(f"Tamaño del archivo: {len(data)} bytes")
    
    # Intentar descomprimir con diferentes wbits
    for wbits in [15, -15, 31, 47]:
        try:
            decomp = zlib.decompress(data, wbits=wbits)
            print(f"✅ Descomprimido con wbits={wbits}: {len(decomp)} bytes")
            
            # Intentar leer como texto
            try:
                texto = decomp.decode('latin-1', errors='ignore')
                print("\n=== TEXTO (latin-1) ===")
                print(texto[:500])
                
                # Buscar flag
                flags = re.findall(r'rootme\{[^}]+\}', texto, re.IGNORECASE)
                if flags:
                    print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
                    return flags[0]
                
                # Buscar palabras clave
                palabras = ['Breizh', 'BZH', 'bretagne', 'breton', 'independance', 'liberte']
                for palabra in palabras:
                    if palabra.lower() in texto.lower():
                        print(f"\n✅ '{palabra}' encontrada!")
                        pos = texto.lower().find(palabra.lower())
                        print(f"Contexto: ...{texto[max(0,pos-50):pos+100]}...")
                        
            except:
                print("No es texto latin-1")
                
        except zlib.error as e:
            print(f"❌ wbits={wbits}: {e}")
    
    # Si no se descomprime, buscar en los datos crudos
    print("\n=== BUSCANDO EN DATOS CRUDOS ===")
    texto = data.decode('latin-1', errors='ignore')
    
    # Buscar cualquier cadena larga de texto
    cadenas = re.findall(r'[A-Za-z0-9\s\.\,\;\:\!\?\-]{20,}', texto)
    if cadenas:
        print(f"Encontradas {len(cadenas)} cadenas de texto")
        for i, cadena in enumerate(cadenas[:10]):
            if len(cadena) > 50:
                print(f"\nCadena {i}: {len(cadena)} caracteres")
                print(cadena[:200])
                
                # Buscar flag
                flags = re.findall(r'rootme\{[^}]+\}', cadena, re.IGNORECASE)
                if flags:
                    print(f"🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
                    return flags[0]
    
    return None

# Ejecutar
extraer_mensaje_del_zlib()
