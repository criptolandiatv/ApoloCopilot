# 🏥 Medical Contacts Scraper - Dados Públicos

Script para coletar dados **públicos** de médicos dos portais oficiais do CFM/CRM e sociedades médicas.

## ⚠️ IMPORTANTE - Limitações Legais

### ✅ O que este script FAZ:
- Coleta dados PÚBLICOS disponíveis nos portais oficiais (CFM/CRM)
- Informações: Nome, CRM, UF, Especialidade, Ano de Formação
- Filtra por especialidades médicas (cirurgiões, especialistas)
- Filtra por região (Sul e Sudeste: SP, RJ, MG, ES, PR, SC, RS)
- Exporta para planilha Excel organizada

### ❌ O que este script NÃO FAZ:
- **NÃO coleta números de WhatsApp** (não disponível em registros públicos)
- **NÃO coleta telefones pessoais** (dado privado)
- **NÃO coleta emails pessoais** (dado privado)
- **NÃO estima renda/faturamento** (dado não público)

### 📋 Dados Disponíveis Publicamente:
Os portais oficiais do CFM/CRM disponibilizam:
- Nome completo do médico
- Número CRM e UF
- Especialidade(s) registrada(s)
- Situação do registro (ativo/inativo)
- Endereço comercial (quando autorizado pelo médico)

## 🎯 Fontes de Dados Públicos

1. **CFM (Conselho Federal de Medicina)**
   - Portal: https://portal.cfm.org.br/busca-medicos/
   - API Oficial: https://crmvirtual.cfm.org.br/BR/servico/web-service---listagem-de-medicos
   - Custo API: R$ 772/ano (empresas privadas) | Gratuito (órgãos públicos)

2. **CRMs Regionais**
   - CREMESP (SP): https://guiamedico.cremesp.org.br/
   - CREMERJ (RJ): https://portal.cremerj.org.br/
   - CRM-MG, CRM-PR, CRM-SC, CRM-RS, CRM-ES: portais regionais

3. **Sociedades de Especialidades**
   - Sociedade Brasileira de Cirurgia Geral
   - Sociedades de especialidades médicas específicas

## 🚀 Instalação

### Requisitos:
```bash
Python 3.7+
pip install pandas openpyxl beautifulsoup4 requests
```

### Instalação de dependências:
```bash
pip install -r requirements.txt
```

## 📖 Uso

### 1. Execução Básica (Modo Demonstração)

```bash
python scrape_medical_contacts.py
```

Este comando:
- Gera 1000 registros de exemplo (500 experientes + 500 recém-formados)
- Cria arquivo `medicos_sul_sudeste.xlsx`
- Organiza em 3 abas: Experientes, Recém-formados, Todos

### 2. Uso Programático

```python
from scrape_medical_contacts import MedicalContactScraper

# Criar instância
scraper = MedicalContactScraper()

# Coletar dados
scraper.collect_data(
    target_experienced=500,  # Médicos experientes
    target_recent=500        # Médicos recém-formados
)

# Exportar para Excel
excel_file = scraper.export_to_excel("medicos_sul_sudeste.xlsx")

# Enviar por email
scraper.send_email(
    recipient='sergio.otavio@icloud.com',
    excel_file=excel_file,
    sender_email='seu_email@icloud.com',
    sender_password='xxxx-xxxx-xxxx-xxxx'  # Senha de app
)
```

## 📧 Envio de Email

### Para enviar para iCloud (sergio.otavio@icloud.com):

1. **Gerar Senha de App no iCloud:**
   - Acesse: https://appleid.apple.com
   - Vá em: Segurança > Senhas de app
   - Clique em "Gerar senha"
   - Copie a senha gerada (formato: xxxx-xxxx-xxxx-xxxx)

2. **Configurar e enviar:**
```python
from scrape_medical_contacts import MedicalContactScraper

scraper = MedicalContactScraper()
scraper.send_email(
    recipient='sergio.otavio@icloud.com',
    excel_file='medicos_sul_sudeste.xlsx',
    sender_email='seu_email@icloud.com',
    sender_password='xxxx-xxxx-xxxx-xxxx'  # Senha de app
)
```

## 📊 Estrutura do Arquivo Excel

O arquivo gerado contém 3 abas:

### Aba 1: Médicos Experientes
- Médicos formados entre 1990-2015
- Cirurgiões gerais e especialistas
- Foco em profissionais estabelecidos

### Aba 2: Médicos Recém-formados
- Médicos formados entre 2020-2024
- Todas especialidades
- Profissionais em início de carreira

### Aba 3: Todos
- Compilação completa de todos os registros

### Campos incluídos:
| Campo | Descrição |
|-------|-----------|
| nome | Nome completo do médico |
| crm | Número CRM/UF |
| uf | Estado |
| especialidade | Especialidade médica |
| ano_formacao | Ano de formação |
| categoria | Experiente / Recém-formado |
| endereco_comercial | Endereço profissional (quando disponível) |
| fonte | Fonte dos dados |
| data_coleta | Data/hora da coleta |

## 🔧 Implementação Real vs Demonstração

### Modo Atual: DEMONSTRAÇÃO
- Gera dados fictícios para teste
- Estrutura completa implementada
- Pronto para integração com fontes reais

### Para Implementação Real:

Você tem 3 opções:

#### Opção 1: API Oficial do CFM (Recomendado)
- **Custo:** R$ 772/ano (empresas privadas)
- **Vantagens:** Dados oficiais, atualizados diariamente, suporte
- **Como:** Registrar em https://crmvirtual.cfm.org.br/BR/servico/web-service---listagem-de-medicos

#### Opção 2: Scraping dos Portais Públicos
- **Custo:** Gratuito
- **Requisitos:**
  - Respeitar robots.txt
  - Implementar delays entre requests
  - Rate limiting apropriado
- **Como:** Implementar métodos `search_cfm_portal()`, `search_cremesp()`, etc.

#### Opção 3: Serviços de Terceiros
- Plataformas como Infosimples, ConsultaCRM
- Custos variáveis por consulta

## 🎯 Especialidades Cobertas

### Cirurgias:
- Cirurgia Geral
- Cirurgia Plástica
- Cirurgia Cardiovascular
- Cirurgia Torácica
- Cirurgia Vascular
- Cirurgia de Cabeça e Pescoço
- Cirurgia do Aparelho Digestivo
- Cirurgia Pediátrica
- Neurocirurgia

### Regiões:
- **Sudeste:** SP, RJ, MG, ES
- **Sul:** PR, SC, RS

## 📱 Sobre Contatos de WhatsApp

### Por que WhatsApp não está incluído?

1. **Não é dado público:** Números de WhatsApp não constam nos registros públicos do CFM/CRM
2. **LGPD:** Coletar contatos pessoais sem consentimento viola a Lei Geral de Proteção de Dados
3. **Ética profissional:** Médicos têm direito à privacidade de contatos pessoais

### Alternativas Legais para Contato:

#### Para Networking e Convites para Eventos:

1. **Canais Profissionais:**
   - LinkedIn (perfis profissionais)
   - Sociedades de especialidades médicas
   - Associações médicas regionais

2. **Marketing Ético:**
   - Anúncios segmentados em plataformas profissionais
   - Parcerias com entidades médicas
   - Participação em congressos e eventos

3. **Endereços Comerciais:**
   - Alguns médicos autorizam divulgação de endereço de consultório
   - Pode ser usado para correspondência profissional (convites físicos)

4. **Emails Profissionais:**
   - Muitos médicos disponibilizam email profissional em sites de clínicas
   - Plataformas como Doctoralia, Consulta do Bem

## 🤝 Uso Ético dos Dados

### ✅ Usos Apropriados:
- Envio de convites para fóruns médicos
- Networking profissional
- Divulgação de eventos científicos
- Envio de presentes corporativos de fim de ano (via endereço comercial)

### ❌ Usos Inapropriados:
- Spam ou comunicações não solicitadas
- Venda de listas de contatos
- Marketing agressivo
- Compartilhamento não autorizado de dados

### 📜 Boas Práticas:
1. Sempre oferecer opção de opt-out
2. Respeitar preferências de contato
3. Usar dados apenas para finalidades legítimas
4. Manter dados seguros e atualizados
5. Seguir as diretrizes da LGPD

## 🔒 Conformidade Legal

### LGPD (Lei Geral de Proteção de Dados):
- ✅ Dados públicos dos CRMs: permitido (base legal: exercício regular de direito)
- ✅ Dados de associações profissionais: permitido (com consentimento da associação)
- ❌ Scraping de dados privados: proibido sem consentimento

### Lei do Exercício da Medicina:
- Respeitar prerrogativas profissionais
- Não usar dados para fins que possam prejudicar a reputação profissional

## 📚 Referências

### Portais Oficiais:
- [Portal CFM](https://portal.cfm.org.br)
- [CFM Virtual - Web Service](https://crmvirtual.cfm.org.br/BR/servico/web-service---listagem-de-medicos)
- [CREMESP - Guia Médico](https://guiamedico.cremesp.org.br/)
- [Portal Transparência CFM](https://transparencia.cfm.org.br/)

### Legislação:
- [LGPD - Lei 13.709/2018](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Resolução CFM 2.129/15](https://sistemas.cfm.org.br/normas/visualizar/resolucoes/BR/2015/2129)

## 🆘 Suporte

### Problemas Comuns:

**1. Erro ao instalar dependências:**
```bash
pip install --upgrade pip
pip install pandas openpyxl beautifulsoup4 requests
```

**2. Erro ao enviar email:**
- Verifique se está usando senha de app (não a senha normal)
- Para iCloud: gere em https://appleid.apple.com

**3. Arquivo Excel não abre:**
- Instale/atualize o openpyxl: `pip install --upgrade openpyxl`

## 📝 Licença

Este script é fornecido para fins educacionais e de demonstração.
Uso de dados deve respeitar a LGPD e regulamentações aplicáveis.

## ⚖️ Disclaimer

Este script coleta apenas dados publicamente disponíveis nos portais oficiais.
O uso dos dados coletados é de responsabilidade do usuário e deve estar em
conformidade com a LGPD e demais legislações aplicáveis.

---

**Versão:** 1.0
**Data:** Dezembro 2024
**Autor:** ApoloCopilot Medical Data Team
