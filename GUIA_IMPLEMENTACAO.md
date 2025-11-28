# 🎼 Sistema Maestro n8n - Guia de Implementação Completo

> **Sistema inteligente de monitoramento e geração de workflows n8n resilientes**

Este guia vai te levar do zero até um sistema completo que:

1. 🔍 **Monitora** diariamente mudanças no ecossistema n8n
2. 📚 **Armazena** conhecimento destilado em uma base consultável por IA
3. 🎼 **Gera** workflows n8n de forma inteligente e à prova de futuro
4. 🎓 **Ensina** enquanto constrói, tornando você mais independente

---

## 📋 Índice

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Pré-requisitos](#pré-requisitos)
3. [Passo 1: Configurar Banco de Dados](#passo-1-configurar-banco-de-dados)
4. [Passo 2: Configurar Workflow Radar](#passo-2-configurar-workflow-radar)
5. [Passo 3: Configurar Maestro](#passo-3-configurar-maestro)
6. [Passo 4: Primeiro Uso](#passo-4-primeiro-uso)
7. [Manutenção e Monitoramento](#manutenção-e-monitoramento)
8. [Troubleshooting](#troubleshooting)
9. [Roadmap](#roadmap)

---

## 🏗️ Visão Geral do Sistema

### Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ECOSSISTEMA N8N                          │
│  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌──────────────┐  │
│  │   Docs   │  │ GitHub  │  │ Forum  │  │ Changelog    │  │
│  └────┬─────┘  └────┬────┘  └───┬────┘  └──────┬───────┘  │
└───────┼─────────────┼───────────┼───────────────┼──────────┘
        │             │           │               │
        └─────────────┴───────────┴───────────────┘
                          │
                    ┌─────▼──────┐
                    │   RADAR    │ ◄── Workflow n8n que roda diariamente
                    │    n8n     │     (workflows/radar-n8n-monitoring.json)
                    └─────┬──────┘
                          │
              ┌───────────┴───────────┐
              │                       │
        ┌─────▼──────┐         ┌──────▼─────┐
        │ n8n_updates│         │ n8n_knowledge│
        │  (tabela)  │────────►│   (vetorial) │
        └────────────┘         └──────┬───────┘
                                      │
                                      │ RAG (busca semântica)
                                      │
                                ┌─────▼──────┐
                                │  MAESTRO   │ ◄── Agente IA construtor
                                │    n8n     │     de workflows
                                └─────┬──────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                    ┌─────▼──────┐         ┌──────▼─────┐
                    │  Blueprint │         │  Workflow  │
                    │   (design) │────────►│    JSON    │
                    └────────────┘         └────────────┘
```

### Componentes

1. **Radar n8n** (`workflows/radar-n8n-monitoring.json`)
   - Workflow que roda diariamente
   - Coleta updates de docs, GitHub, fórum
   - Processa com LLM (resume, categoriza, extrai metadados)
   - Salva em `n8n_updates` e gera embeddings para `n8n_knowledge`

2. **Banco de Dados** (`database/schema.sql`)
   - `n8n_updates`: Updates brutos diários
   - `n8n_knowledge`: Base vetorial para RAG
   - `workflow_blueprints`: Blueprints gerados
   - `maestro_conversations`: Histórico de conversas
   - `radar_execution_log`: Log de execuções

3. **Maestro n8n** (`maestro/`)
   - `system-prompt.md`: Prompt de sistema do agente
   - `tools-definition.json`: Definição das ferramentas
   - `tools-implementation.py`: Implementação em Python
   - Agente IA que consulta a base antes de gerar workflows

---

## 🔧 Pré-requisitos

### 1. Serviços Necessários

- ✅ **n8n** (self-hosted ou cloud)
  - Versão: >= 1.0.0
  - [Como instalar](https://docs.n8n.io/hosting/)

- ✅ **Supabase** (ou Postgres com extensão `pgvector`)
  - [Criar conta grátis](https://supabase.com)
  - Plano Free já funciona para começar

- ✅ **OpenAI API**
  - Para embeddings (text-embedding-ada-002) e LLM (gpt-4o-mini)
  - [Obter API key](https://platform.openai.com/api-keys)

- ✅ **GitHub Token** (opcional, mas recomendado)
  - Para acessar API do GitHub sem rate limit
  - [Criar token](https://github.com/settings/tokens)

- ✅ **Telegram Bot** (opcional)
  - Para receber notificações diárias
  - [Criar bot](https://t.me/BotFather)

### 2. Ferramentas Locais (para usar o Maestro)

- Python >= 3.10
- pip (gerenciador de pacotes Python)

### 3. Estimativa de Custos

**Plano Mínimo (Free/quase free):**
- Supabase: Free tier (500MB storage, 2GB transfer/month)
- OpenAI: ~$2-5/mês (dependendo do volume)
- n8n: Self-hosted free ou Cloud starter $20/mês
- Total: **$2-25/mês**

**Plano Recomendado:**
- Supabase: Pro $25/mês (8GB storage, 250GB transfer)
- OpenAI: $10-20/mês
- n8n: Cloud Pro $50/mês
- Total: **$85-95/mês**

---

## 🗄️ Passo 1: Configurar Banco de Dados

### 1.1 Criar projeto no Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Crie uma conta (se não tiver)
3. Clique em **"New Project"**
4. Preencha:
   - **Name**: `n8n-maestro` (ou o que preferir)
   - **Database Password**: Anote essa senha! Você vai precisar
   - **Region**: Escolha a mais próxima de você
   - **Pricing Plan**: Free (para começar)

5. Aguarde 2-3 minutos até o projeto estar pronto

### 1.2 Ativar extensão pgvector

1. No dashboard do Supabase, vá em **Database** > **Extensions**
2. Procure por `vector`
3. Clique em **Enable** ao lado de `vector`

### 1.3 Executar schema SQL

1. No Supabase, vá em **SQL Editor**
2. Clique em **"New query"**
3. Copie todo o conteúdo de `database/schema.sql`
4. Cole no editor
5. Clique em **Run** (ou pressione Ctrl+Enter)

✅ **Resultado esperado:** Mensagem "Success. No rows returned"

Verifique que as tabelas foram criadas:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

Você deve ver:
- `n8n_updates`
- `n8n_knowledge`
- `workflow_blueprints`
- `maestro_conversations`
- `radar_execution_log`

### 1.4 Obter credenciais de conexão

1. No Supabase, vá em **Settings** > **API**
2. Anote:
   - **Project URL** (ex: `https://abc123.supabase.co`)
   - **Project API Key** (anon/public key)
   - **Service Role Key** (secret key - para operações admin)

3. Vá em **Settings** > **Database**
4. Anote:
   - **Host** (ex: `db.abc123.supabase.co`)
   - **Database name** (geralmente `postgres`)
   - **Port** (geralmente `5432`)
   - **User** (geralmente `postgres`)
   - **Password** (a que você definiu na criação)

---

## 🔍 Passo 2: Configurar Workflow Radar

### 2.1 Configurar credenciais no n8n

Antes de importar o workflow, você precisa criar as credenciais:

#### a) **OpenAI API**

1. No n8n, vá em **Settings** > **Credentials** > **Add Credential**
2. Procure por "OpenAI"
3. Clique em **OpenAI**
4. Preencha:
   - **Name**: `openai-api` (importante: use exatamente esse nome)
   - **API Key**: Sua chave da OpenAI
5. Clique em **Save**

#### b) **Postgres (Supabase)**

1. **Add Credential** > procure por "Postgres"
2. Preencha com os dados do Supabase (do passo 1.4):
   - **Name**: `supabase-postgres` (use exatamente esse nome)
   - **Host**: (do Supabase)
   - **Database**: `postgres`
   - **User**: `postgres`
   - **Password**: (do Supabase)
   - **Port**: `5432`
   - **SSL**: Ative (importante!)
3. Clique em **Test connection** (deve dar sucesso)
4. **Save**

#### c) **GitHub Token** (opcional)

1. **Add Credential** > procure por "HTTP Header Auth"
2. Preencha:
   - **Name**: `github-token`
   - **Name** (do header): `Authorization`
   - **Value**: `Bearer SEU_TOKEN_GITHUB`
3. **Save**

#### d) **Telegram Bot** (opcional)

1. **Add Credential** > procure por "Telegram"
2. Preencha:
   - **Name**: `telegram-bot`
   - **Access Token**: (do BotFather)
3. **Save**

### 2.2 Configurar variável de ambiente

Se você vai usar Telegram, adicione esta variável de ambiente no n8n:

```bash
TELEGRAM_CHAT_ID=seu_chat_id
```

Para descobrir seu chat_id:
1. Mande uma mensagem para o bot
2. Acesse: `https://api.telegram.org/botSEU_BOT_TOKEN/getUpdates`
3. Procure por `"chat":{"id":123456789}`

### 2.3 Importar workflow Radar

1. No n8n, vá em **Workflows**
2. Clique em **Import from File** (ou pressione Ctrl+O)
3. Selecione o arquivo `workflows/radar-n8n-monitoring.json`
4. Clique em **Import**

✅ **Resultado esperado:** Workflow "🔍 Radar n8n - Daily Monitoring" aparece

### 2.4 Testar workflow manualmente

1. Abra o workflow "Radar n8n"
2. Clique em **Test workflow** (botão de play no canto superior direito)
3. Observe a execução:
   - Verde: sucesso
   - Vermelho: erro (veja os logs)

**Primeira execução pode demorar 2-5 minutos** (vai processar muitos items)

### 2.5 Ativar execução diária

1. No workflow, vá em **Settings** (ícone de engrenagem)
2. Em "Workflow Settings":
   - **Active**: Ligue (toggle para ON)
   - **Timezone**: Escolha seu timezone
3. **Save**

Agora o workflow rodará automaticamente todo dia às 8h da manhã.

### 2.6 Verificar que funcionou

Vá no Supabase e rode:

```sql
-- Ver updates coletados
SELECT COUNT(*) FROM n8n_updates;

-- Ver conhecimento gerado
SELECT COUNT(*) FROM n8n_knowledge;

-- Ver últimas execuções
SELECT * FROM radar_execution_log ORDER BY executed_at DESC LIMIT 5;
```

Se tudo funcionou, você deve ver:
- `n8n_updates`: Pelo menos 10-50 registros
- `n8n_knowledge`: Pelo menos 10-50 registros
- `radar_execution_log`: 1 registro (a execução manual)

---

## 🎼 Passo 3: Configurar Maestro

### 3.1 Instalar dependências Python

```bash
cd maestro
pip install openai supabase pgvector python-dotenv
```

### 3.2 Criar arquivo .env

Crie um arquivo `.env` na pasta `maestro/`:

```bash
# Supabase
SUPABASE_URL=https://abc123.supabase.co
SUPABASE_KEY=sua_service_role_key_aqui

# OpenAI
OPENAI_API_KEY=sk-...

# Opcional: n8n (se quiser integrar)
N8N_API_URL=https://sua-instancia.n8n.cloud/api/v1
N8N_API_KEY=sua_api_key
```

⚠️ **Atenção:** Use a **Service Role Key** do Supabase (não a anon key), pois ela tem permissões de escrita.

### 3.3 Testar implementação das ferramentas

```bash
cd maestro
python tools-implementation.py
```

✅ **Resultado esperado:**
```
🔍 Teste 1: Buscar documentação sobre OpenAI node
  - OpenAI Node Configuration (similaridade: 0.85)
  - ...

🔍 Teste 2: Buscar best practices de error handling no fórum
  - ...

✅ Todos os testes concluídos!
```

Se der erro, verifique:
- `.env` está correto?
- Banco de dados tem dados (rodou o Radar pelo menos 1x)?
- Credenciais OpenAI e Supabase estão válidas?

### 3.4 Integrar Maestro com OpenAI/Claude

Agora você tem 2 opções de como usar o Maestro:

#### Opção A: Via OpenAI Assistant (recomendado)

1. Acesse [platform.openai.com/assistants](https://platform.openai.com/assistants)
2. Clique em **Create Assistant**
3. Preencha:
   - **Name**: `Maestro n8n`
   - **Instructions**: Cole o conteúdo de `maestro/system-prompt.md`
   - **Model**: `gpt-4o` (ou `gpt-4o-mini` para economia)
   - **Tools**: Adicione as ferramentas de `maestro/tools-definition.json`

4. **Como adicionar ferramentas:**
   - Copie cada objeto `function` de `tools-definition.json`
   - Em "Functions", clique em **Add Function**
   - Cole o JSON de cada função
   - Repita para todas as 9 ferramentas

5. **Save**

6. Agora você pode usar via:
   - Interface do OpenAI (Playground)
   - API do OpenAI (com `assistant_id`)
   - Integração com n8n (node OpenAI Assistant)

#### Opção B: Via API direta (mais flexível)

Crie um script Python `maestro/chat.py`:

```python
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools_implementation import *

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carregar system prompt
with open('system-prompt.md', 'r') as f:
    system_prompt = f.read()

# Carregar tools
with open('tools-definition.json', 'r') as f:
    tools_config = json.load(f)

# Mapear funções Python
tools_map = {
    'search_n8n_docs': search_n8n_docs,
    'search_n8n_forum': search_n8n_forum,
    'check_node_compatibility': check_node_compatibility,
    'suggest_workflow_structure': suggest_workflow_structure,
    'generate_n8n_json': generate_n8n_json,
    'validate_workflow_json': validate_workflow_json,
    'get_recent_n8n_changes': get_recent_n8n_changes,
    'save_blueprint': save_blueprint,
    'search_existing_blueprints': search_existing_blueprints
}

def chat_with_maestro(user_message):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools_config['tools']
        )

        message = response.choices[0].message
        messages.append(message)

        # Se não tem tool calls, retornar resposta
        if not message.tool_calls:
            return message.content

        # Executar tool calls
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"🔧 Executando: {function_name}({arguments})")

            # Executar função
            result = tools_map[function_name](**arguments)

            # Adicionar resultado às mensagens
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

if __name__ == "__main__":
    print("🎼 Maestro n8n - Chat Interface\n")

    while True:
        user_input = input("Você: ")
        if user_input.lower() in ['exit', 'quit', 'sair']:
            break

        response = chat_with_maestro(user_input)
        print(f"\nMaestro: {response}\n")
```

Usar:
```bash
python chat.py
```

---

## 🎯 Passo 4: Primeiro Uso

### 4.1 Exemplo: Criar workflow de transcrição

**Prompt para o Maestro:**

```
Quero criar um workflow que:

1. Recebe áudio via webhook (WhatsApp Business API)
2. Valida que o áudio não é maior que 15MB
3. Transcreve com OpenAI Whisper
4. Usa GPT-4 para gerar:
   - Thread (10 posts de Twitter/X)
   - 3 Stories
   - Resumo executivo
5. Salva tudo no Supabase (tabela 'content')
6. Me manda uma notificação no Telegram com os resultados

Restrições:
- Orçamento médio (não precisa ser ultra barato, mas sem exageros)
- Precisa ser resiliente (com error handling)
- Prefiro no-code quando possível
```

### 4.2 O que o Maestro vai fazer

**Fase 1 - Pesquisa (1-2 min)**
- Buscar docs sobre Webhook, Whisper, GPT-4
- Buscar no fórum padrões de transcription workflows
- Checar compatibilidade dos nodes

**Fase 2 - Blueprint (apresentação para você)**
```
## 📐 Blueprint: Conteúdo Diário PRO-CRIAR

### Objetivo
Receber áudio via WhatsApp, transcrever, gerar conteúdo multi-formato, e armazenar.

### Estrutura
1. **Webhook** - Receber áudio do WhatsApp
   - Por que: WhatsApp Business API usa webhooks
   - Ref: [n8n webhook docs]

2. **Code (Validação)** - Validar tamanho do áudio
   - Por que: Evitar timeout/custo com áudios grandes
   - Alternativa: Node IF simples (menos robusto)

3. **HTTP Request (Whisper)** - Transcrição
   - Por que: Mais estável que node OpenAI específico
   - Ref: [OpenAI Whisper API docs]

[... continua ...]

### ⚠️ Pontos de Atenção
- WhatsApp limita áudio a 16MB (já tratado na validação)
- Whisper timeout padrão é 30s → aumentar para 120s
- GPT-4 pode demorar 20-30s → adicionar timeout adequado

### 💡 Recomendações
- Adicionar retry com backoff exponencial em chamadas de API
- Logar erros no Supabase para debug posterior
- Considerar fallback para GPT-4o-mini se GPT-4 falhar

Posso prosseguir com esse blueprint?
```

**Você:** "Sim, pode prosseguir"

**Fase 3 - Geração do JSON (1-2 min)**
```
✅ Blueprint aprovado!

Gerando JSON do workflow...
Validando...

📦 Workflow pronto!

📄 Arquivo: conteudo-diario-pro-criar.json
🔑 Credenciais necessárias:
   1. OpenAI API - [Como configurar](...)
   2. Supabase - [Como configurar](...)
   3. Telegram Bot - [Como configurar](...)

📖 Próximos passos:
   1. Importar o JSON no n8n
   2. Configurar as credenciais acima
   3. Definir variável TELEGRAM_CHAT_ID
   4. Testar com áudio de exemplo

[Anexa arquivo JSON]
```

### 4.3 Importar e testar

1. Salve o JSON em um arquivo `.json`
2. Importe no n8n (Workflows > Import)
3. Configure credenciais conforme instruções
4. Teste manualmente com um áudio

---

## 📊 Manutenção e Monitoramento

### Monitorar saúde do Radar

**Query SQL útil:**

```sql
-- Estatísticas do Radar (últimos 30 dias)
SELECT * FROM get_radar_stats(30);

-- Últimas execuções com erros
SELECT * FROM radar_execution_log
WHERE status != 'success'
ORDER BY executed_at DESC
LIMIT 10;

-- Updates de alto impacto (últimos 7 dias)
SELECT title, category, impact_level, url, update_date
FROM n8n_updates
WHERE update_date >= CURRENT_DATE - INTERVAL '7 days'
  AND impact_level IN ('critical', 'high')
ORDER BY update_date DESC;

-- Knowledge mais usado
SELECT * FROM top_knowledge LIMIT 10;
```

### Dashboard no Supabase

Crie uma dashboard no Supabase com:

1. **Total de conhecimento**: `SELECT COUNT(*) FROM n8n_knowledge WHERE active = true`
2. **Updates/dia**: `SELECT COUNT(*) FROM n8n_updates GROUP BY update_date ORDER BY update_date DESC LIMIT 30`
3. **Taxa de sucesso do Radar**: `SELECT status, COUNT(*) FROM radar_execution_log GROUP BY status`
4. **Blueprints criados**: `SELECT category, COUNT(*) FROM workflow_blueprints GROUP BY category`

### Notificações de Breaking Changes

Adicione este workflow no n8n para ser alertado de breaking changes:

```json
{
  "name": "🚨 Alert: Breaking Changes",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
        }
      }
    },
    {
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT * FROM n8n_updates WHERE category = 'breaking_change' AND update_date >= CURRENT_DATE - INTERVAL '1 day'"
      }
    },
    {
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [{"value1": "={{ $json.length }}", "operation": "larger", "value2": 0}]
        }
      }
    },
    {
      "type": "n8n-nodes-base.telegram",
      "parameters": {
        "chatId": "{{ $env.TELEGRAM_CHAT_ID }}",
        "text": "🚨 BREAKING CHANGE detectado no n8n!\n\n{{ $json.title }}\n\n{{ $json.summary }}\n\n🔗 {{ $json.url }}"
      }
    }
  ]
}
```

---

## 🔧 Troubleshooting

### Problema: Radar não coleta nada

**Sintomas:** `n8n_updates` vazio após execução

**Possíveis causas:**
1. **APIs externas fora do ar:** Tente acessar manualmente:
   - https://docs.n8n.io
   - https://api.github.com/repos/n8n-io/n8n/releases
   - https://community.n8n.io/latest.json

2. **Rate limit do GitHub:** Se não tem token configurado, GitHub limita a 60 requests/hora
   - Solução: Configure o `github-token` nas credenciais

3. **Timeout nas chamadas HTTP:** Aumentar timeout nos nodes HTTP Request
   - Edite o workflow, em cada HTTP Request > Options > Timeout > 60000 (60s)

### Problema: Embeddings não estão sendo gerados

**Sintomas:** `n8n_knowledge` vazio mas `n8n_updates` tem dados

**Possíveis causas:**
1. **Cota OpenAI esgotada:** Verifique em https://platform.openai.com/usage
2. **Credencial OpenAI inválida:** Teste manualmente

**Solução:**
```bash
# Testar credencial OpenAI via curl
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "teste",
    "model": "text-embedding-ada-002"
  }'
```

### Problema: Maestro não encontra resultados relevantes

**Sintomas:** Busca retorna poucos resultados ou não relevantes

**Possíveis causas:**
1. **Base ainda pequena:** Espere alguns dias de coleta do Radar
2. **Embeddings de baixa qualidade:** LLM não resumiu bem

**Solução:**
- Rodar o Radar manualmente mais algumas vezes
- Verificar quality dos resumos em `n8n_updates`:
  ```sql
  SELECT title, summary FROM n8n_updates LIMIT 10;
  ```
- Se resumos estão ruins, ajustar prompt do LLM no workflow Radar

### Problema: Workflow gerado não importa no n8n

**Sintomas:** Erro ao importar JSON

**Possíveis causas:**
1. **Versão do n8n incompatível:** Verifique versão do n8n
2. **Node não existe:** Maestro usou node que não existe na sua versão
3. **JSON malformado:** Erro de sintaxe

**Solução:**
- Validar JSON antes de importar:
  ```python
  from maestro.tools_implementation import validate_workflow_json

  with open('workflow.json', 'r') as f:
      workflow = json.load(f)

  result = validate_workflow_json(workflow)
  print(result)
  ```

---

## 🗺️ Roadmap

### v1.0 (Atual)
- ✅ Radar diário de updates
- ✅ Base vetorial de conhecimento
- ✅ Maestro com 9 ferramentas
- ✅ Geração de blueprints e JSON

### v1.1 (Próxima)
- [ ] Interface web para o Maestro (Streamlit/Gradio)
- [ ] Auto-teste de workflows gerados
- [ ] Feedback loop (workflows que falharam alimentam o knowledge)
- [ ] Suporte a múltiplos LLMs (Anthropic Claude, Gemini)

### v1.2
- [ ] Marketplace de blueprints (compartilhar com comunidade)
- [ ] Versionamento de workflows (Git-like)
- [ ] CI/CD para workflows (deploy automático)
- [ ] Documentação automática de workflows existentes

### v2.0
- [ ] Maestro autônomo (cria, testa, corrige sem intervenção)
- [ ] Multi-agente (Maestro Arquiteto + Maestro Tester + Maestro Otimizador)
- [ ] Integração com n8n Cloud (API oficial)
- [ ] Analytics e insights de uso

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [n8n Docs](https://docs.n8n.io)
- [n8n Forum](https://community.n8n.io)
- [Supabase Docs](https://supabase.com/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)

### Comunidade
- [n8n Discord](https://discord.gg/n8n)
- [n8n Reddit](https://reddit.com/r/n8n)

### Ferramentas Úteis
- [n8n Workflow Viewer](https://n8n.io/workflows)
- [JSON Formatter](https://jsonformatter.org)
- [Supabase Studio](https://supabase.com/docs/guides/platform/studio)

---

## 🤝 Contribuindo

Este é um projeto open-source! Contribuições são bem-vindas:

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Áreas que precisam de ajuda:
- [ ] Testes automatizados
- [ ] Interface web para o Maestro
- [ ] Suporte a outras bases vetoriais (Pinecone, Weaviate)
- [ ] Tradução para outros idiomas
- [ ] Otimização de prompts do LLM

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 👏 Agradecimentos

- Time do n8n pela ferramenta incrível
- Comunidade n8n pelos padrões e best practices
- OpenAI pela API de embeddings e LLMs
- Supabase pelo backend simplificado

---

## 📧 Suporte

- **Issues:** [GitHub Issues](https://github.com/seu-repo/issues)
- **Discussões:** [GitHub Discussions](https://github.com/seu-repo/discussions)
- **Email:** seu-email@exemplo.com

---

**Feito com ❤️ para a comunidade n8n**

🎼 Maestro n8n - Workflows inteligentes, resilientes e à prova de futuro.
