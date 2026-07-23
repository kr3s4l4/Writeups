from PIL import Image

# Abrir y convertir a grises
img = Image.open('ch26.png').convert('L')
pixels = list(img.getdata())

print(f"Píxeles: {len(pixels)}")
print(f"Primeros 10 píxeles: {pixels[:10]}")

# Probar los métodos más probables
for nombre, func in [
    ('diferencia', lambda p1, p2: (p2 - p1) % 256),
    ('lsb_combinado', lambda p1, p2: ((p1 & 1) << 1) | (p2 & 1)),
    ('bit2', lambda p1, p2: ((p1 >> 2) & 1) | (((p2 >> 2) & 1) << 1)),
]:
    print(f"\n=== {nombre} ===")
    chars = []
    for i in range(0, min(len(pixels), 892*2), 2):
        if i+1 < len(pixels):
            val = func(pixels[i], pixels[i+1])
            if 32 <= val <= 126:
                chars.append(chr(val))
            else:
                chars.append('�')
    
    texto = ''.join(chars)
    imprimibles = sum(1 for c in texto if c != '�')
    print(f"Válidos: {imprimibles}/{len(texto)}")
    if imprimibles > 800:
        print(f"¡Funciona! {texto[:200]}")
