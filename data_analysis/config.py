# -*- coding: utf-8 -*-
"""
Configurações e constantes para o projeto Plantões App Blueprint
"""
import os
from datetime import datetime

# Diretórios
BASE_PATH = os.path.join(os.path.dirname(__file__), "output")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
REPORTS_PATH = os.path.join(os.path.dirname(__file__), "reports")

# Arquivos de saída
OUTPUT_FILENAME = "Plantoes_App_Blueprint.xlsx"
CHART1_FILENAME = "chart_leads_por_canal.png"
CHART2_FILENAME = "chart_cvr_lead_trial.png"

# Formatação Excel
EXCEL_FORMATS = {
    "header": {"bold": True, "bg_color": "#F2F2F2", "border": 1},
    "good": {"bg_color": "#C6EFCE", "font_color": "#006100"},
    "warn": {"bg_color": "#FFEB9C", "font_color": "#9C6500"},
    "bad": {"bg_color": "#F2DCDB", "font_color": "#9C0006"}
}

# Dimensões de colunas padrão
COLUMN_WIDTHS = {
    0: 22,  # Primeira coluna
    1: 60,  # Segunda coluna
    2: 30,  # Terceira coluna
    3: 22   # Demais colunas
}

# Nomes das abas
SHEET_NAMES = {
    "vision": "01_Visao",
    "personas": "02_Personas",
    "jtbd": "03_JTBD",
    "vpc": "04_ValueProp",
    "modules": "05_Modulos",
    "use_cases": "06_UseCases",
    "lead_magnets": "07_LeadMagnets",
    "funnel_events": "08_Events",
    "kpis": "09_KPIs",
    "pricing": "10_Precos",
    "automations": "11_Automacoes",
    "data_model": "12_Dados",
    "compliance": "13_Compliance",
    "pitch": "14_Pitch",
    "roadmap": "15_Roadmap",
    "tests": "16_Testes",
    "report": "17_Relatorio",
    "channels": "18_DashboardSrc",
    "dashboard": "00_Dashboard"
}

# Configurações de gráficos
CHART_DPI = 160
CHART_SCALE = 0.9

# Informações do produto
PRODUCT_INFO = {
    "name": "plantoes.app",
    "domain": "plantoes.app",
    "email": "contato@plantoes.app",
    "vision": "Conectar médicos e unidades com máxima eficiência, segurança e inteligência, reduzindo fricção na gestão de plantões.",
    "mission": "Automatizar escala, substituições e comunicação, com UX clara e integração nativa (WhatsApp, Google, prontuário)."
}

def ensure_directories():
    """Cria os diretórios necessários se não existirem"""
    for path in [BASE_PATH, DATA_PATH, REPORTS_PATH]:
        os.makedirs(path, exist_ok=True)

def get_output_path(filename):
    """Retorna o caminho completo para um arquivo de saída"""
    return os.path.join(BASE_PATH, filename)

def get_timestamp():
    """Retorna timestamp formatado para uso em relatórios"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")
