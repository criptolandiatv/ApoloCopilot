#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador simplificado de blueprint - SEM DEPENDÊNCIAS EXTERNAS

Este script gera arquivos CSV e JSON com os dados do blueprint,
não requerendo pandas, matplotlib ou xlsxwriter.

Uso:
    python3 simple_generator.py
"""
import json
import csv
import os
from datetime import datetime


# Diretório de saída
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output_simple")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_to_csv(data, filename):
    """Salva dados em arquivo CSV"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    if not data:
        return

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"  ✓ {filename}")
    return filepath


def save_to_json(data, filename):
    """Salva dados em arquivo JSON"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ {filename}")
    return filepath


# Dados estruturados (mesmos do data_generator.py mas sem pandas)
VISION_DATA = [
    {"Item": "Visão", "Descrição": "Conectar médicos e unidades com máxima eficiência, segurança e inteligência, reduzindo fricção na gestão de plantões."},
    {"Item": "Missão", "Descrição": "Automatizar escala, substituições e comunicação, com UX clara e integração nativa (WhatsApp, Google, prontuário)."},
    {"Item": "Princípios", "Descrição": "LGPD-first • Mobile-first • Automação por voz • Métricas orientando decisões • Simplicidade radical."},
    {"Item": "Domínio / Marca", "Descrição": "plantoes.app | contato@plantoes.app"}
]

PERSONAS_DATA = [
    {
        "Persona": "Médico(a) Plantonista",
        "Jobs": "Encontrar plantões, confirmar/cancelar, substituir",
        "Dores": "Burocracia, confirmações tardias, falhas de comunicação",
        "Gains": "Escala clara, pagamentos previsíveis, autonomia",
        "Clareza_UX": 9,
        "Friccao": 2
    },
    {
        "Persona": "Coordenador(a) de Escala",
        "Jobs": "Montar escala, cobrir faltas, auditar presenças",
        "Dores": "Planilhas manuais, ligações, retrabalho",
        "Gains": "Automação, alertas, visão consolidada",
        "Clareza_UX": 8,
        "Friccao": 3
    },
    {
        "Persona": "RH/Adm Unidade",
        "Jobs": "Contratar, credenciar, faturar",
        "Dores": "Documentos dispersos, compliance",
        "Gains": "Checklists e fluxos padronizados",
        "Clareza_UX": 8,
        "Friccao": 3
    },
    {
        "Persona": "Diretoria/Financeiro",
        "Jobs": "Custos, MRR, SLA",
        "Dores": "Dados atrasados",
        "Gains": "Relatórios e previsões confiáveis",
        "Clareza_UX": 9,
        "Friccao": 2
    },
]

MODULES_DATA = [
    {"Modulo": "Cadastro & KYC", "Beneficio": "Onboarding guiado • validação docs • LGPD", "Clareza_UX": 9, "Friccao": 2},
    {"Modulo": "Agenda Inteligente", "Beneficio": "Escalas automatizadas, matching, conflitos", "Clareza_UX": 9, "Friccao": 2},
    {"Modulo": "Chatbox Médico Auxiliar", "Beneficio": "Tira-dúvidas, triagens, protocolos", "Clareza_UX": 8, "Friccao": 3},
    {"Modulo": "Prescrições Padronizadas", "Beneficio": "Modelos, CID, via assinatura digital", "Clareza_UX": 8, "Friccao": 3},
    {"Modulo": "Faturamento & Repasse", "Beneficio": "Consolidação, NF, previsão de pagamento", "Clareza_UX": 8, "Friccao": 3},
    {"Modulo": "Notificações Omnicanal", "Beneficio": "WhatsApp, e-mail, push, SMS", "Clareza_UX": 9, "Friccao": 2},
    {"Modulo": "Automação WhatsApp→Sheets", "Beneficio": "Comandos de voz → agendamento", "Clareza_UX": 9, "Friccao": 2},
    {"Modulo": "Integrações (Google/ERP)", "Beneficio": "Agenda, Drive, ERPs saúde", "Clareza_UX": 8, "Friccao": 3},
    {"Modulo": "Analytics & Relatórios", "Beneficio": "KPIs, funis, SLA, NPS", "Clareza_UX": 9, "Friccao": 2},
    {"Modulo": "Leads & Growth Ops", "Beneficio": "Ganchos e iscas, nurturing", "Clareza_UX": 9, "Friccao": 2},
]

LEAD_MAGNETS_DATA = [
    {"ID": "LM-01", "Isca": "Simulador de remuneração de plantões", "CTA": "Teste grátis", "Canal": "Landing / plantoes.app", "Conversao_Estimada": 7.5, "Qualidade": 9},
    {"ID": "LM-02", "Isca": "Planilha de Escala Inteligente (template)", "CTA": "Baixar agora", "Canal": "Blog / Parcerias", "Conversao_Estimada": 11.0, "Qualidade": 8},
    {"ID": "LM-03", "Isca": "Checklist LGPD para clínicas", "CTA": "Receber por e-mail", "Canal": "LinkedIn / Ads", "Conversao_Estimada": 6.0, "Qualidade": 8},
    {"ID": "LM-04", "Isca": "Prescrições padronizadas (PDF)", "CTA": "Acessar modelos", "Canal": "WhatsApp CTA", "Conversao_Estimada": 9.0, "Qualidade": 9},
    {"ID": "LM-05", "Isca": "Calculadora de custo de não-cobertura", "CTA": "Calcular agora", "Canal": "Landing / Ads", "Conversao_Estimada": 8.0, "Qualidade": 9},
]

KPIS_DATA = [
    {"KPI": "Leads/Mês", "Meta": "1200", "Status": "on track"},
    {"KPI": "Taxa de Conversão Lead→Trial", "Meta": "18%", "Status": "steady"},
    {"KPI": "Trial→Pago", "Meta": "25%", "Status": "improving"},
    {"KPI": "Ciclo de confirmação (min)", "Meta": "< 5", "Status": "melhor"},
    {"KPI": "Cobertura de plantões", "Meta": "> 98%", "Status": "on track"},
    {"KPI": "NPS", "Meta": "> 60", "Status": "steady"},
]

PRICING_DATA = [
    {"Plano": "Free", "Preco_Mensal": "0", "Ideal_Para": "Testes individuais", "Recursos": "Confirmação via WhatsApp • 3 prescrições/mês"},
    {"Plano": "Starter", "Preco_Mensal": "149", "Ideal_Para": "Pequenas clínicas", "Recursos": "Agenda inteligente • Substituições • Prescrições ilimitadas"},
    {"Plano": "Pro", "Preco_Mensal": "399", "Ideal_Para": "Redes de clínicas", "Recursos": "Relatórios • Integrações Google/ERP • SLA"},
    {"Plano": "Enterprise", "Preco_Mensal": "Sob consulta", "Ideal_Para": "Hospitais/Rede", "Recursos": "SSO • Onboarding dedicado • Compliance avançado"},
]

REPORT_DATA = [
    {"Mes": "2025-08", "Leads": 800, "Trials": 160, "Pagos": 40, "MRR": 15960, "NPS": 58},
    {"Mes": "2025-09", "Leads": 1000, "Trials": 200, "Pagos": 52, "MRR": 20748, "NPS": 60},
    {"Mes": "2025-10", "Leads": 1200, "Trials": 220, "Pagos": 60, "MRR": 23940, "NPS": 61},
    {"Mes": "2025-11", "Leads": 1300, "Trials": 234, "Pagos": 68, "MRR": 27132, "NPS": 63},
]

CHANNELS_DATA = [
    {"Canal": "Orgânico", "Leads": 380, "CVR_Lead_Trial": 22, "CVR_Trial_Pago": 28},
    {"Canal": "Ads", "Leads": 520, "CVR_Lead_Trial": 15, "CVR_Trial_Pago": 22},
    {"Canal": "Parcerias", "Leads": 260, "CVR_Lead_Trial": 26, "CVR_Trial_Pago": 30},
    {"Canal": "WhatsApp CTA", "Leads": 140, "CVR_Lead_Trial": 32, "CVR_Trial_Pago": 33},
]


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("📊 PLANTÕES APP - GERADOR SIMPLIFICADO")
    print("="*60)
    print("\n🔧 Gerando arquivos CSV e JSON (sem dependências externas)...\n")

    # Salva CSVs
    print("📄 Gerando arquivos CSV:")
    save_to_csv(VISION_DATA, "01_visao.csv")
    save_to_csv(PERSONAS_DATA, "02_personas.csv")
    save_to_csv(MODULES_DATA, "05_modulos.csv")
    save_to_csv(LEAD_MAGNETS_DATA, "07_lead_magnets.csv")
    save_to_csv(KPIS_DATA, "09_kpis.csv")
    save_to_csv(PRICING_DATA, "10_pricing.csv")
    save_to_csv(REPORT_DATA, "17_report.csv")
    save_to_csv(CHANNELS_DATA, "18_channels.csv")

    # Salva JSON consolidado
    print("\n📦 Gerando arquivo JSON consolidado:")
    all_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "product": "plantoes.app",
            "version": "1.0"
        },
        "vision": VISION_DATA,
        "personas": PERSONAS_DATA,
        "modules": MODULES_DATA,
        "lead_magnets": LEAD_MAGNETS_DATA,
        "kpis": KPIS_DATA,
        "pricing": PRICING_DATA,
        "report": REPORT_DATA,
        "channels": CHANNELS_DATA
    }
    save_to_json(all_data, "plantoes_app_blueprint.json")

    # Estatísticas
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS")
    print("="*60)
    last_month = REPORT_DATA[-1]
    print(f"\n📈 Métricas do último mês ({last_month['Mes']}):")
    print(f"   • Leads: {last_month['Leads']}")
    print(f"   • Trials: {last_month['Trials']}")
    print(f"   • Pagos: {last_month['Pagos']}")
    print(f"   • MRR: R$ {last_month['MRR']:,}".replace(',', '.'))
    print(f"   • NPS: {last_month['NPS']}")

    print(f"\n📁 Arquivos gerados em: {OUTPUT_DIR}/")
    print("\n✅ Processo concluído!\n")

    print("💡 Próximos passos:")
    print("   1. Abra os arquivos CSV no Excel, Google Sheets ou LibreOffice")
    print("   2. Use o JSON para integrações e APIs")
    print("   3. Para gráficos, instale as dependências: pip install -r requirements.txt")
    print("   4. Então execute: python main.py\n")


if __name__ == "__main__":
    main()
