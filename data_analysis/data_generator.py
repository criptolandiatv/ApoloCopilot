# -*- coding: utf-8 -*-
"""
Módulo para geração de dados estruturados do Plantões App Blueprint
"""
import pandas as pd
from config import PRODUCT_INFO


def generate_vision_data():
    """Gera dados da visão do produto"""
    return pd.DataFrame([
        {"Item": "Visão", "Descrição": PRODUCT_INFO["vision"]},
        {"Item": "Missão", "Descrição": PRODUCT_INFO["mission"]},
        {"Item": "Princípios", "Descrição": "LGPD-first • Mobile-first • Automação por voz • Métricas orientando decisões • Simplicidade radical."},
        {"Item": "Domínio / Marca", "Descrição": f"{PRODUCT_INFO['domain']} | {PRODUCT_INFO['email']}"}
    ])


def generate_personas_data():
    """Gera dados das personas de usuário"""
    return pd.DataFrame([
        {
            "Persona": "Médico(a) Plantonista",
            "Jobs": "Encontrar plantões, confirmar/cancelar, substituir",
            "Dores": "Burocracia, confirmações tardias, falhas de comunicação",
            "Gains": "Escala clara, pagamentos previsíveis, autonomia",
            "Clareza UX (0-10)": 9,
            "Fricção (0-10)": 2
        },
        {
            "Persona": "Coordenador(a) de Escala",
            "Jobs": "Montar escala, cobrir faltas, auditar presenças",
            "Dores": "Planilhas manuais, ligações, retrabalho",
            "Gains": "Automação, alertas, visão consolidada",
            "Clareza UX (0-10)": 8,
            "Fricção (0-10)": 3
        },
        {
            "Persona": "RH/Adm Unidade",
            "Jobs": "Contratar, credenciar, faturar",
            "Dores": "Documentos dispersos, compliance",
            "Gains": "Checklists e fluxos padronizados",
            "Clareza UX (0-10)": 8,
            "Fricção (0-10)": 3
        },
        {
            "Persona": "Diretoria/Financeiro",
            "Jobs": "Custos, MRR, SLA",
            "Dores": "Dados atrasados",
            "Gains": "Relatórios e previsões confiáveis",
            "Clareza UX (0-10)": 9,
            "Fricção (0-10)": 2
        },
    ])


def generate_jtbd_data():
    """Gera dados de Jobs To Be Done"""
    return pd.DataFrame([
        {
            "Persona": "Médico",
            "Quando": "preciso confirmar um plantão rapidamente",
            "Eu quero": "responder por WhatsApp/voz",
            "Para": "não perder oportunidades e evitar ligações"
        },
        {
            "Persona": "Coordenador",
            "Quando": "há uma falta de última hora",
            "Eu quero": "disparar busca inteligente de substituto",
            "Para": "garantir cobertura sem retrabalho"
        },
        {
            "Persona": "RH",
            "Quando": "um médico é contratado",
            "Eu quero": "coletar docs e assinar termos digitais",
            "Para": "cumprir LGPD/compliance sem e-mails"
        },
    ])


def generate_value_prop_canvas():
    """Gera dados do Value Proposition Canvas"""
    return pd.DataFrame([
        {"Bloco": "Jobs dos Usuários", "Conteúdo": "Confirmar/atribuir plantões, substituir, faturar, comunicar"},
        {"Bloco": "Dores", "Conteúdo": "Retrabalho manual, falta de cobertura, canal fragmentado"},
        {"Bloco": "Ganhos", "Conteúdo": "Automação, prazos claros, relatórios, prescrição padronizada"},
        {"Bloco": "Aliviadores de Dor", "Conteúdo": "WhatsApp-voice → agenda; matching inteligente; alertas; checklists"},
        {"Bloco": "Criadores de Ganho", "Conteúdo": "Marketplace de plantões; simuladores; MRR previsível; analytics"},
    ])


def generate_modules_data():
    """Gera dados dos módulos da aplicação"""
    return pd.DataFrame([
        {"Módulo": "Cadastro & KYC", "Benefício": "Onboarding guiado • validação docs • LGPD", "Clareza UX (0-10)": 9, "Fricção (0-10)": 2},
        {"Módulo": "Agenda Inteligente", "Benefício": "Escalas automatizadas, matching, conflitos", "Clareza UX (0-10)": 9, "Fricção (0-10)": 2},
        {"Módulo": "Chatbox Médico Auxiliar", "Benefício": "Tira-dúvidas, triagens, protocolos", "Clareza UX (0-10)": 8, "Fricção (0-10)": 3},
        {"Módulo": "Prescrições Padronizadas", "Benefício": "Modelos, CID, via assinatura digital", "Clareza UX (0-10)": 8, "Fricção (0-10)": 3},
        {"Módulo": "Faturamento & Repasse", "Benefício": "Consolidação, NF, previsão de pagamento", "Clareza UX (0-10)": 8, "Fricção (0-10)": 3},
        {"Módulo": "Notificações Omnicanal", "Benefício": "WhatsApp, e-mail, push, SMS", "Clareza UX (0-10)": 9, "Fricção (0-10)": 2},
        {"Módulo": "Automação WhatsApp→Sheets", "Benefício": "Comandos de voz → agendamento", "Clareza UX (0-10)": 9, "Fricção (0-10)": 2},
        {"Módulo": "Integrações (Google/ERP)", "Benefício": "Agenda, Drive, ERPs saúde", "Clareza UX (0-10)": 8, "Fricção (0-10)": 3},
        {"Módulo": "Analytics & Relatórios", "Benefício": "KPIs, funis, SLA, NPS", "Clareza UX (0-10)": 9, "Fricção (0-10)": 2},
        {"Módulo": "Leads & Growth Ops", "Benefício": "Ganchos e iscas, nurturing", "Clareza UX (0-10)": 9, "Fricção (0-10)": 2},
    ])


def generate_use_cases_data():
    """Gera dados dos casos de uso"""
    return pd.DataFrame([
        {"ID": "UC-01", "Use Case": "Confirmar plantão por voz (WhatsApp)", "Módulo": "Automação WhatsApp→Sheets", "Valor": "Reduz tempo de confirmação", "Clareza (0-10)": 9},
        {"ID": "UC-02", "Use Case": "Substituição last-minute com matching", "Módulo": "Agenda Inteligente", "Valor": "Cobertura imediata", "Clareza (0-10)": 8},
        {"ID": "UC-03", "Use Case": "Emitir prescrição padronizada", "Módulo": "Prescrições", "Valor": "Padronização e segurança", "Clareza (0-10)": 8},
        {"ID": "UC-04", "Use Case": "Relatório de repasses por unidade", "Módulo": "Faturamento", "Valor": "Transparência financeira", "Clareza (0-10)": 9},
        {"ID": "UC-05", "Use Case": "Chatbox para protocolos clínicos", "Módulo": "Chatbox Médico", "Valor": "Agilidade na tomada de decisão", "Clareza (0-10)": 8},
    ])


def generate_lead_magnets_data():
    """Gera dados dos lead magnets"""
    return pd.DataFrame([
        {"ID": "LM-01", "Isca": "Simulador de remuneração de plantões", "CTA": "Teste grátis", "Canal": "Landing / plantoes.app", "Conversão Estimada %": 7.5, "Qualidade (0-10)": 9},
        {"ID": "LM-02", "Isca": "Planilha de Escala Inteligente (template)", "CTA": "Baixar agora", "Canal": "Blog / Parcerias", "Conversão Estimada %": 11.0, "Qualidade (0-10)": 8},
        {"ID": "LM-03", "Isca": "Checklist LGPD para clínicas", "CTA": "Receber por e-mail", "Canal": "LinkedIn / Ads", "Conversão Estimada %": 6.0, "Qualidade (0-10)": 8},
        {"ID": "LM-04", "Isca": "Prescrições padronizadas (PDF)", "CTA": "Acessar modelos", "Canal": "WhatsApp CTA", "Conversão Estimada %": 9.0, "Qualidade (0-10)": 9},
        {"ID": "LM-05", "Isca": "Calculadora de custo de não-cobertura", "CTA": "Calcular agora", "Canal": "Landing / Ads", "Conversão Estimada %": 8.0, "Qualidade (0-10)": 9},
    ])


def generate_funnel_events_data():
    """Gera taxonomia de eventos do funil"""
    return pd.DataFrame([
        {"Evento": "view_landing", "Descrição": "Visitou plantoes.app", "Categoria": "Aquisição"},
        {"Evento": "lead_submit", "Descrição": "Preencheu formulário", "Categoria": "Aquisição"},
        {"Evento": "whatsapp_start", "Descrição": "Iniciou conversa WhatsApp", "Categoria": "Ativação"},
        {"Evento": "voice_cmd_schedule", "Descrição": "Usou comando de voz para agendar", "Categoria": "Ativação"},
        {"Evento": "signup", "Descrição": "Criou conta", "Categoria": "Ativação"},
        {"Evento": "schedule_confirmed", "Descrição": "Confirmou plantão", "Categoria": "Adoção"},
        {"Evento": "substitution_auto", "Descrição": "Substituição via matching", "Categoria": "Adoção"},
        {"Evento": "prescription_issued", "Descrição": "Emitiu prescrição", "Categoria": "Adoção"},
        {"Evento": "payment_plan_upgrade", "Descrição": "Upgrade de plano", "Categoria": "Receita"},
        {"Evento": "churn", "Descrição": "Cancelou", "Categoria": "Retenção"},
    ])


def generate_kpis_data():
    """Gera dados de KPIs e OKRs"""
    return pd.DataFrame([
        {"KPI": "Leads/Mês", "Meta": "1200", "Status": "⬆︎ on track"},
        {"KPI": "Taxa de Conversão Lead→Trial", "Meta": "18%", "Status": "~ steady"},
        {"KPI": "Trial→Pago", "Meta": "25%", "Status": "⬆︎ improving"},
        {"KPI": "Ciclo de confirmação (min)", "Meta": "< 5", "Status": "⬇︎ melhor"},
        {"KPI": "Cobertura de plantões", "Meta": "> 98%", "Status": "⬆︎ on track"},
        {"KPI": "NPS", "Meta": "> 60", "Status": "~ steady"},
    ])


def generate_pricing_data():
    """Gera dados de pricing"""
    return pd.DataFrame([
        {"Plano": "Free", "Preço (R$/mês)": "0", "Ideal para": "Testes individuais", "Principais recursos": "Confirmação via WhatsApp • 3 prescrições/mês"},
        {"Plano": "Starter", "Preço (R$/mês)": "149", "Ideal para": "Pequenas clínicas", "Principais recursos": "Agenda inteligente • Substituições • Prescrições ilimitadas"},
        {"Plano": "Pro", "Preço (R$/mês)": "399", "Ideal para": "Redes de clínicas", "Principais recursos": "Relatórios • Integrações Google/ERP • SLA"},
        {"Plano": "Enterprise", "Preço (R$/mês)": "Sob consulta", "Ideal para": "Hospitais/Rede", "Principais recursos": "SSO • Onboarding dedicado • Compliance avançado"},
    ])


def generate_automations_data():
    """Gera dados das automações WhatsApp → Google Sheets"""
    return pd.DataFrame([
        {"Etapa": "1. Trigger", "Detalhe": "Usuário envia áudio no WhatsApp: 'Confirmar plantão sexta 19h-7h UPA Centro'"},
        {"Etapa": "2. Transcrição", "Detalhe": "STT transcreve e extrai entidades (data, hora, unidade)"},
        {"Etapa": "3. Validação", "Detalhe": "Bot verifica conflitos de agenda e políticas"},
        {"Etapa": "4. GSheets", "Detalhe": "Escreve/atualiza linha em Escala!A:K (status=confirmado)"},
        {"Etapa": "5. Confirmação", "Detalhe": "Retorna resumo ao WhatsApp e agenda push/ICS"},
    ])


def generate_data_model():
    """Gera modelo de dados"""
    return pd.DataFrame([
        {"Entidade": "Medico", "Campos-chave": "id, nome, CRM, especialidade, whatsapp, consentimento", "PII": "Sim", "Base Legal": "Consentimento/Contrato"},
        {"Entidade": "Unidade", "Campos-chave": "id, nome, CNPJ, endereço, SLA", "PII": "Não", "Base Legal": "Contrato"},
        {"Entidade": "Plantao", "Campos-chave": "id, unidade_id, medico_id, inicio, fim, status", "PII": "Não", "Base Legal": "Interesse Legítimo"},
        {"Entidade": "Substituicao", "Campos-chave": "id, plantao_id, medico_sub_id, motivo, status", "PII": "Não", "Base Legal": "Interesse Legítimo"},
        {"Entidade": "Prescricao", "Campos-chave": "id, medico_id, paciente_hash, modelo_id, assinatura", "PII": "Pseudon.", "Base Legal": "Obrigação legal"},
        {"Entidade": "Lead", "Campos-chave": "id, email, origem, campanha, score, consentimento", "PII": "Sim", "Base Legal": "Consentimento"},
    ])


def generate_compliance_data():
    """Gera dados de compliance"""
    return pd.DataFrame([
        {"Tema": "LGPD – Bases legais", "Ação": "Mapear tratamento por entidade • DPA com processadores"},
        {"Tema": "Segurança", "Ação": "Criptografia em repouso/trânsito • Gestão de chaves"},
        {"Tema": "Governança", "Ação": "DPO • Registro de incidentes • DPIA"},
        {"Tema": "Retenção", "Ação": "Política de retenção e anonimização"},
    ])


def generate_pitch_data():
    """Gera resumo do pitch de vendas"""
    return pd.DataFrame([
        {"Bloco": "Problema", "Resumo": "Fricção e falhas na cobertura de plantões + burocracia de comunicação."},
        {"Bloco": "Solução", "Resumo": "Automação por voz/WhatsApp + agenda inteligente + prescrições + analytics."},
        {"Bloco": "Tração (amostragem)", "Resumo": ">1k leads/mês estimados com iscas e parcerias; cobertura >98%."},
        {"Bloco": "Modelo", "Resumo": "SaaS escalonado (Free/Starter/Pro/Enterprise) + serviços."},
        {"Bloco": "Diferencial", "Resumo": "Foco em zero-fricção e integração nativa com Google e WhatsApp."},
    ])


def generate_roadmap_data():
    """Gera roadmap do produto"""
    return pd.DataFrame([
        {"Fase": "MVP (0-3m)", "Escopo": "WhatsApp→GSheets, Agenda básica, Prescrições, Landing + iscas", "Critério": "20 clínicas, 200 médicos"},
        {"Fase": "V1 (3-6m)", "Escopo": "Matching, Faturamento, Analytics, SSO, App mobile", "Critério": "MRR R$120k, NPS>60"},
        {"Fase": "V2 (6-12m)", "Escopo": "Marketplace de plantões, IA clínica contextual, ERPs", "Critério": "Rede hospitalar, churn<2%"},
    ])


def generate_tests_data():
    """Gera plano de testes A/B"""
    return pd.DataFrame([
        {"Teste": "A/B CTA Lead Magnet", "Hipótese": "CTA WhatsApp converte mais que formulário", "Métrica": "CVR", "Amostra": "n=10k sessões", "Meta": "+15%"},
        {"Teste": "Fluxo Voz vs Texto", "Hipótese": "Voz reduz tempo de confirmação", "Métrica": "T_confirmação", "Amostra": "n=2k confirmações", "Meta": "-30%"},
        {"Teste": "Matching Regras vs IA", "Hipótese": "IA ↑ cobertura em faltas", "Métrica": "Cobertura", "Amostra": "n=300 faltas", "Meta": "+10%"},
    ])


def generate_report_data():
    """Gera dados de relatório mensal"""
    return pd.DataFrame([
        {"Mês": "2025-08", "Leads": 800, "Trials": 160, "Pagos": 40, "MRR (R$)": 15960, "NPS": 58},
        {"Mês": "2025-09", "Leads": 1000, "Trials": 200, "Pagos": 52, "MRR (R$)": 20748, "NPS": 60},
        {"Mês": "2025-10", "Leads": 1200, "Trials": 220, "Pagos": 60, "MRR (R$)": 23940, "NPS": 61},
        {"Mês": "2025-11", "Leads": 1300, "Trials": 234, "Pagos": 68, "MRR (R$)": 27132, "NPS": 63},
    ])


def generate_channels_data():
    """Gera dados de canais para dashboard"""
    return pd.DataFrame([
        {"Canal": "Orgânico", "Leads": 380, "CVR Lead→Trial %": 22, "CVR Trial→Pago %": 28},
        {"Canal": "Ads", "Leads": 520, "CVR Lead→Trial %": 15, "CVR Trial→Pago %": 22},
        {"Canal": "Parcerias", "Leads": 260, "CVR Lead→Trial %": 26, "CVR Trial→Pago %": 30},
        {"Canal": "WhatsApp CTA", "Leads": 140, "CVR Lead→Trial %": 32, "CVR Trial→Pago %": 33},
    ])


def generate_all_data():
    """Gera todos os dados e retorna um dicionário com os DataFrames"""
    return {
        "vision": generate_vision_data(),
        "personas": generate_personas_data(),
        "jtbd": generate_jtbd_data(),
        "vpc": generate_value_prop_canvas(),
        "modules": generate_modules_data(),
        "use_cases": generate_use_cases_data(),
        "lead_magnets": generate_lead_magnets_data(),
        "funnel_events": generate_funnel_events_data(),
        "kpis": generate_kpis_data(),
        "pricing": generate_pricing_data(),
        "automations": generate_automations_data(),
        "data_model": generate_data_model(),
        "compliance": generate_compliance_data(),
        "pitch": generate_pitch_data(),
        "roadmap": generate_roadmap_data(),
        "tests": generate_tests_data(),
        "report": generate_report_data(),
        "channels": generate_channels_data()
    }
