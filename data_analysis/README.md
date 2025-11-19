# 📊 Plantões App - Análise de Dados e Blueprint

Este módulo contém toda a infraestrutura de análise de dados e geração de documentação estratégica para o **plantoes.app** - plataforma de gestão inteligente de plantões médicos.

## 🎯 O que este módulo faz?

Gera automaticamente um **workbook Excel completo** contendo:

- **18 abas de dados estruturados** (visão, personas, KPIs, roadmap, etc.)
- **Dashboard executivo** com métricas-chave e gráficos
- **Formatação condicional** para análise visual rápida
- **Gráficos automatizados** (Leads, Conversão, MRR, Funil)

## 📁 Estrutura do Projeto

```
data_analysis/
├── config.py              # Configurações e constantes
├── data_generator.py      # Geração de dados estruturados
├── chart_generator.py     # Criação de gráficos
├── excel_exporter.py      # Export para Excel com formatação
├── main.py                # Script principal
├── requirements.txt       # Dependências Python
├── README.md              # Esta documentação
│
├── output/                # Arquivos gerados
│   ├── Plantoes_App_Blueprint.xlsx
│   ├── chart_leads_por_canal.png
│   ├── chart_cvr_lead_trial.png
│   ├── chart_mrr_trend.png
│   └── chart_funnel.png
│
├── data/                  # Dados brutos (opcional)
├── notebooks/             # Jupyter notebooks para análises
└── reports/               # Relatórios customizados
```

## 🚀 Como Usar

### 1. Instalação

```bash
# Navegue até o diretório
cd data_analysis

# Instale as dependências
pip install -r requirements.txt
```

### 2. Execução Básica

```bash
# Gera o blueprint completo
python main.py
```

O arquivo `Plantoes_App_Blueprint.xlsx` será criado na pasta `output/`

### 3. Opções Avançadas

```bash
# Especificar caminho de saída personalizado
python main.py --output /caminho/customizado/meu_blueprint.xlsx

# Ver versão
python main.py --version

# Ajuda
python main.py --help
```

## 📊 Conteúdo Gerado

### Abas do Excel

| Aba | Conteúdo | Descrição |
|-----|----------|-----------|
| **00_Dashboard** | Dashboard executivo | KPIs principais + 4 gráficos |
| **01_Visao** | Visão do produto | Visão, missão, princípios |
| **02_Personas** | Personas de usuário | Médicos, coordenadores, RH, diretoria |
| **03_JTBD** | Jobs To Be Done | Tarefas-chave dos usuários |
| **04_ValueProp** | Value Proposition Canvas | Dores, ganhos, aliviadores |
| **05_Modulos** | Módulos da aplicação | 10 módulos com UX/fricção |
| **06_UseCases** | Casos de uso | 5 use cases principais |
| **07_LeadMagnets** | Iscas de lead generation | Conversão estimada |
| **08_Events** | Taxonomia de eventos | Analytics e tracking |
| **09_KPIs** | KPIs e OKRs | Metas mensuráveis |
| **10_Precos** | Pricing | 4 planos (Free → Enterprise) |
| **11_Automacoes** | Fluxo WhatsApp → Sheets | Automação por voz |
| **12_Dados** | Modelo de dados | Entidades e LGPD |
| **13_Compliance** | Compliance LGPD | Segurança e governança |
| **14_Pitch** | Sales pitch | Problema/solução/tração |
| **15_Roadmap** | Roadmap do produto | MVP/V1/V2 |
| **16_Testes** | Plano de testes A/B | Hipóteses e métricas |
| **17_Relatorio** | Dados históricos | 4 meses de métricas |
| **18_DashboardSrc** | Fonte do dashboard | Dados de canais |

### Gráficos Incluídos

1. **Leads por Canal** - Distribuição de leads por origem
2. **Conversão Lead→Trial** - Taxa de conversão por canal
3. **Evolução do MRR** - Tendência de receita recorrente
4. **Funil de Conversão** - Leads → Trials → Pagos

## 🔧 Arquitetura Modular

O código foi organizado em módulos independentes:

### `config.py`
- Configurações centralizadas
- Constantes reutilizáveis
- Funções auxiliares (paths, timestamps)

### `data_generator.py`
- 18 funções para gerar DataFrames
- Dados estruturados e validados
- Fácil manutenção e extensão

### `chart_generator.py`
- 4 funções de visualização
- Gráficos padronizados e profissionais
- Export para PNG em alta resolução

### `excel_exporter.py`
- Classe `ExcelExporter` com context manager
- Formatação condicional automática
- Dashboard com inserção de imagens

### `main.py`
- Script principal orquestrador
- CLI com argparse
- Tratamento de erros robusto

## 💡 Casos de Uso

### 1. Apresentação para Investidores
```bash
python main.py --output pitch_investidores_2025.xlsx
```

### 2. Planejamento Trimestral
Edite os dados em `data_generator.py` e regenere:
```bash
python main.py
```

### 3. Análise Personalizada
Use Jupyter notebooks na pasta `notebooks/`:
```python
from data_generator import generate_all_data
from chart_generator import create_leads_by_channel_chart

data = generate_all_data()
# Suas análises customizadas aqui
```

### 4. Integração com CI/CD
```yaml
# .github/workflows/generate-blueprint.yml
- name: Generate Blueprint
  run: |
    cd data_analysis
    python main.py --output ../artifacts/blueprint.xlsx
```

## 🎨 Personalizações

### Alterar Cores dos Gráficos
Edite `chart_generator.py`:
```python
plt.bar(..., color='#4A90E2')  # Altere a cor aqui
```

### Adicionar Novos KPIs
1. Adicione função em `data_generator.py`
2. Atualize `excel_exporter.py` para incluir nova aba
3. Execute `python main.py`

### Customizar Formatação Excel
Edite `config.py`:
```python
EXCEL_FORMATS = {
    "header": {"bold": True, "bg_color": "#SUA_COR"},
    # ...
}
```

## 📝 Melhorias em Relação ao Código Original

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Organização** | 1 arquivo monolítico | 5 módulos especializados |
| **Reutilização** | Código duplicado | Funções reutilizáveis |
| **Manutenção** | Difícil localizar mudanças | Módulos independentes |
| **Testabilidade** | Não testável | Funções unitárias |
| **Configuração** | Hardcoded | Centralized config |
| **Documentação** | Mínima | Completa com exemplos |
| **CLI** | Não disponível | Argparse completo |

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "Permission denied"
```bash
# Dê permissão de execução
chmod +x main.py
```

### Gráficos não aparecem
Certifique-se de que o matplotlib está instalado:
```bash
pip install matplotlib --upgrade
```

### Excel não abre
Verifique se tem espaço em disco e permissões na pasta `output/`

## 📚 Recursos Adicionais

- [Documentação pandas](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [XlsxWriter Examples](https://xlsxwriter.readthedocs.io/)

## 🤝 Contribuindo

Para adicionar novas funcionalidades:

1. Crie função geradora em `data_generator.py`
2. Adicione visualização em `chart_generator.py` (se necessário)
3. Atualize exportação em `excel_exporter.py`
4. Teste com `python main.py`
5. Documente no README

## 📜 Licença

Este código faz parte do projeto **ApoloCopilot** e segue a mesma licença do repositório principal.

## 👥 Autores

- **Equipe Plantões App** - Planejamento estratégico
- **Claude Code** - Modularização e infraestrutura

---

**plantoes.app** | contato@plantoes.app

Gerado com ❤️ para revolucionar a gestão de plantões médicos no Brasil.
