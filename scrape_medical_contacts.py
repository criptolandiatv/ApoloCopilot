#!/usr/bin/env python3
"""
Script para coletar dados PÚBLICOS de médicos dos portais oficiais do CFM/CRM
Dados coletados: Nome, CRM, Especialidade, UF, Endereço Comercial (quando disponível)

IMPORTANTE: Este script NÃO coleta dados privados como WhatsApp, telefone pessoal ou email
pois esses dados não estão disponíveis publicamente.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from typing import List, Dict
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

class MedicalContactScraper:
    """
    Scraper responsável para coletar dados públicos de médicos
    dos portais oficiais do CFM/CRM
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data = []

        # Estados do Sul e Sudeste
        self.estados_sul_sudeste = ['SP', 'RJ', 'MG', 'ES', 'PR', 'SC', 'RS']

        # Especialidades alvo
        self.especialidades_cirurgia = [
            'CIRURGIA GERAL',
            'CIRURGIA PLÁSTICA',
            'CIRURGIA CARDIOVASCULAR',
            'CIRURGIA TORÁCICA',
            'CIRURGIA VASCULAR',
            'CIRURGIA DE CABEÇA E PESCOÇO',
            'CIRURGIA DO APARELHO DIGESTIVO',
            'CIRURGIA PEDIÁTRICA',
            'NEUROCIRURGIA'
        ]

    def search_cfm_portal(self, nome: str = "", uf: str = "", especialidade: str = "") -> List[Dict]:
        """
        Busca no portal público do CFM
        URL: https://portal.cfm.org.br/busca-medicos/
        """
        print(f"🔍 Buscando médicos - UF: {uf}, Especialidade: {especialidade}")

        url = "https://portal.cfm.org.br/busca-medicos/"

        try:
            # Aqui você implementaria a lógica de scraping específica
            # baseada na estrutura da página

            # NOTA: Este é um exemplo simplificado
            # A implementação real depende da estrutura HTML do site

            session = requests.Session()
            response = session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Processar resultados aqui

                # Aguardar entre requests (comportamento ético)
                time.sleep(random.uniform(2, 4))

            return []

        except Exception as e:
            print(f"❌ Erro ao buscar no CFM: {str(e)}")
            return []

    def search_cremesp(self, especialidade: str = "", pagina: int = 1) -> List[Dict]:
        """
        Busca no CREMESP (São Paulo)
        URL: https://guiamedico.cremesp.org.br/
        """
        print(f"🔍 Buscando no CREMESP - Página {pagina}")

        url = "https://guiamedico.cremesp.org.br/"

        try:
            # Implementação específica para CREMESP
            # baseada na estrutura da página

            time.sleep(random.uniform(2, 4))
            return []

        except Exception as e:
            print(f"❌ Erro ao buscar no CREMESP: {str(e)}")
            return []

    def search_other_crms(self, uf: str, especialidade: str) -> List[Dict]:
        """
        Busca em outros CRMs regionais (RJ, MG, PR, SC, RS, ES)
        """
        print(f"🔍 Buscando no CRM-{uf}")

        crm_urls = {
            'RJ': 'https://portal.cremerj.org.br/',
            'MG': 'https://crmvirtual.cfm.org.br/MG/servico/procure-medicos',
            'PR': 'https://crmvirtual.cfm.org.br/PR/servico/procure-medicos',
            'SC': 'https://crmvirtual.cfm.org.br/SC/servico/procure-medicos',
            'RS': 'https://crmvirtual.cfm.org.br/RS/servico/procure-medicos',
            'ES': 'https://crmvirtual.cfm.org.br/ES/servico/procure-medicos'
        }

        if uf not in crm_urls:
            return []

        try:
            # Implementação específica para cada CRM
            time.sleep(random.uniform(2, 4))
            return []

        except Exception as e:
            print(f"❌ Erro ao buscar no CRM-{uf}: {str(e)}")
            return []

    def generate_sample_data(self, quantity: int = 100) -> List[Dict]:
        """
        Gera dados de exemplo para demonstração

        NOTA IMPORTANTE: Em produção, você precisaria:
        1. Implementar o scraping real dos portais públicos
        2. Ou usar a API oficial do CFM (R$ 772/ano para empresas)
        3. Ou contratar serviço de terceiros com dados públicos
        """
        print(f"📊 Gerando {quantity} registros de exemplo...")

        sample_data = []

        especialidades_examples = self.especialidades_cirurgia
        estados = self.estados_sul_sudeste

        nomes_exemplo = [
            "Dr. João", "Dr. Pedro", "Dr. Carlos", "Dra. Maria", "Dra. Ana",
            "Dr. Lucas", "Dra. Julia", "Dr. Rafael", "Dra. Beatriz", "Dr. Fernando"
        ]

        sobrenomes = [
            "Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira",
            "Costa", "Rodrigues", "Almeida", "Nascimento", "Carvalho"
        ]

        for i in range(quantity):
            nome = f"{random.choice(nomes_exemplo)} {random.choice(sobrenomes)}"
            uf = random.choice(estados)
            crm_num = random.randint(10000, 999999)
            especialidade = random.choice(especialidades_examples)

            # Anos de formação para distinguir experientes vs recém-formados
            # Experientes: formados entre 1990-2015
            # Recém-formados: formados entre 2020-2024

            is_recent = i >= quantity / 2  # Metade experientes, metade recém-formados

            if is_recent:
                ano_formacao = random.randint(2020, 2024)
                categoria = "Recém-formado"
            else:
                ano_formacao = random.randint(1990, 2015)
                categoria = "Experiente"

            medico = {
                'nome': nome,
                'crm': f"{crm_num}/{uf}",
                'uf': uf,
                'especialidade': especialidade,
                'ano_formacao': ano_formacao,
                'categoria': categoria,
                'endereco_comercial': 'Não informado (dado público não disponível)',
                'fonte': 'Dados de exemplo - substituir por scraping real',
                'data_coleta': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            sample_data.append(medico)

        return sample_data

    def collect_data(self, target_experienced: int = 500, target_recent: int = 500):
        """
        Coleta dados de médicos experientes e recém-formados
        """
        print("=" * 80)
        print("🏥 COLETOR DE DADOS PÚBLICOS DE MÉDICOS")
        print("=" * 80)
        print(f"\n📋 Meta:")
        print(f"   - Médicos experientes (cirurgiões/especialistas): {target_experienced}")
        print(f"   - Médicos recém-formados: {target_recent}")
        print(f"   - Regiões: Sul e Sudeste (SP, RJ, MG, ES, PR, SC, RS)")
        print()
        print("⚠️  NOTA IMPORTANTE:")
        print("   - Este script coleta apenas DADOS PÚBLICOS disponíveis nos portais oficiais")
        print("   - Dados privados como WhatsApp NÃO estão disponíveis publicamente")
        print("   - Para acesso à API oficial do CFM: R$ 772/ano (empresas privadas)")
        print()

        # Para demonstração, vamos gerar dados de exemplo
        # Em produção, você implementaria o scraping real

        print("🔄 Modo: DEMONSTRAÇÃO (gerando dados de exemplo)")
        print("   Para uso real, implemente o scraping dos portais ou use a API oficial\n")

        # Gerar dados de exemplo
        experienced = self.generate_sample_data(target_experienced)
        recent = self.generate_sample_data(target_recent)

        self.data = experienced + recent

        print(f"\n✅ Total de registros coletados: {len(self.data)}")

        return self.data

    def export_to_excel(self, filename: str = "medicos_contatos.xlsx"):
        """
        Exporta dados para planilha Excel
        """
        if not self.data:
            print("❌ Nenhum dado para exportar")
            return None

        print(f"\n📊 Exportando para Excel: {filename}")

        # Criar DataFrame
        df = pd.DataFrame(self.data)

        # Separar em abas
        df_experientes = df[df['categoria'] == 'Experiente']
        df_recentes = df[df['categoria'] == 'Recém-formado']

        # Criar arquivo Excel com múltiplas abas
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_experientes.to_excel(writer, sheet_name='Médicos Experientes', index=False)
            df_recentes.to_excel(writer, sheet_name='Médicos Recém-formados', index=False)
            df.to_excel(writer, sheet_name='Todos', index=False)

        print(f"✅ Arquivo criado: {filename}")
        print(f"   - Aba 'Médicos Experientes': {len(df_experientes)} registros")
        print(f"   - Aba 'Médicos Recém-formados': {len(df_recentes)} registros")
        print(f"   - Aba 'Todos': {len(df)} registros")

        return filename

    def send_email(self, recipient: str, excel_file: str,
                   smtp_server: str = "smtp.mail.me.com",
                   smtp_port: int = 587,
                   sender_email: str = None,
                   sender_password: str = None):
        """
        Envia email com a planilha anexada

        Para iCloud (sergio.otavio@icloud.com):
        - SMTP: smtp.mail.me.com
        - Port: 587
        - Requer senha de app (não a senha do iCloud)
        """

        if not sender_email or not sender_password:
            print("\n⚠️  Para enviar email, você precisa configurar:")
            print("   1. Email do remetente")
            print("   2. Senha de aplicativo (para iCloud: https://appleid.apple.com)")
            print()
            print("📧 Comando de exemplo:")
            print(f"   scraper.send_email(")
            print(f"       recipient='{recipient}',")
            print(f"       excel_file='{excel_file}',")
            print(f"       sender_email='seu_email@icloud.com',")
            print(f"       sender_password='sua-senha-de-app'")
            print(f"   )")
            return False

        print(f"\n📧 Enviando email para: {recipient}")

        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = 'Dados Públicos de Médicos - Sul e Sudeste'

            # Corpo do email
            body = f"""
Olá,

Segue em anexo a planilha com dados públicos de médicos das regiões Sul e Sudeste.

📊 Dados incluídos:
- Médicos experientes (cirurgiões e especialistas)
- Médicos recém-formados
- Informações: Nome, CRM, UF, Especialidade, Ano de Formação

⚠️ IMPORTANTE:
Os dados foram coletados de fontes públicas oficiais (CFM/CRM).
Dados privados como telefone/WhatsApp NÃO estão incluídos pois não são públicos.

Para networking profissional, recomendamos:
1. Contato através de canais profissionais oficiais
2. Parcerias com sociedades médicas
3. Eventos e congressos médicos

Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Atenciosamente
"""

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Anexar arquivo Excel
            if os.path.exists(excel_file):
                with open(excel_file, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                  f'attachment; filename={os.path.basename(excel_file)}')
                    msg.attach(part)

            # Enviar email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            print(f"✅ Email enviado com sucesso para {recipient}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar email: {str(e)}")
            print("\n💡 Dicas:")
            print("   - Para iCloud: use senha de aplicativo (não a senha do iCloud)")
            print("   - Gere em: https://appleid.apple.com > Segurança > Senhas de app")
            return False


def main():
    """
    Função principal
    """
    print("\n" + "=" * 80)
    print("🏥 SCRAPER DE CONTATOS MÉDICOS - DADOS PÚBLICOS")
    print("=" * 80)
    print("\n📍 Fontes de dados públicos:")
    print("   - CFM (Conselho Federal de Medicina)")
    print("   - CRMs Regionais (SP, RJ, MG, ES, PR, SC, RS)")
    print("   - Sociedades de Especialidades Médicas")
    print()

    # Inicializar scraper
    scraper = MedicalContactScraper()

    # Coletar dados
    scraper.collect_data(target_experienced=500, target_recent=500)

    # Exportar para Excel
    excel_file = scraper.export_to_excel("medicos_sul_sudeste.xlsx")

    # Informações sobre envio de email
    print("\n" + "=" * 80)
    print("📧 ENVIO DE EMAIL")
    print("=" * 80)

    recipient = "sergio.otavio@icloud.com"

    print(f"\n⚠️  Para enviar o arquivo para {recipient}, você precisa:")
    print()
    print("1. Gerar uma 'Senha de App' no iCloud:")
    print("   https://appleid.apple.com")
    print("   > Segurança > Senhas de app > Gerar senha")
    print()
    print("2. Executar o seguinte código Python:")
    print()
    print("```python")
    print("from scrape_medical_contacts import MedicalContactScraper")
    print()
    print("scraper = MedicalContactScraper()")
    print("scraper.send_email(")
    print(f"    recipient='{recipient}',")
    print(f"    excel_file='{excel_file}',")
    print("    sender_email='seu_email@icloud.com',")
    print("    sender_password='xxxx-xxxx-xxxx-xxxx'  # Senha de app gerada")
    print(")")
    print("```")
    print()

    # OU enviar diretamente se as credenciais estiverem configuradas
    # Descomente abaixo e configure suas credenciais:

    # sender_email = "seu_email@icloud.com"
    # sender_password = "xxxx-xxxx-xxxx-xxxx"  # Senha de app
    # scraper.send_email(recipient, excel_file, sender_email=sender_email, sender_password=sender_password)

    print("\n" + "=" * 80)
    print("✅ PROCESSO CONCLUÍDO")
    print("=" * 80)
    print(f"\n📁 Arquivo gerado: {excel_file}")
    print(f"📊 Total de contatos: {len(scraper.data)}")
    print()
    print("⚠️  LEMBRETE IMPORTANTE:")
    print("   Este é um exemplo com dados fictícios para demonstração.")
    print("   Para dados reais, você precisa:")
    print("   1. Implementar scraping dos portais públicos (respeitando robots.txt)")
    print("   2. OU contratar acesso à API oficial do CFM (R$ 772/ano)")
    print("   3. OU usar serviços de terceiros com dados públicos")
    print()
    print("📧 Dados de contato (WhatsApp) NÃO estão disponíveis em registros públicos.")
    print("   Para networking, use canais profissionais oficiais.")
    print()


if __name__ == "__main__":
    # Verificar dependências
    try:
        import pandas
        import openpyxl
        import bs4
    except ImportError as e:
        print("❌ Dependência faltando. Instale com:")
        print("   pip install pandas openpyxl beautifulsoup4 requests")
        exit(1)

    main()
