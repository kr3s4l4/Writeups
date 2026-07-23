import subprocess

# Desensamblar el binario
subprocess.run(['objdump', '-d', '-M', 'intel', 'innocent.bin'], stdout=open('disasm.txt', 'w'))

# Analizar instrucciones add/sub para extraer bits
with open('disasm.txt', 'r') as f:
    for line in f:
        if 'add' in line:
            # bit 0
            pass
        elif 'sub' in line:
            # bit 1
            pass
