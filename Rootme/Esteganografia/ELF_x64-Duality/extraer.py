import lzma
import subprocess

# Extraer la sección
subprocess.run(['objcopy', '--dump-section', '.gnu_debugdata=debugdata.lzma', 'innocent.bin'])

# Intentar descomprimir
try:
    with open('debugdata.lzma', 'rb') as f:
        data = f.read()
    decompressed = lzma.decompress(data)
    with open('debugdata_extracted.elf', 'wb') as f:
        f.write(decompressed)
    print("¡Descomprimido correctamente!")
    print("Archivo: debugdata_extracted.elf")
except Exception as e:
    print(f"Error: {e}")
