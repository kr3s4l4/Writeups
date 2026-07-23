from PIL import Image
import re

# Abrir imagen
img = Image.open('ch26.png').convert('L')
pixels = list(img.getdata())

print("Primeros 50 píxeles:", pixels[:50])

# Probar: tomar el LSB de cada píxel y agrupar de a 8
print("\n=== LSB de cada píxel, 8 píxeles por carácter ===")
chars = []
for i in range(0, min(len(pixels), 892 * 8), 8):
    if i + 8 <= len(pixels):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | (pixels[i + j] & 1)
        if 32 <= byte <= 126:
            chars.append(chr(byte))
        else:
            chars.append('�')

texto = ''.join(chars)
print(f"Caracteres válidos: {sum(1 for c in texto if c != '�')}/{len(texto)}")
print("Primeros 300 caracteres:")
print(texto[:300])

# Probar ROT47
def rot47(t):
    return ''.join(chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c for c in t)

rot = rot47(texto)
print("\n=== ROT47 ===")
print(rot[:300])

flags = re.findall(r'rootme\{[^}]+\}', rot, re.IGNORECASE)
if flags:
    print(f"\n🚩 ¡FLAG ENCONTRADA!: {flags[0]}")
