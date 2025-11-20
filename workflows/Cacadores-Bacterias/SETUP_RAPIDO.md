# 🚀 SETUP RÁPIDO - Sistema Caçadores + Bactérias

Guia passo-a-passo para colocar o sistema funcionando em **menos de 1 hora**.

---

## 📋 CHECKLIST RÁPIDA

- [ ] **Passo 1:** Criar contas e APIs necessárias (15 min)
- [ ] **Passo 2:** Configurar Notion Databases (20 min)
- [ ] **Passo 3:** Importar workflows para n8n (10 min)
- [ ] **Passo 4:** Configurar variáveis de ambiente (10 min)
- [ ] **Passo 5:** TESTE PRÁTICO - Primeira execução (5 min)

---

## 🔧 PASSO 1: Criar Contas e APIs (15 min)

### 1.1 Anthropic Claude API

```bash
# Acesse: https://console.anthropic.com/
# 1. Criar conta (se não tiver)
# 2. Settings → API Keys
# 3. Create Key
# 4. Copiar: sk-ant-api03-xxxxx
```

**💰 Custo estimado:** ~$5-10/mês (uso moderado)

### 1.2 Notion Integration

```bash
# Acesse: https://www.notion.so/my-integrations
# 1. New integration
# 2. Nome: "Sistema Caçadores Bactérias"
# 3. Copiar: Internal Integration Token
# 4. Capabilities: Read content, Update content, Insert content
```

### 1.3 n8n Instance

**Opção A - Cloud (Recomendado para testes):**
```bash
# https://n8n.io/pricing
# Free tier: 5 workflows ativos
# Perfect para começar
```

**Opção B - Self-hosted (Docker):**
```bash
docker run -d --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 1.4 Slack (Opcional mas recomendado)

```bash
# https://api.slack.com/apps
# 1. Create New App
# 2. OAuth & Permissions → Bot Token Scopes:
#    - chat:write
#    - channels:read
# 3. Install to Workspace
# 4. Copiar: Bot User OAuth Token
```

### 1.5 Google Drive (Opcional)

```bash
# Para armazenar contexto de negócio
# Google Cloud Console → Enable Drive API
# Criar OAuth 2.0 credentials
```

---

## 📊 PASSO 2: Configurar Notion Databases (20 min)

### 2.1 Criar Workspace

1. Abra Notion
2. Crie nova página: **"🦠 Sistema Caçadores + Bactérias"**
3. Adicione ícone: 🦠

### 2.2 Database #1: REGISTRO_DEFEITOS

**Criar database:**
```
/table → Full page
Nome: 🔍 REGISTRO_DEFEITOS
```

**Propriedades (copie exatamente):**

| Nome da Propriedade | Tipo | Configuração |
|---------------------|------|--------------|
| ID | Title | (padrão) |
| Categoria | Select | MODELO_NEGOCIO, PRODUTO_COMUNIDADE, CULTURA_EXECUCAO, EFEITO_COLATERAL |
| Caçador | Select | CAÇADOR #1, CAÇADOR #2, CAÇADOR #3 |
| Severidade | Select | CRÍTICA, ALTA, MÉDIA |
| Defeito | Text | (padrão) |
| Probabilidade Colapso % | Number | Format: Percent |
| Prazo Morte (meses) | Number | (padrão) |
| Análise Completa | Text | Long text |
| Status | Select | AGUARDANDO_BACTERIAS, EM_REPARO, VALIDADO, REJEITADO |
| Data Detecção | Date | (padrão) |
| Bactérias Ativadas Em | Date | (padrão) |
| Total Ações Criadas | Number | (padrão) |
| Prioridade Atribuída | Select | P1, P2, P3 |

**⚡ ATALHO:** Use o template no arquivo `NOTION_SETUP.md` para copiar a estrutura completa.

### 2.3 Database #2: PLANOS_REPARO

**Criar database:**
```
/table → Full page
Nome: 🦠 PLANOS_REPARO
```

**Propriedades:**

| Nome | Tipo | Config |
|------|------|--------|
| ID Reparo | Title | - |
| Defeito Origem | Relation | → REGISTRO_DEFEITOS |
| Categoria | Rollup | From: Defeito Origem → Categoria |
| Prioridade | Select | P1 (0-3m), P2 (3-12m), P3 (12m+) |
| Score Letalidade | Number | 0-10 |
| Ação | Text | - |
| Prazo (dias) | Number | - |
| Data Limite | Date | - |
| Responsável | Person | - |
| Resultado Esperado | Text | - |
| Métrica Sucesso | Text | - |
| Critério Sucesso | Text | - |
| Status | Select | PENDENTE, EM_EXECUÇÃO, CONCLUÍDO, VALIDADO, REJEITADO |
| Validado Em | Date | - |
| Rejeitado Em | Date | - |
| Motivo Rejeição | Text | - |

### 2.4 Database #3: EVOLUÇÃO_TAXA_ERRO

**Criar database:**
```
/table → Full page
Nome: 📈 EVOLUÇÃO_TAXA_ERRO
```

**Propriedades:**

| Nome | Tipo | Config |
|------|------|--------|
| Período | Title | - |
| Taxa Erro Atual | Number | - |
| Taxa Erro Anterior | Number | - |
| Melhoria % | Formula | `((prop("Taxa Erro Anterior") - prop("Taxa Erro Atual")) / prop("Taxa Erro Anterior")) * 100` |
| Status Evolução | Select | 📈 EVOLUINDO, ➡️ ESTAGNADO, 📉 REGREDINDO |
| Total Histórico | Number | - |
| Última Atualização | Date | - |

### 2.5 Compartilhar com Integração

**IMPORTANTE:** Conecte cada database com a integração:

1. Abra cada database
2. `⋯` (três pontos) → **Add connections**
3. Selecione **"Sistema Caçadores Bactérias"**
4. ✅ Conexão estabelecida

### 2.6 Copiar IDs das Databases

```bash
# Para cada database, copie o ID da URL:
# https://notion.so/[WORKSPACE]/[DATABASE_ID]?v=...
#                              ^^^^^^^^^^^^^^^^
#                              Este é o ID!

# Exemplo:
# URL: https://notion.so/myworkspace/a1b2c3d4e5f6?v=...
# ID:  a1b2c3d4e5f6
```

**Salve os IDs:**
- `REGISTRO_DEFEITOS`: ________________
- `PLANOS_REPARO`: ________________
- `EVOLUÇÃO_TAXA_ERRO`: ________________

---

## 🔄 PASSO 3: Importar Workflows N8N (10 min)

### 3.1 Acesse n8n

```bash
# Cloud: https://app.n8n.cloud
# Self-hosted: http://localhost:5678
```

### 3.2 Importar os 3 Workflows

**Para cada workflow:**

1. **Workflows** → **Import from File**
2. Selecione o arquivo:
   - `01_cacadores_detector_fragilidades.json`
   - `02_bacterias_obsessao_reparo.json`
   - `03_validacao_loop_infinito.json`
3. Clique **Import**

### 3.3 Verificar Importação

Você deve ver 3 workflows na lista:

```
✅ 🔍 CAÇADORES - Detector de Fragilidades Mortais
✅ 🦠 BACTÉRIAS - Obsessão por Reparo
✅ ♻️ VALIDAÇÃO - Loop Infinito de Melhoria
```

**🚨 NÃO ATIVE AINDA!** Precisamos configurar credenciais primeiro.

---

## ⚙️ PASSO 4: Configurar Variáveis de Ambiente (10 min)

### 4.1 Criar Credenciais no n8n

**Settings** → **Credentials** → **New**

#### Anthropic API

```
Type: HTTP Header Auth
Name: Anthropic API
Header Name: x-api-key
Header Value: sk-ant-api03-xxxxx (sua chave)
```

#### Notion API

```
Type: Notion API
Name: Notion Admin
API Key: secret_xxxxx (seu token)
```

#### Slack (opcional)

```
Type: Slack OAuth2 API
Name: Slack Admin
OAuth2: (seguir wizard de autenticação)
```

#### Google Drive (opcional)

```
Type: Google Drive OAuth2 API
Name: Google Drive Admin
OAuth2: (seguir wizard)
```

### 4.2 Configurar Variáveis de Ambiente

**Settings** → **Environments** → **Variables**

Adicione:

```env
# Notion IDs
NOTION_DATABASE_DEFEITOS=a1b2c3d4e5f6
NOTION_DATABASE_REPAROS=x1y2z3w4v5u6
NOTION_DATABASE_EVOLUCAO=m1n2o3p4q5r6
NOTION_DASHBOARD_PAGE_ID=k1l2m3n4o5p6

# Notion URLs (para notificações)
NOTION_DEFEITOS_URL=https://notion.so/your-workspace/a1b2c3d4e5f6
NOTION_REPAROS_URL=https://notion.so/your-workspace/x1y2z3w4v5u6
NOTION_DASHBOARD_URL=https://notion.so/your-workspace/k1l2m3n4o5p6

# Google Drive (opcional)
GDRIVE_MODELO_NEGOCIO_ID=1ABC123xyz

# Slack Channels (opcional)
SLACK_CHANNEL_CACADORES=C01234567
SLACK_CHANNEL_BACTERIAS=C98765432
SLACK_CHANNEL_VALIDACAO=C11111111

# Webhook URLs
N8N_WEBHOOK_BACTERIAS_URL=https://sua-instancia.n8n.cloud/webhook/bacterias-ativacao
```

### 4.3 Configurar Webhook URL

1. Abra workflow **"🦠 BACTÉRIAS"**
2. Clique no node **"🔗 Webhook Ativação BACTÉRIAS"**
3. Copie a URL que aparece (Production URL)
4. Cole em `N8N_WEBHOOK_BACTERIAS_URL`

---

## 🧪 PASSO 5: TESTE PRÁTICO - Primeira Execução (5 min)

### 5.1 Teste Manual - Workflow CAÇADORES

**Este é o teste mais importante!**

#### Preparar dados de teste

1. Crie um documento no Google Drive (ou Notion) com contexto fictício:

```markdown
# CONTEXTO DE NEGÓCIO - TESTE

## Modelo de Negócio
- Startup SaaS B2B
- CAC atual: $500
- LTV: $1200
- Margem: 35%
- Crescimento: 20% MoM
- 90% receita vem de tráfego pago

## Comunidade
- Newsletter: 0 inscritos
- LinkedIn: 120 seguidores
- Comunidade própria: não existe

## Cultura
- Time celebrando milestone de 100 clientes
- Última análise de risco: há 3 meses
- Foco total em features do produto
```

2. Copie o ID do documento e adicione em `GDRIVE_MODELO_NEGOCIO_ID`

#### Executar teste

1. Abra workflow **"🔍 CAÇADORES"**
2. Clique **"Execute Workflow"** (botão no canto superior direito)
3. Aguarde... ⏳ (pode demorar 30-60s)

#### Verificar resultados

**✅ Sucesso se você ver:**

1. **No n8n:** Workflow completou sem erros (nodes verdes)
2. **No Notion (REGISTRO_DEFEITOS):** 3 novas linhas criadas
   - CAÇADOR #1: defeito no modelo de negócio
   - CAÇADOR #2: inversão produto vs comunidade
   - CAÇADOR #3: cultura medíocre
3. **No Slack (opcional):** Notificação de caçada concluída

**❌ Erro comum:**

```
Error: Missing required field 'Análise Completa'
```

**Solução:** Verifique se a propriedade no Notion tem exatamente o mesmo nome (incluindo acentos).

### 5.2 Teste Manual - Workflow BACTÉRIAS

1. No Notion, abra **REGISTRO_DEFEITOS**
2. Clique em um dos defeitos criados
3. Verifique que Status = **AGUARDANDO_BACTERIAS**
4. Abra workflow **"🦠 BACTÉRIAS"** no n8n
5. Clique no node **"🔗 Webhook"**
6. Clique em **"Test URL"** para gerar URL de teste
7. Use Postman/curl para chamar o webhook:

```bash
curl -X POST https://sua-instancia.n8n.cloud/webhook-test/bacterias-ativacao \
  -H "Content-Type: application/json" \
  -d '{
    "defeitos": [],
    "total": 3,
    "timestamp": "2025-01-15T10:00:00Z"
  }'
```

**✅ Sucesso se você ver:**

1. Workflow executou
2. **PLANOS_REPARO** tem novas tarefas criadas
3. Cada tarefa tem:
   - Ação específica
   - Prazo em dias
   - Métrica de sucesso
   - Prioridade (P1/P2/P3)
4. Defeito mudou status para **EM_REPARO**

### 5.3 Teste Manual - Workflow VALIDAÇÃO

1. No **PLANOS_REPARO**, mude status de uma tarefa para **CONCLUÍDO**
2. Abra workflow **"♻️ VALIDAÇÃO"**
3. Execute manualmente
4. Aguarde validação do Claude

**✅ Sucesso se você ver:**

1. Tarefa foi analisada
2. Status mudou para **VALIDADO** ou **REJEITADO**
3. Se rejeitado → novo ciclo de bactérias
4. **EVOLUÇÃO_TAXA_ERRO** foi atualizada

---

## ✅ ATIVAR SISTEMA COMPLETO

**Depois que todos os testes passarem:**

1. Abra cada workflow
2. **Toggle "Active"** (botão no canto superior direito)
3. ✅ Verde = workflow ativo

**Agendamento automático:**

- **CAÇADORES:** Roda a cada 6 horas
- **BACTÉRIAS:** Webhook (ativado pelos Caçadores)
- **VALIDAÇÃO:** Roda toda segunda-feira 9am

---

## 🎯 COMO TESTAR NA PRÁTICA (RESPOSTA DIRETA)

### TESTE RÁPIDO EM 5 MINUTOS

**1. Prepare contexto real do seu negócio:**

Crie um documento com:
- Métricas atuais (CAC, margem, crescimento)
- Tamanho da comunidade
- Últimas decisões estratégicas

**2. Execute workflow CAÇADORES manualmente:**
- Verifica se Claude detecta vulnerabilidades reais
- Analisa se os defeitos fazem sentido

**3. Leia os defeitos no Notion:**
- São brutalmente honestos?
- Batem com suas preocupações reais?
- Te deixaram desconfortável? ✅ FUNCIONOU!

**4. Deixe o sistema rodar por 1 semana:**
- Segunda-feira: Caçadores detectam defeitos
- Terça: Bactérias criam planos de reparo
- Você executa as ações sugeridas
- Sexta: Validação verifica se funcionou

**5. Olhe a métrica "ERRAR CADA VEZ MENOS":**
- Está diminuindo? ✅ Sistema funcionando
- Aumentando? 🔴 Você está ignorando os avisos

---

## 🚨 TROUBLESHOOTING COMUM

### Erro: "Database not found"

**Causa:** Notion integration não tem acesso
**Solução:** Compartilhe database com integração

### Erro: "Anthropic API rate limit"

**Causa:** Muitas chamadas em pouco tempo
**Solução:** Adicione delay entre nodes ou upgrade do plano

### Workflow não executa automaticamente

**Causa:** Trigger não configurado
**Solução:** Verifique se workflow está **Active** (verde)

### Claude retorna erro 400

**Causa:** Prompt muito longo ou formato inválido
**Solução:** Reduza tamanho do contexto de negócio

---

## 📖 PRÓXIMOS PASSOS

1. **Customize os prompts dos Caçadores:** Adapte para seu setor/nicho
2. **Ajuste frequência:** 6h pode ser muito/pouco para você
3. **Integre com seu dashboard:** Use API do Notion para visualizar métricas
4. **Adicione mais Caçadores:** Crie CAÇADOR #4 para finanças, #5 para vendas, etc.
5. **Gamifique:** Recompense quem mais "caça" e "repara" defeitos

---

## 💬 DÚVIDAS?

**Problema com setup:**
- Consulte `NOTION_SETUP.md` para detalhes das databases
- Veja `README.md` para visão geral do sistema

**Quer customizar:**
- Edite os prompts diretamente nos nodes HTTP Request
- Ajuste lógica JavaScript nos nodes Code

**Sistema não detecta seus defeitos reais:**
- Forneça mais contexto no documento de negócio
- Seja mais específico nas métricas

---

**🔥 MANTRA DO SISTEMA:**

> **"Pensamento positivo é lixo. Caçamos defeitos para nunca mais errar."**

Agora vai lá e **CONSTRÓI ESSA PORRA**! 💪
