#!/bin/bash
# -*- coding: utf-8 -*-
# Script de setup automatizado para o módulo de análise de dados

set -e  # Para na primeira falha

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║    PLANTÕES APP - SETUP DE ANÁLISE DE DADOS       ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}🔧 Iniciando setup...${NC}\n"

# 1. Verificar Python
echo -e "${BLUE}[1/5]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Por favor, instale Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION encontrado"

# 2. Verificar pip
echo -e "\n${BLUE}[2/5]${NC} Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 não encontrado. Por favor, instale pip${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip encontrado"

# 3. Criar ambiente virtual (opcional mas recomendado)
echo -e "\n${BLUE}[3/5]${NC} Configurando ambiente virtual..."
read -p "Deseja criar um ambiente virtual? (recomendado) [y/N]: " create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Ambiente virtual criado"
    else
        echo -e "${YELLOW}⚠${NC} Ambiente virtual já existe"
    fi

    echo "Ativando ambiente virtual..."
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Ambiente virtual ativado"
else
    echo -e "${YELLOW}⚠${NC} Pulando criação de ambiente virtual"
fi

# 4. Instalar dependências
echo -e "\n${BLUE}[4/5]${NC} Instalando dependências..."
pip3 install -r requirements.txt --upgrade
echo -e "${GREEN}✓${NC} Dependências instaladas"

# 5. Criar diretórios
echo -e "\n${BLUE}[5/5]${NC} Criando estrutura de diretórios..."
mkdir -p output data notebooks reports
echo -e "${GREEN}✓${NC} Diretórios criados"

# Verificação final
echo -e "\n${BLUE}Verificando instalação...${NC}"
python3 -c "import pandas; import matplotlib; import xlsxwriter; print('✓ Todas as bibliotecas principais importadas com sucesso')"

# Dar permissão de execução ao main.py
chmod +x main.py

echo -e "\n${GREEN}╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║           ✅ SETUP CONCLUÍDO COM SUCESSO!         ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}📝 Próximos passos:${NC}"
echo -e "  1. Execute: ${GREEN}python3 main.py${NC}"
echo -e "  2. Ou leia: ${GREEN}cat README.md${NC} para mais opções"

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}💡 Dica:${NC} Para ativar o ambiente virtual no futuro, use:"
    echo -e "  ${GREEN}source venv/bin/activate${NC}"
fi

echo ""
